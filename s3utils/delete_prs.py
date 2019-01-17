#!/usr/bin/env python3
import os
import boto3
import botocore
from datetime import datetime, timedelta, timezone

BUCKET = 'status-im-prs'
# remove builds older than 30 days
CUTOFF = 30

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

threshold = datetime.now(timezone.utc) - timedelta(days=CUTOFF)

for f in s3.list_objects_v2(Bucket=BUCKET, MaxKeys=9999)['Contents']:
    name = f['Key']
    modified = f['LastModified']
    if name == 'index.html':
        continue
    if modified > threshold:
        continue
    print('DELETING: {}:{}'.format(BUCKET, name))
    s3.delete_object(Bucket=BUCKET, Key=name)
