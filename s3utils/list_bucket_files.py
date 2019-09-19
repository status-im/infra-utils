#!/usr/bin/env python3
import os
import boto3
import botocore

bucket_name = 'status-im'

s3 = boto3.resource(
    's3',
    region_name='ams3',
    endpoint_url='https://ams3.digitaloceanspaces.com',
    aws_access_key_id=os.environ['DO_ID'],
    aws_secret_access_key=os.environ['DO_SECRET']
)

bucket = s3.Bucket(bucket_name)

for obj in bucket.objects.all():
    if obj.key == 'index.html':
        continue
    print('{:<30}'.format(obj.key))
