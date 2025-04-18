# FloTorch Installation guide

Welcome to FloTorch! This guide will help you set up FloTorch's infrastructure on AWS.

## Prerequisites

1. **AWS Account and IAM User** with these permissions:
   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Action": [
                   "cloudformation:*", "s3:*", "ec2:*", "iam:*", "lambda:*",
                   "dynamodb:*", "events:*", "sagemaker:*", "opensearch:*",
                   "ecr:*", "apprunner:*", "cloudwatch:*", "logs:*",
                   "ssm:*", "es:*", "bedrock:*", "sts:*", "kms:*",
                   "secretsmanager:*", "ecs:*", "states:*",
                   "elasticloadbalancing:*", "application-autoscaling:*",
                   "acm:*", "sns:*", "vpc-lattice:*"
               ],
               "Resource": "*"
           }
       ]
   }
   ```
2. **AWS CLI** installed and configured on your computer
3. **Required AWS Service Quotas**:
   - VPC, Lambda, EventBridge, SageMaker, OpenSearch
   - DynamoDB, ECR, AppRunner

4. **Bedrock Model Access** - Enable these models in your AWS account:
   - **Embedding**: Amazon Titan Embed (text/image), Cohere Embed
   - **Retrieval**: Amazon Titan/Nova, Claude, Cohere Command, Llama, Mistral
## Installation Steps

### 1. Subscribe to FloTorch on AWS Marketplace

1. Visit the [FloTorch AWS Marketplace page](https://aws.amazon.com/marketplace/pp/prodview-z5zcvloh7l3ky?ref_=aws-mp-console-subscription-detail-payg)
2. Click "View Purchase options"
3. Click "Continue to Configuration" after subscribing
4. Select your preferred fulfillment option and software version

### 2. Deploy Using CloudFormation

Click this link to launch the stack: [Install FloTorch (US East 1)](https://us-east-1.console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create?stackName=flotorch-stack&templateURL=https://flotorch-public.s3.us-east-1.amazonaws.com/latest/templates/master-template.yaml)

Complete the required parameters:

| Parameter | Example | Description |
|-----------|---------|-------------|
| PrerequisitesMet | "yes" | Confirm prerequisites completion |
| NeedOpensearch | "yes" | Whether to deploy OpenSearch cluster |
| ProjectName | "flotorch" | Name for your stack and resources |
| TableSuffix | "abctry" | 6 lowercase letters for unique resources |
| ClientName | "acmecorp" | Your organization name (lowercase) |
| OpenSearchAdminUser | "admin" | Admin username for OpenSearch |
| OpenSearchAdminPassword | "YourSecurePass123!" | Secure password (12-41 chars) |
| NginxAuthPassword | "YourNginxPass123!" | Secure password (12-41 chars) |

### 3. Configure DNS for Application Access

After deployment completes, get the EC2 instance's public IP:

```bash
aws cloudformation describe-stacks \
  --stack-name YOUR_PROJECT_NAME-KubernetesSetupStack \
  --query "Stacks[0].Outputs[?OutputKey=='InstancePublicIp'].OutputValue" \
  --output text
```

Map the FloTorch domain to this IP in your hosts file:

- **Linux users**:
  ```bash
  echo "<EC2_PUBLIC_IP> console.flotorch.com" | sudo tee -a /etc/resolv.conf
  ```

- **macOS users**:
  ```bash
  sudo vi /private/etc/hosts
  # Add: <EC2_PUBLIC_IP> console.flotorch.com
  sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder
  ```

### 4. Access Your FloTorch Console

Once DNS is configured, access your FloTorch console at:
- https://console.flotorch.com

Log in with the credentials you specified in the CloudFormation parameters.

## What's New

- **Security Improvements**: IMDSv2 tokens and SSM parameters for secure metadata access
- **Kubernetes Setup**: 
  - Nginx Ingress Controller with automatic cleanup and NodePort configuration
  - FloTorch Helm chart with properly formatted values for dynamic credentials
  - Ingress controller readiness verification before deployment
- **Infrastructure**: 
  - Split EC2 stacks for with/without OpenSearch deployments
  - Console image updated to tag 178
  - Added new PostgreSQL migration scripts

## Monitoring & Management

### Deployment Status

Monitor your CloudFormation deployment progress:
```bash
aws cloudformation describe-stack-events --stack-name YOUR_PROJECT_NAME
```

## Post-Installation

After successful deployment, you'll have access to:

1. **FloTorch Console**: https://console.flotorch.com
2. **AppRunner Service**: For API requests (URL in CloudFormation outputs)
3. **OpenSearch Dashboard**: For data exploration (if enabled)

### Performance Monitoring

Monitor your FloTorch deployment using AWS services:

| AWS Service | Monitoring Capabilities |
|------------|--------------------------|
| CloudWatch | • Lambda execution metrics<br>• SageMaker endpoint usage<br>• AppRunner performance<br>• Application logs |
| CloudFormation | • Stack events<br>• Resource status |
| OpenSearch | • Query performance<br>• Cluster health |

Access CloudWatch dashboards from the AWS console to view performance metrics and logs.

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
