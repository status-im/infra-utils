#!/usr/bin/env python
import os
import requests
from optparse import OptionParser
from datetime import datetime, timedelta, timezone

HELP_DESCRIPTION='Utility for deleting and banning spam accounts from Discourse.'
HELP_EXAMPLE='Example: ./add_to_private.py -o "waku-org" -u "devops"'

def parse_opts():
    parser = OptionParser(description=HELP_DESCRIPTION, epilog=HELP_EXAMPLE)
    parser.add_option('-U', '--url', default='https://discuss.status.app/',
                      help='URL of Discourse instance.')
    parser.add_option('-u', '--username', default='jakubgs',
                      help='Username of Discourse admin.')
    parser.add_option('-k', '--api-key', default=os.environ.get('DISCOURSE_API_KEY', False),
                      help='API key for Discourse instance.')
    parser.add_option('-n', '--hours-count', default=1,
                      help='Delete accounts created in the last N hours.')
    parser.add_option('-D', '--delete', default=False, action='store_true',
                      help='Actually delete users.')
    parser.add_option('-d', '--debug', default=False, action='store_true',
                      help='Print debug messages for GitHub calls.')

    (opts, args) = parser.parse_args()

    assert opts.api_key, parser.error('No Discourse API key!')

    return opts, args


class DiscourseAPI:

    def __init__(self, url, username, api_key):
        self.url = url
        self.session = requests.Session()
        self.session.headers.update({
            'Api-Key': api_key,
            'Api-Username': username,
            'Accept': 'application/json',
        })

    def list_new_users_page(self, page: int = 1):
        r = self.session.get(
            f'{self.url}/admin/users/list/new.json',
            params={'page': page, 'show_emails': True}
        )
        r.raise_for_status()
        return r.json()

    def list_new_users(self, start_page: int = 1, end_page: int = 10):
        page = start_page
        while page < end_page:
            for user in self.list_new_users_page(page):
                yield user
            page += 1

    def delete_user(self, user_id: int, delete_posts=True, block_email=True, block_urls=True, block_ip=True):
        url = f'{self.url}/admin/users/{user_id}.json'
        payload = {
            'delete_posts': delete_posts,
            'block_email': block_email,
            'block_urls': block_urls,
            'block_ip': block_ip,
        }
        r = self.session.delete(url, json=payload)
        r.raise_for_status()
        data = r.json()
        if not data['deleted']:
            raise Exception('Failed to delete user:'+data)
        return data


def main():
    (opts, args) = parse_opts()

    dapi = DiscourseAPI(opts.url, opts.username, opts.api_key)

    cutoff = datetime.now(timezone.utc) - timedelta(hours=opts.hours_count)
    deleted = []
    skipped = []

    for u in dapi.list_new_users():
        created_at = datetime.fromisoformat(u.get('created_at'))
        if created_at < cutoff:
            skipped.append((u, 'older_than_1h'))
            continue

        is_staff = any([
            u.get('admin'),
            u.get('moderator'),
            u.get('moderator'),
            u.get('trust_level') > 1,
        ])
        if is_staff:
            skipped.append((u, 'is_staff'))
            continue

        print('Deleting:', u['id'], u['username'], 'Posts:', u['post_count'])
        if opts.delete:
            dapi.delete_user(u['id'])
        deleted.append(u)

    if not opts.delete:
        print('WARNING: Dry run, nothing deleted!')
    print(f'Deleted users:', len(deleted))
    print(f'Skipped users.', len(skipped))


if __name__ == '__main__':
    main()
