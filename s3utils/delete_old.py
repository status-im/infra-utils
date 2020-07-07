#!/usr/bin/env python3
import os
import boto3
import botocore
from optparse import OptionParser
from datetime import datetime, timedelta, timezone

HELP_DESCRIPTION='This script removes files older than set number of days from s3 bucket.'
HELP_EXAMPLE='Example: ./delete_old.py -b status-im -o 90'

def parse_opts():
    parser = OptionParser(description=HELP_DESCRIPTION, epilog=HELP_EXAMPLE)
    parser.add_option('-e', '--endpoint', default='https://ams3.digitaloceanspaces.com',
                      help='Endpoint URL for the s3 bucket.')
    parser.add_option('-b', '--bucket', default='status-im-prs',
                      help='Name of the s3 bucket.')
    parser.add_option('-r', '--region', default='ams3',
                      help='Name of s3 bucket region.')
    parser.add_option('-o', '--older-than', type='int', default=30,
                      help='Max age of files to leave in bucket.')
    parser.add_option('-d', '--dry-run', action='store_true',
                      help='Only print files that will be deleted.')
    (opts, args) = parser.parse_args()

    return (opts, args)

def main():
    (opts, args) = parse_opts()

    if opts.dry_run:
        print('DRY-RUN!')

    session = boto3.session.Session()
    s3 = session.client('s3',
        region_name=opts.region,
        endpoint_url=opts.endpoint,
        aws_access_key_id=os.environ['DO_ID'],
        aws_secret_access_key=os.environ['DO_SECRET']
    )

    threshold = datetime.now(timezone.utc) - timedelta(days=opts.older_than)

    for f in s3.list_objects_v2(Bucket=opts.bucket, MaxKeys=9999)['Contents']:
        name = f['Key']
        modified = f['LastModified']
        if name == 'index.html':
            continue
        if modified > threshold:
            continue
        print('DELETING: {}:{}'.format(opts.bucket, name))
        if not opts.dry_run:
            s3.delete_object(Bucket=opts.bucket, Key=name)


if __name__ == '__main__':
    main()
