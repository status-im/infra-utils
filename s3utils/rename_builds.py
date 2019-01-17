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

for f in s3.list_objects_v2(Bucket=BUCKET)['Contents']:
    name = f['Key']
    when = f['LastModified']
    if name.startswith('StatusIm-') or name == 'index.html':
        continue
    # exception for last dot before file extension
    dots = name.count('.')
    new_name = name.replace('.', '-', dots-1)
    print('{:<30} -> {}'.format(name, new_name))
    # WARNING: This does not copy ACL rules!
    s3.copy({'Bucket': BUCKET, 'Key': name}, BUCKET, new_name)
    s3.delete_object(Bucket=BUCKET, Key=name)
