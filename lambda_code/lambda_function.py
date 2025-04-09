import boto3
import os
import json

s3 = boto3.client('s3')
BUCKET = os.getenv('BUCKET_NAME', None)

def handler(event, context):
    global BUCKET
    for record in event['Records']:
        # retrieve body message
        body = json.loads(record['Body'])
        s3_event = json.loads(body['Message'])
        for record in s3_event['Records']:
            if not BUCKET:
                BUCKET = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            processed_key = key.replace('inputs/', 'processed/')
            s3.copy_object(
                Bucket=BUCKET,
                Key=processed_key,
                CopySource={
                    'Bucket': BUCKET, 'Key': key
                }
            )
            s3.delete_object(Bucket=BUCKET, Key=key)
