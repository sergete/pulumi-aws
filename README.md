# pulumi-aws
This project defines the infrastructure using Pulumi and AWS. 
Below is a description of the deployed architecture.

---

## Architecture description

### S3 Bucket  
An Amazon S3 bucket named `xfarm-bucket-01` is created with `force_destroy` enabled, allowing it to be deleted even if it contains objects. It is used to store files that trigger events.

### SQS Queues  
Two SQS queues are defined: a main queue (`xFarmMainQueue`) and a Dead Letter Queue (`xFarmDeadLetterSqs`) for messages that fail processing after 5 attempts. The main queue includes a redrive policy to route messages to the DLQ.

### S3 Notifications  
The S3 bucket is configured to send notifications to the SQS queue when objects are created under the `inputs/` prefix. This enables automatic triggering of downstream processes.

### SQS Queue Policy  
A policy is defined to allow the S3 service to send messages to the SQS queue. It ensures that only the specified bucket has permission to send events to the queue.

### Lambda Function  
An AWS Lambda function using Python 3.12 is created and triggered by the SQS queue. It is packaged into a `.zip` file generated from the local directory (`lambda_code/lambda_function.py`).

### Lambda Role & Permissions  
The Lambda function uses a role with permissions to execute, access S3, and process SQS messages. Two managed AWS policies are attached: one for basic Lambda execution and another for full S3 access.

### Event Source Mapping  
The Lambda function is directly linked to the SQS queue through an `EventSourceMapping`, allowing it to automatically process messages from the queue.

---

