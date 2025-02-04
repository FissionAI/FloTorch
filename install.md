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

### 2. AWS Marketplace Subscription
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


## What You're Installing

### Core Infrastructure Components

| Component | Purpose |
|-----------|----------|
| VPC Stack | Private network infrastructure |
| VPC Endpoint Stack | Secure access to AWS services within VPC |
| DynamoDB Stack | Database tables and S3 bucket for data storage |
| OpenSearch Stack | Search functionality |
| ECR Repository Stack | Container image repositories |
| ECS Stack | Running containerized applications |
| Lambda Stack | Serverless functions |
| State Machine Stack | Step Functions for orchestration |
| AppRunner Stack | Application hosting and management |


## Installation Guide

### Option 1: Quick Install Parameters

| Parameter | Example | Requirements |
|-----------|----------|--------------|
| ProjectName | "flotorch" | Your project name |
| TableSuffix | "abc123" | 6 lowercase characters |
| ClientName | "acmecorp" | Must be lowercase |
| OpenSearchAdminUser | "admin" | Admin username |
| OpenSearchAdminPassword | "YourSecurePassword123!" | 8-41 chars with letters, numbers, symbols |
| NginxAuthPassword | "YourNginxPassword123!" | 8-41 chars with letters, numbers, symbols |

### Option 2: Command Line Installation

## What You're Installing

FloTorch creates a comprehensive architecture for managing and deploying machine learning models, combining serverless components with managed services like OpenSearch. Here's what you get:

### Core Infrastructure Components

- **VPC Stack**: Your private network infrastructure
- **VPC Endpoint Stack**: Secure access to AWS services within the VPC
- **DynamoDB Stack**: Database tables and S3 bucket for data storage
- **OpenSearch Stack**: Search functionality
- **ECR Repository Stack**: Container image repositories
- **ECS Stack**: Elastic Container Service for running containerized applications
- **Lambda Stack**: Serverless functions for various operations
- **State Machine Stack**: Step Functions for orchestration
- **AppRunner Stack**: Application hosting and management

### Key Features

1. Automated deployment and management
2. Serverless architecture for cost optimization
3. Secure VPC configuration
4. Integrated monitoring and logging
5. Automated container image management

## Installation Guide

### Option 1: Quick Install (Recommended for Beginners)

1. Click this link: [Install FloTorch (US East 1)](https://us-east-1.console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create?stackName=flotorch-stack&templateURL=https://flotorch-public.s3.us-east-1.amazonaws.com/2.0.1/templates/master-template.yaml)

2. Fill in these details in the CloudFormation console:
   - **ProjectName**: your-project-name
     (Example: "flotorch")
   - **TableSuffix**: unique-suffix
     (Example: "abc123" - must be 6 lowercase characters)
   - **ClientName**: your-client-name
     (Example: "acmecorp" - must be lowercase)
   - **OpenSearchAdminUser**: admin
     (Example: "admin")
   - **OpenSearchAdminPassword**: YourSecurePassword123!
     (Must be 8-41 characters with letters, numbers, and symbols)
   - **NginxAuthPassword**: YourNginxPassword123!
     (Must be 8-41 characters with letters, numbers, and symbols)

3. Click "Review and create" and acknowledge that the stack will create IAM resources

### Option 2: Command Line Installation

For advanced users, you can deploy using the AWS CLI:

```bash
aws cloudformation create-stack \
    --stack-name flotorch-stack \
    --template-url https://flotorch-public.s3.us-east-1.amazonaws.com/templates/master-template.yaml \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
    --parameters \
        ParameterKey=ProjectName,ParameterValue=your-project-name \
        ParameterKey=TableSuffix,ParameterValue=unique-suffix \
        ParameterKey=ClientName,ParameterValue=your-client-name \
        ParameterKey=OpenSearchAdminUser,ParameterValue=admin \
        ParameterKey=OpenSearchAdminPassword,ParameterValue=YourSecurePassword123! \
        ParameterKey=NginxAuthPassword,ParameterValue=YourNginxPassword123!
```

## Cost Overview

| Service | Daily Cost Range | Details |
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

**Total Estimated Cost**: $56.53-$75.69/day (varies with usage)

## Monitoring Your Installation

| Component | What to Monitor |
|-----------|----------------|
| CloudWatch Metrics | • Lambda execution<br>• SageMaker endpoint usage<br>• AppRunner service metrics |
| Logs | • Lambda function logs<br>• AppRunner application logs<br>• OpenSearch logs |
| Alerts | • Cost thresholds<br>• Error rates<br>• Service health |

## Security Features

| Feature | Description |
|---------|-------------|
| VPC Isolation | Private network infrastructure |
| IAM Access | Role-based access control |
| Encryption | Data encryption at rest |
| Security Groups | Network access control |
| Authentication | NGINX basic auth |
| Access Control | OpenSearch security |

## Troubleshooting Guide

| Issue Type | Resolution Steps |
|------------|-----------------|
| Installation Issues | 1. Check CloudFormation events<br>2. Verify IAM permissions<br>3. Validate parameter values |
| Runtime Problems | 1. Check CloudWatch logs<br>2. Verify network connectivity<br>3. Check service quotas |

## Getting Help

| Method | Contact |
|--------|---------|
| Logs | Check CloudWatch |
| Stack Events | Review in Console |
| DevOps Team | Contact support |
| Email | info@flotorch.ai |

