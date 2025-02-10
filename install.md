# FloTorch Installation guide


Welcome to FloTorch! This guide will help you set up FloTorch's infrastructure on AWS. We will guide you through the steps.

## Before You Begin (Prerequisites)

### 1. AWS Account and Tools

1. AWS Account and a user with the following permissions in AWS

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "cloudformation:*",
                "s3:*",
                "ec2:*",
                "iam:*",
                "lambda:*",
                "dynamodb:*",
                "events:*",
                "sagemaker:*",
                "opensearch:*",
                "ecr:*",
                "apprunner:*",
                "cloudwatch:*",
                "logs:*",
                "ssm:*",
                "es:*",
                "bedrock:*",
                "sts:*",
                "kms:*",
                "secretsmanager:*",
                "ecs:*",
                "states:*",
                "elasticloadbalancing:*",
                "application-autoscaling:*",
                "acm:*",
                "sns:*",
                "vpc-lattice:*"
            ],
            "Resource": "*"
        }
    ]
   }
   ```
2. AWS CLI installed and configured on your computer
3. AWS Marketplace Subscription (see next section)

### 2. AWS Marketplace Subscription ‼️
Before starting the installation, subscribe to FloTorch:

1. Visit the [FloTorch AWS Marketplace page](https://aws.amazon.com/marketplace/pp/prodview-z5zcvloh7l3ky?ref_=aws-mp-console-subscription-detail-payg)
2. Click on the "View Purchase options" button
3. After subscribing, click on 'Continue to Configuration'
4. Select your preferred fulfillment option and Software Version

### 3. Required AWS Service Quotas

| Service | Resource Type |
|---------|--------------|
| VPC | Networking resources |
| Lambda | Functions |
| EventBridge | Rules |
| SageMaker | Endpoints |
| OpenSearch | Domains |
| DynamoDB | Tables |
| ECR | Repositories |
| AppRunner | Services |

### 4. Required Bedrock Model Access

| Purpose | Model Name |
|---------|------------|
| **Embedding** | Amazon/amazon.titan-embed-text-v2:0 |
| | Amazon/amazon.titan-embed-image-v1 |
| | Cohere/cohere.embed-english-v3 |
| | Cohere/cohere.embed-multilingual-v3 |
| **Retrieval** | Amazon/amazon.titan-text-lite-v1 |
| | Amazon/amazon.titan-text-express-v1 |
| | Amazon/amazon.nova-lite-v1:0 |
| | Amazon/amazon.nova-micro-v1:0 |
| | Amazon/amazon.nova-pro-v1:0 |
| | Anthropic/anthropic.claude-3-5-sonnet-20241022-v2:0 |
| | Anthropic/anthropic.claude-3-5-sonnet-20240620-v1:0 |
| | Cohere/cohere.command-r-plus-v1:0 |
| | Cohere/cohere.command-r-v1:0 |
| | Meta/meta.llama3-2-1b-instruct-v1:0 |
| | Meta/meta.llama3-2-3b-instruct-v1:0 |
| | Meta/meta.llama3-2-11b-instruct-v1:0 |
| | Meta/meta.llama3-2-90b-instruct-v1:0 |
| | Mistral AI/mistral.mistral-7b-instruct-v0:2 |
| | Mistral AI/mistral.mistral-large-2402-v1:0 |

## Installation Guide

## Required Parameters that to be met in both approaches.

| Parameter | Example | Requirements |
|-----------|----------|--------------|
| PrerequisitesMet | "yes" | Set this to 'yes' only after completing above steps. |
| ProjectName | "flotorch" | Your project name |
| TableSuffix | "abctry" | 6 lowercase characters only alphabets allowed |
| ClientName | "acmecorp" | Must be lowercase |
| OpenSearchAdminUser | "admin" | Admin username |
| OpenSearchAdminPassword | "YourSecurePassword123!" | 12-41 chars with letters, numbers, symbols |
| NginxAuthPassword | "YourNginxPassword123!" | 12-41 chars with letters, numbers, symbols |

### Approach #1: Using AWS Cloudformation Template (<mark> Ensure the above Parameter conditions are met </mark>).

Click this link: [Install FloTorch (US East 1)](https://us-east-1.console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create?stackName=flotorch-stack&templateURL=https://flotorch-public.s3.us-east-1.amazonaws.com/2.0.2/templates/master-template.yaml)

### Approach #2: AWS Command Line Installation (<mark> Ensure the above Parameter conditions are met </mark>).

```bash
aws cloudformation create-stack \
    --stack-name flotorch-stack \
    --template-url https://flotorch-public.s3.us-east-1.amazonaws.com/templates/master-template.yaml \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
    --parameters \
        ParameterKey=PrerequisitesMet,ParameterValue=yes \
        ParameterKey=ProjectName,ParameterValue=your-project-name \
        ParameterKey=TableSuffix,ParameterValue=unique-suffix \
        ParameterKey=ClientName,ParameterValue=your-client-name \
        ParameterKey=OpenSearchAdminUser,ParameterValue=admin \
        ParameterKey=OpenSearchAdminPassword,ParameterValue=YourSecurePassword123! \
        ParameterKey=NginxAuthPassword,ParameterValue=YourNginxPassword123!
```

## Monitor your setup

| AWS Service | You can view |
|-----------|----------------|
| CloudWatch Metrics | • Lambda execution<br>• SageMaker endpoint usage<br>• AppRunner service metrics |
| CloudWatch Logs | • Lambda function logs<br>• AppRunner application logs<br>• OpenSearch logs |

## Cost Overview

| Service | Daily Cost Range (Approx) | Details |
|---------|-----------------|----------|
| Lambda Functions | $0.50-$2.00 | • Free tier: 1M requests/month<br>• 400,000 GB-seconds included |
| SageMaker Endpoints | $1.40-$2.80 | • ml.t3.medium instances<br>• 1-2 endpoints running |
| OpenSearch | $41.81 | • r7g.2xlarge: $0.5184/hour<br>• IOPS (16000): $1.152/hour<br>• Throughput: $0.072/hour |
| DynamoDB | $2-$5 | • Write: $1.25/million<br>• Read: $0.25/million<br>• Storage: $0.25/GB/month |
| AppRunner | $1.54-$3.08 | • 1 vCPU, 2GB memory: $0.064/hour<br>• 1-2 instances |
| ECR | $0.20-$0.50 | • Storage: $0.10/GB/month<br>• Transfer: $0.09/GB |
| VPC and Networking | $1.08-$2.00 | • NAT Gateway: $0.045/hour<br>• Processing: $0.045/GB |
| CloudWatch | $0.50-$1.50 | • Log ingestion: $0.30/GB<br>• Metrics: $0.01/1,000 requests |
| Step Functions | $0.50-$2.00 | • $0.025/1,000 state transitions |
| ECS (Fargate) | $2.00-$5.00 | • vCPU: $0.04048/hour<br>• Memory: $0.004445/GB-hour |
| Bedrock | $5.00-$10.00 | • Input: $0.0001/1K tokens<br>• Output: $0.0002/1K tokens |

**Total Estimated Cost (Approx)**: $56.53-$75.69/day (varies with usage)

## Security Features

| Feature | Description |
|---------|-------------|
| VPC Isolation | Private network infrastructure |
| IAM Permissions | Role-based access control |
| Security Groups | Network access control |
| Authentication | NGINX basic auth |
| Access Control | OpenSearch Security |

## Getting Help 

| Method | Contact |
|--------|---------|
| Email | [info@flotorch.ai](mailto:info@flotorch.ai) |
| Issues | [FloTorch GitHub Issues](https://github.com/FissionAI/FloTorch/issues) |
