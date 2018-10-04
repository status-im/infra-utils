#!/usr/bin/env python3
import os
import boto3
import botocore

SRC_BUCKET = 'status-im'
DST_BUCKET = 'status-im-prs'

session = boto3.session.Session()
s3 = session.client('s3',
                    region_name='ams3',
                    endpoint_url='https://ams3.digitaloceanspaces.com',
                    aws_access_key_id=os.environ['DO_ID'],
                    aws_secret_access_key=os.environ['DO_SECRET'])

for f in s3.list_objects_v2(Bucket=SRC_BUCKET)['Contents']:
    name = f['Key']
    when = f['LastModified']
    new_name = 'StatusIm.{}.{}.nightly.{}'.format(
        when.strftime('%y%m%d.%H%M%S'),
        name[9:15],
        name.split('.')[-1]
    )
    print('{:<25} -> {}'.format(name, new_name))
    path = '/tmp/{}'.format(new_name)
    s3.download_file(SRC_BUCKET, name, path)
    s3.upload_file(path, DST_BUCKET, new_name)
