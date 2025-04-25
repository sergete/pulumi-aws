"""A Python Pulumi program"""

import json
import pulumi
import pulumi_aws as aws
import shutil

# Bucket S3
bucket = aws.s3.BucketV2(
    resource_name="bucket",
    bucket="xfarm-bucket-01",
    force_destroy=True
)

# Main Queue
main_queue = aws.sqs.Queue(
    resource_name="main_queue",
    name="xFarmMainQueue",
    message_retention_seconds=345600, # 4 days
    receive_wait_time_seconds=10
)

# Dead Letter SQS
dead_letter_sqs = aws.sqs.Queue(
    resource_name="dead_letter_sqs",
    name="xFarmDeadLetterSqs",
    message_retention_seconds=1209600 , # 14 days
    redrive_allow_policy=pulumi.Output.json_dumps({
        "redrivePermission": "byQueue",
        "sourceQueueArns": [main_queue.arn],
    }),
    opts=pulumi.ResourceOptions(depends_on=main_queue)
)

# Main Queue Redrive
main_queue_redrive_policy = aws.sqs.RedrivePolicy(
    resource_name="main_queue",
    queue_url=main_queue.id,
    redrive_policy=pulumi.Output.json_dumps({
        "deadLetterTargetArn": dead_letter_sqs.arn,
        "maxReceiveCount": 5,
    }))

# Main Queue Policy
queue_policy = aws.sqs.QueuePolicy(
    resource_name="main_queue_policy",
    queue_url=main_queue.url,
    policy=pulumi.Output.all(main_queue.arn, bucket.arn).apply(lambda args: {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {
                "Service": "s3.amazonaws.com"
            },
            "Action": "sqs:SendMessage",
            "Resource": args[0],
            "Condition": {
                "ArnLike": {
                    "aws:SourceArn": args[1]
                },
            }
        }]
    })
)

# S3 notifications
notification = aws.s3.BucketNotification(
    resource_name="bucket_notification",
    bucket=bucket.id,
    queues=[{
        "queue_arn": main_queue.arn,
        "events": ["s3:ObjectCreated:*"],
        "filter_prefix": "inputs/",
    }],
    opts=pulumi.ResourceOptions(depends_on=queue_policy)
)

# Lambda Role
lambda_role = aws.iam.Role(
    resource_name="lambda_role",
    name="xFarmLambdaRole",
    assume_role_policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }]
    })
)

# Attach existing policies
lambda_policies = {
    "xFarmLambdaBasicExec": "arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole",
    "xFarmLambdaS3Full": "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

for name, policy_arn in lambda_policies.items():
    aws.iam.RolePolicyAttachment(
        name,
        role=lambda_role.name,
        policy_arn=policy_arn
    )

# Create lambda zip file
shutil.make_archive("lambda_function", "zip", "./lambda_code/", "lambda_function.py")

# Create lambda function
lambda_func = aws.lambda_.Function(
    resource_name="lambda_function",
    name="xFarmLambdaFunction",
    runtime=aws.lambda_.Runtime.PYTHON3D12,
    handler="lambda_function.handler",
    code=pulumi.FileArchive("lambda_function.zip"),
    role=lambda_role.arn,
    environment=aws.lambda_.FunctionEnvironmentArgs(
        variables={
            "BUCKET_NAME": bucket.id
        }
    ),
)

event_source_mapping = aws.lambda_.EventSourceMapping(
    resource_name="event_source_mapping",
    event_source_arn=main_queue.arn,
    function_name=lambda_func.name
)


# Exports
pulumi.export('bucket_name', bucket.id)
pulumi.export('SQS name', main_queue.name)
pulumi.export('lambda_name', lambda_func.name)

