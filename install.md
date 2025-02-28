# FloTorch Installation guide


Welcome to FloTorch! This guide will help you set up FloTorch's infrastructure on AWS. There are two approaches for setting up and we will guide you through the steps.

Irrespective of the approach, below are the pre-requisites:


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


### 2. Required AWS Service Quotas

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

### 3. Required Bedrock Model Access

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

## Required Parameters to be met in both approaches.

| Parameter | Example | Requirements |
|-----------|----------|--------------|
| PrerequisitesMet | "yes" | Set this to 'yes' only after completing above steps. |
| ProjectName | "flotorch" | Your project name |
| TableSuffix | "abctry" | 6 lowercase characters only alphabets allowed |
| ClientName | "acmecorp" | Must be lowercase |
| OpenSearchAdminUser | "admin" | Admin username |
| OpenSearchAdminPassword | "YourSecurePassword123!" | 12-41 chars with letters, numbers, specialchars |
| NginxAuthPassword | "YourNginxPassword123!" | 12-41 chars with letters, numbers, specialchars |

### Approach #1: AWS Cloudformation Template 

Before starting the installation, please subscribe to FloTorch:

1. Visit the [FloTorch AWS Marketplace page](https://aws.amazon.com/marketplace/pp/prodview-z5zcvloh7l3ky?ref_=aws-mp-console-subscription-detail-payg)
2. Click on the "View Purchase options" button
3. After subscribing, click on 'Continue to Configuration'
4. Select your preferred fulfillment option and Software Version


Post subscribing, please click this link: [Install FloTorch (US East 1)](https://us-east-1.console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create?stackName=flotorch-stack&templateURL=https://flotorch-public.s3.us-east-1.amazonaws.com/2.1.0/templates/master-template.yaml)

### Approach #2: Command Line Installation

Please ensure the following pre-requisites are met:

1. Python 3.9+
2. AWS CLI configured
3. docker installed and running

## Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/FissionAI/FloTorch.git
cd FloTorch
```

2. Make the provision script executable:
```bash
chmod +x provision.sh
```

3. Run the provision script:
```bash
./provision.sh
```

## Configuration Steps

The script will prompt you for the following information:

### 1. AWS Region
- Choose AWS regions (us-east-1, us-west-2)
- Default: `us-east-1`

```bash
Enter AWS region [us-east-1]:
```
### 2. AWS Marketplace Subscription
- Answer `no` if you haven't subscribed to FloTorch on AWS Marketplace yet
- Answer `yes` if you have an active subscription

```bash
Subscribed to FloTorch on AWS Marketplace? (yes/no) [no]:
```

### 3. Stack Parameters
- This will be used as your CloudFormation stack name. Must be unique within your AWS account
- Example: `MyProject` or `FloTorch-Dev`

```bash
Enter project name [FloTorch]:
```

```bash
Enter Table suffix (exactly 6 lowercase letters) [fltdev]:
```
- Used to create resources with unique suffix
- Example: `asdfgh`, `qwerty`, `uiojkl` etc

```bash
Enter client/organization name [FloTorch]:
```
- Your organization or team name
- Used for resource tagging

### 4. OpenSearch is needed for FloTorch indexing. Skip if using Amazon Knowledge Bases or leverage Foundational Model data for inferencing (no KB dataset).
- `yes`: Deploys with OpenSearch integration
- `no`: Deploys without OpenSearch
```bash
Do you need OpenSearch? (yes/no) [yes]:

# The details below will be asked if OpenSearch has been chosen.

Enter OpenSearch admin username [admin]:
Enter OpenSearch admin password (12-41 chars with letters, numbers, specialchars):

```
  
### 5. FloTorch App login
- Choose strong passwords
- Store these securely as you'll need them to access services

```bash
Enter NGINX password (12-41 chars with letters, numbers, specialchars):
```

## Deployment

The script will:
1. Create a CloudFormation stack with your project name
2. Build Docker Images in your local and pushes to ECR, if there is no marketplace subscription.
3. Deploy all necessary resources
4. Output the API Gateway URL when complete

To monitor the deployment:
```bash
aws cloudformation describe-stack-events --stack-name YOUR_PROJECT_NAME
```

## Post-Installation

After successful deployment, you'll receive:
1. API Gateway URL for making requests
2. OpenSearch endpoint (if enabled)
3. Monitoring dashboard URL

Store these URLs securely for future use.

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

## Troubleshooting

### Common Issues

1. Stack Creation Failed
   - Check CloudFormation events in AWS Console
   - Verify your AWS CLI has sufficient permissions

2. Resource Limits
   - Ensure your AWS account has sufficient service quotas
   - Request limit increases if needed

3. Issues for AWS Marketplace Subscription Users
   - Verify your subscription status in AWS Marketplace
   - Ensure your subscription is active and properly configured

## Cleanup

To remove all deployed resources:
```bash
aws cloudformation delete-stack --stack-name YOUR_PROJECT_NAME
```

## Getting Help 

| Method | Contact |
|--------|---------|
| Email | [info@flotorch.ai](mailto:info@flotorch.ai) |
| Issues | [FloTorch GitHub Issues](https://github.com/FissionAI/FloTorch/issues) |
