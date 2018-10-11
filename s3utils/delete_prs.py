#!/usr/bin/env python3
import os
import boto3
import botocore

BUCKET = 'status-im'

session = boto3.session.Session()
s3 = session.client('s3',
                    region_name='ams3',
                    endpoint_url='https://ams3.digitaloceanspaces.com',
                    aws_access_key_id=os.environ['DO_ID'],
                    aws_secret_access_key=os.environ['DO_SECRET'])

def exists(name):
    try:
        s3.get_object(Bucket=BUCKET, Key=name)
    except s3.exceptions.NoSuchKey:
        return False
    return True

for f in s3.list_objects_v2(Bucket=BUCKET, MaxKeys=9999)['Contents']:
    name = f['Key']
    build_type = name.split('-')[-1].split('.')[0]
    if build_type == 'e2e':
        # if an e2e build has a release or a nightly it's not a PR
        not_pr = any([
          exists(name.replace('e2e', 'release')),
          exists(name.replace('e2e', 'nightly'))
        ])
        if not_pr:
            continue
    elif build_type != 'pr':
        continue
    print('DELETING: {}:{}'.format(BUCKET, name))
    s3.delete_object(Bucket=BUCKET, Key=name)
