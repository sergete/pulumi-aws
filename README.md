# pulumi-aws
This project defines the infrastructure using Pulumi and AWS. 
Below is a description of the deployed architecture.

## Architecture design

![Architecture](/repo_images/architecture.png)

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

## Deployment instructions

The deployment is managed through a GitHub Actions workflow using Pulumi. It is triggered manually via the GitHub UI using `workflow_dispatch`.

### Required repository secrets

To allow the GitHub Actions workflow to deploy the infrastructure, the following repository secrets must be configured:

- `AWS_ACCESS_KEY_ID` – Access key ID for your AWS IAM user or role.
- `AWS_SECRET_ACCESS_KEY` – Secret access key for your AWS IAM user or role.
- `AWS_REGION` – AWS region to deploy the infrastructure (e.g., `eu-west-1`).
- `AWS_ASSUME_ROLE` – ARN of the IAM role to assume during the deployment process.

### Workflow inputs

When triggering the workflow manually, you must provide the following inputs:

- `command` – Action to perform. Available options:
  - `preview` (default): Shows a preview of the changes Pulumi would apply.
  - `run`: Applies the infrastructure changes.
  - `delete`: Destroys the deployed resources.

- `stackName` – Name of the Pulumi stack to use. Currently supported:
  - `dev`

The workflow handles installation, authentication, configuration, and execution of Pulumi commands according to the selected action.

---

## Technical Decisions

Altough technical challenge task description talks about creating S3 events to execute Lambda functions i decided that it wasn´t the best choice for this type of solution.
i am searching for something that can give us more than an lambda execution, for realtime data we need something **robust**, 
that provide **fault tolerance** and ensure **retry attempts**.





