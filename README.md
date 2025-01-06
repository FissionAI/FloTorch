# What is FloTorch.ai?

FloTorch.ai is an innovative product poised to transform the field of Generative AI by simplifying and optimizing the
decision-making process for leveraging Large Language Models (LLMs) in Retrieval Augmented Generation (RAG) systems. In
today’s fast-paced digital landscape, selecting the right LLM setup is critical for achieving efficiency, accuracy, and
cost-effectiveness. However, this process often involves extensive trial-and-error, significant resource expenditure,
and complex comparisons of performance metrics. Our solution addresses these challenges with a streamlined,
user-friendly approach.

## Demo

[![FloTorch.ai Demo](./cover-image.png?raw=true)](https://fissiontorch-public.s3.us-east-1.amazonaws.com/demo.mp4)

## Key Features

- **Automated Evaluation of LLMs**: FloTorch.ai evaluates multiple LLMs by analyzing combinations of hyperparameters
  defined by the end user.
- **Performance Metrics**: Produces detailed performance scores, including relevance, fluency, and robustness.
- **Cost and Time Insights**: Provides actionable insights into the pricing and execution times for each LLM
  configuration.
- **Data-Driven Decision-Making**: Empowers users to align LLM configurations with specific goals and budget
  constraints.

## Who Benefits from FloTorch.ai?

FloTorch.ai caters to a broad spectrum of users, including:

- **Startups**: Optimize AI-driven systems for rapid growth.
- **Data Scientists**: Simplify model selection and evaluation.
- **Developers**: Focus on deployment and innovation rather than experimentation.
- **Researchers**: Gain insights into LLM performance metrics effortlessly.
- **Enterprises**: Enhance customer experiences, improve content generation, and refine data retrieval processes.

## Why Choose FloTorch.ai?

- **Eliminates Complexity**: No more manual evaluations or tedious trial-and-error processes.
- **Accelerates Selection**: Streamlines the evaluation and decision-making process.
- **Maximizes Efficiency**: Ensures users achieve the best performance from their chosen LLMs.
- **Focus on Innovation**: Allows users to dedicate resources to innovation and deployment rather than experimentation.

## Vision

By combining advanced evaluation capabilities with a focus on cost and time efficiency, FloTorch.ai provides a holistic
solution for navigating the evolving RAG landscape. It empowers users to focus on innovation and deployment, setting a
new standard for intelligent decision-making in AI-driven applications.

With FloTorch.ai, we aim to be a pivotal enabler of progress in the generative AI ecosystem, helping our users achieve
excellence in their projects.

# FloTorch Installation Guide

## Overview

The CDK directory under the main directory in the FloTorch directory structure defines the AWS infrastructure creation
for the FloTorch application using AWS CDK in Python. The infrastructure is designed with a suffix-based deployment
strategy, allowing multiple isolated deployments to coexist in the same AWS account.

### AWS Account Requirements

- An AWS account with sufficient credit / payment method.
- An EC2 instance (t2.large recommended; choose an Ubuntu or Amazon Linux 2 AMI), with an attached IAM role having the
  following permissions:
    - [AmazonDynamoDBFullAccess](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AmazonDynamoDBFullAccess.html)
    - [AmazonEC2ContainerRegistryFullAccess](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AmazonEC2ContainerRegistryFullAccess.html)
    - [AmazonEC2FullAccess](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AmazonEC2FullAccess.html)
    - [AmazonECS_FullAccess](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AmazonECS_FullAccess.html)
    - [AmazonS3FullAccess](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AmazonS3FullAccess.html)
    - [AmazonSSMFullAccess](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AmazonSSMFullAccess.html)
    - [AmazonVPCFullAccess](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AmazonVPCFullAccess.html)
    - [AWSAppRunnerFullAccess](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AWSAppRunnerFullAccess.html)
    - [AWSStepFunctionsFullAccess](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AWSStepFunctionsFullAccess.html)
    - [IAMFullAccess](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/IAMFullAccess.html)
    - [AWSCloudFormationFullAccess](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AWSCloudFormationFullAccess.html)

### Prerequisites

- Docker 20.10.x or later
- AWS CLI v2
- Python 3.8+
- Node.js 16.x
- AWS CDK CLI 2.x
- jq (JSON processor)

**Note** - all these are automatically setup by the installation script

## Automatic Setup and Installation Script

Installs all prerequisites and necessary AWS infrastructure for FloTorch automatically before installing the FloTorch
components.

1. Go into your AWS EC2 instance (Using SSH, SSM, or Instance Connect) (Choose an Ubuntu or Amazon Linux 2 AMI).
2. Clone the FloTorch git repository and follow the steps below to automatically install FloTorch and its prerequisites
   on AWS:

   ```bash
   git clone https://github.com/FissionAI/FloTorch.git
   cd FloTorch
   cd cdk
   ./deploy.sh
   ```

The `deploy.sh` script supports Ubuntu and Amazon Linux 2, automatically detecting the OS and using the appropriate
package manager (`apt` for Ubuntu, `yum` for Amazon Linux). This script will also automatically install and set up the
prerequisites needed for FloTorch to be running.

## What components are used & installed?

- **Networking**
    - VPC with public and private subnets
    - NAT Gateways for private subnet internet access
    - Security Groups for various services
- **OpenSearch Domain**
    - Version: OpenSearch 2.15
    - Instance Type: r7g.large.search
    - Data Nodes: 3
    - Storage: 100GB GP3 EBS volumes
- **DynamoDB Tables**
    - Experiment Table
    - Metrics Table
    - Model Invocations Table
- **S3 Buckets**
    - Data bucket for storing application data
    - Versioning enabled
    - Encryption enabled
- **ECS Configuration**
    - Fargate Task Definitions
        - Memory: 32GB
        - CPU: 8 vCPUs
        - Task Role with necessary permissions
- **Step Functions State Machine**
    - Parallel execution of experiments
    - Map state with failure tolerance:
        - Maximum concurrency: 10
        - Continues processing even if individual experiments fail
    - Lambda function configurations:
        - Memory: 1024MB
- **App Runner Service**
    - 4 vCPU and 12 GM memory

### Post-Installation

After successful deployment, you'll receive:

1. **Access Information**:
    - Web UI URL (App Runner endpoint)
    - Nginx authentication credentials
    - OpenSearch domain endpoint

2. **Resource Details**:
    - Stack name and ID
    - Region information
    - Created resource IDs

### Uninstallation

To remove FloTorch and its infrastructure:

1. Go to AWS CloudFormation console in your deployed region
2. Remove all images in the each of the following repositories:
    - `flotorch-indexing-<suffix>`
    - `flotorch-retriever-<suffix>`
    - `flotorch-app-<suffix>`
    - `flotorch-evaluation-<suffix>`
    - `flotorch-runtime-<suffix>`
3. Delete the following stacks in order:
    - `FlotorchAppStack-<suffix>`
    - `FlotorchStateMachineStack-<suffix>`
    - `FlotorchVPCStack-<suffix>`

# Using the FloTorch Application for RAG Evaluation

After you login to the App Runner instance hosting the FloTorch UI application, you will be greeted with a Welcome Page.

## Welcome Page

Upon accessing FloTorch, you are greeted with a welcome page. Click ‘Get started’ to initiate your first project.

---

## Viewing Projects

You’ll be taken to the "Projects" section to view all existing projects.  
Each project is listed with details such as ID, Name, Region, Status, and Date of completion or initiation.  
**Example ID**: `5GM2E`

---

## Creating a New Project

When creating a new project, you'll go through three main steps where you'll need to specify the necessary settings and
options for your project.

You will also have the option to use a previously saved configuration file if you have one. Simply click on 'Upload
config' and select a valid JSON file with all necessary parameters. The application will automatically load these
parameters and display the available experiments you can run. If you don't have a configuration file, please proceed
with manual setup.

### Data Strategy

- Click on "Create Project" to start a new project.
- Fill in required fields such as **Project Name**, **Region**, **Knowledge Base Data**, and **Ground Truth Data**.

### Indexing Strategy

In this page, you’ll be configuring experiment indexing-related settings. Define experiment parameters, including:

- **Chunking Strategy**
- **Vector Dimension**
- **Chunk Size**
- **Chunk Overlap Percentage**
- **Indexing Algorithm** (e.g., HNSW)
- **Embedding Model** (e.g., Titan Embeddings V2 - Text)

### Retrieval Strategy

In this page, you’ll be configuring experiment retrieval-related settings. Define the parameters:

- **N shot prompt**; provide a shot prompt file if you’re going with non-zero shot prompt.
- **KNN**
- **Inferencing LLM**
- **Inferencing LLM Temperature**

Once these are selected, all the valid configurations will be displayed on the next page based on the choices you’ve
made.

You will have the option to save the valid configurations by clicking the ‘Download config’ button.

Please review the configurations and select all the experiments that you’d like to run by marking the checkboxes and
click ‘Run’. Now all the experiments you had marked will be displayed on a table, review it and click ‘Confirm’ to start
the experiments.

You’ll now be taken back to the projects page where you can monitor the status of experiments.

Each experiment is tracked by ID, embedding model used, indexing algorithm, and other parameters.  
**Example statuses** include "Not Started", "In Progress", “Failed” or "Completed".

If you select an experiment that is in progress, you’ll be able to view its status in the experiment table.  
**Statuses** include:

- "Not started"
- "Indexing in progress"
- "Retrieval in progress"
- "Completed"

---

## Evaluation

Once an experiment is completed, an evaluation will be run based on a few metrics and the results will be displayed in
the experiment table along with directional pricing and the duration.  
The evaluation metrics include:

- **Faithfulness**
- **Context Precision**
- **Aspect Critic**
- **Answer Relevancy**

If you’d like to see the answers the model generated, you can click on the experiment ID to view them along with the
questions and the ground truth answers.

You’ll also have the option to view all the parameters of the experiment configuration; click the ‘details’ button on
the same page.

# Frequently Asked Questions

## 1. What is FloTorch.ai? What are its service offerings?

FloTorch.ai is an innovative platform designed to simplify and optimize the selection and configuration of Large
Language Models (LLMs) for use in Retrieval Augmented Generation (RAG) systems. It addresses the challenges of manual
evaluation, resource-intensive experimentation, and complex performance comparisons by providing an automated,
user-friendly approach to decision-making. The platform enables efficient and cost-effective utilization of LLMs, making
it a valuable tool for startups, researchers, developers, and enterprises.

### Service Offerings of FloTorch.ai:

- **Automated Evaluation of LLMs**
    - FloTorch.ai analyzes multiple LLM configurations by evaluating combinations of hyperparameters specified by users.
    - It measures key performance metrics such as relevance, fluency, and robustness.
- **Performance Insights**
    - Provides detailed performance scores for each evaluated LLM configuration.
    - Offers actionable insights into execution times and pricing, helping users understand the cost-effectiveness of
      each setup.
- **Cost and Time Efficiency**
    - Streamlines the LLM selection process by eliminating manual trial-and-error.
    - Saves time and resources by automating comparisons and evaluations.
- **User-Friendly Decision-Making**
    - Helps users make data-driven decisions aligned with their specific goals and budgets.
    - Simplifies the complexity of optimizing LLMs in RAG systems.
- **Broad Applicability**
    - Caters to diverse use cases, such as enhancing customer experiences, improving content generation, and refining
      data retrieval processes.
- **Targeted Support for Users**
    - Designed for startups, data scientists, developers, researchers, and enterprises seeking to optimize AI-driven
      systems.

By focusing on performance, cost, and time efficiency, FloTorch.ai empowers users to maximize the potential of
generative AI without the need for extensive experimentation.

---

## 2. Is an API key required to be able to use this tool?

It is a platform hosted on AWS infrastructure and provides web-based access through an App Runner instance; it is common
for such systems to require authentication mechanisms for secure access.

### For Web-Based Access:

After the installation is complete, users receive a web URL and credentials to log into the FloTorch application. This
implies that secure login credentials (possibly including an API key or token) are required for authentication.

### For Programmatic Access:

If FloTorch.ai provides an API for external integrations, it is likely that credentials would be required to
authenticate API calls.

### AWS Infrastructure:

Since FloTorch runs on AWS, users must have their AWS credentials configured locally to deploy and manage
infrastructure. This is separate from accessing the FloTorch application itself.

---

## 3. Can I run this tool from a local machine, or do I have to necessarily use an EC2 instance?

FloTorch.ai is designed primarily for deployment on AWS infrastructure, including the use of an EC2 instance for setup
and hosting. However, whether it can be run from a local machine depends on the specific requirements of the tool and
the intended use case.

---

## 4. Is there any sample data available for use as knowledge base data and ground truth data?

FloTorch.ai includes sample data for knowledge base data and ground truth data. However, FloTorch typically provides
some form of example datasets or pre-configured templates to help users get started.

---

## 5. Do I require AWS account access as a root user to be able to use the features and to be able to get the tool running?

No, you do not require root user access to an AWS account to use and set up FloTorch.ai. However, you do need an AWS
account with sufficient permissions to perform specific actions necessary for deploying and managing the infrastructure.
Using the root account directly is not recommended for security reasons. Instead, you should use an IAM user or role
with the required permissions.

---

## 6. Who can help me in troubleshooting the errors I get in the tool?

If you encounter errors while using FloTorch.ai, there are several avenues to seek help and resolve the issues:

- Check the installation guide, FAQs, and other resources provided in the FloTorch repository or official website.
- Review detailed error logs (if available) for clues. The application may log specific issues during infrastructure
  setup or usage.

---

## 7. Can I contact someone or is there a way of getting some online support?

### Support Channels

- **GitHub Repository:**
    - If the tool is hosted on GitHub (e.g., FissionAI/FloTorch), check for an "Issues" tab.
    - You can report bugs or errors by creating a new issue with detailed information.
- **FloTorch.ai Website**

---

## 8. What is evaluation? What does the evaluation process do?

Evaluation refers to the process of analyzing the performance of the experiments conducted using Large Language Models (
LLMs) for Retrieval Augmented Generation (RAG) tasks. The evaluation process measures how effectively the selected
configurations and models meet specific criteria, such as relevance, fluency, robustness, and cost efficiency.

### Evaluation Process:

- **Metrics Assessment:**
    - Faithfulness
    - Context Precision
    - Aspect Critic
    - Answer Relevancy
- **Cost and Time Analysis**
- **Configuration Validation**
- **Result Visualization**
- **Iterative Improvement**

---

## 9. What is the data strategy and what is the retrieval strategy?

Data strategy and retrieval strategy are key components in configuring and optimizing experiments involving RAG systems.

---

## 10. Is there a limit on the size of the files I can upload?

Yes, the Knowledge Base dataset size limit is restricted to **40MB**.

---

## 11. I want to contribute to the GitHub source code of FloTorch.ai. Is there a way in which I can contribute?

[GitHub Repository](https://github.com/your-username/FloTorch.git)

---

## 12. Can I use this tool for commercial purposes?

This tool is governed by the terms and conditions of the **APACHE 2.0 license**.

---

## 13. When will this tool support SageMaker models?

It will be released shortly. Please stay tuned to the FloTorch.ai website for regular updates.

---

## 14. What is the meaning of directional pricing? Is it not accurate?

Directional pricing is an effective price taken for an experiment to complete. It is the summation of OpenSearch price,
embedding model price, retrieval, and evaluation price.

---

## 15. Is there a limit on the number of experiments I can run with this tool?

Yes, here are restrictions from the tool:

1. KB dataset limit - **40MB**
2. GT questions - **50**
3. Max number of experiments - **25**

---

## 16. When is the next version of the tool going to be released?

The next version of the product will be released shortly. Stay tuned to the FloTorch.ai website for regular updates.

---

## 17. How much time does it take to complete an experiment with a typical configuration?

The time it takes to complete an experiment in FloTorch.ai with a typical configuration can vary based on several
factors, including the complexity of the configuration, the size of the data, the type of model used, and the available
computational resources.

---

## 18. Is there a default configuration available in the GitHub repository?

No, we do not have any default configuration available in Git.

---

## 19. Is the data which I use (project data and evaluation data) transferred to the cloud or made public?

No, it will be saved in an S3 bucket, but it is not made public. It will be limited to your AWS Account based on your
default IAM configurations and Security Group settings.

---

## 20. What is the licensing mechanism for this tool?

The license is **Apache 2.0**.

# Open Source Developer Contribution Guidelines

This document outlines the guidelines for contributing to the project to maintain consistency and code quality.

### Adding an Embedding Model or Inference Model

Follow the detailed steps provided in [instructions.md](./instructions.md).

### Master Branch

- The `master` branch is the primary branch and should remain stable.
- **Avoid pushing directly to the `master` branch.** All changes must go through the pull request process.

### Feature Branches

- All new feature branches must be created from the `master` branch.
- Use descriptive names for feature branches.  
  Example: `feature/bedrock_claude_inferencer`

### Pull Requests

- All code changes must be submitted as pull requests.
- Each pull request should be reviewed by at least one other developer.
- Keep pull requests small and focused on a specific feature or fix.
- Include relevant information in commit messages to provide context.

### Branch Hygiene

- Delete feature branches after they have been successfully merged into `master`.

### Testing Changes Locally

- Before submitting a pull request, thoroughly test your changes locally to ensure they work as expected.

### Naming Conventions

- Use **snake_case** for:
    - names
    - Configuration variables
    - python file names
      Example: `example_snake_case`
