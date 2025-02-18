# FloTorch Installation & Setup Guide

This guide provides a complete, step-by-step process to set up and manage environments for FloTorch. Follow the instructions carefully for both creating a new environment and updating an existing one.

---

## Prerequisites

Before you begin, ensure that you have the following installed:

- **AWS CLI** (configured with appropriate credentials and permissions to update CloudFormation stacks)
- **jq** (for processing JSON files)
- **Docker** (for building and pushing container images)
- **Bash** (the provided scripts are Bash-based)

---

## Environment Configuration

FloTorch uses environment configuration files stored in the `.envs` directory. Each environment is represented by a JSON file that contains the following parameters:

- `version`: The version of the deployment (used in the CloudFormation template URL)
- `project_name`: The name of your project (this is used as the CloudFormation stack name)
- `table_suffix`: A suffix for naming tables/resources
- `client_name`: The client identifier
- `opensearch_user`: OpenSearch username
- `opensearch_password`: OpenSearch password
- `nginx_password`: Nginx password
- `region`: AWS region for deployment
- `prerequisites_met`: Confirmation if prerequisites are met
- `need_opensearch`: Flag indicating if OpenSearch is required

The environment file is created by the `save_environment` function and loaded by the `load_environment` function in `provision.sh`.

---

## Setup Scenarios

### 1. Creating a New Environment

When you run the `provision.sh` script and no environments exist (i.e. the `.envs` directory is empty), the script will:

1. Prompt you for required configuration details such as version, project name, table suffix, client name, and other parameters.
2. Save your configuration to a JSON file inside the `.envs` directory (e.g., `.envs/<suffix>.json`).
3. Proceed with provisioning based on the entered parameters.

### 2. Updating an Existing Environment

If the `.envs` directory already exists and contains environment files, the script will detect existing configurations and prompt you with:

```
Do you want to create a new environment or update an existing one? (new/update):
```

If you choose `update`, the following process occurs:

1. The script calls the `list_environments` function, allowing you to see available environments.
2. It then prompts you to enter the environment suffix to update.
3. Once a valid environment file (e.g., `.envs/<suffix>.json`) is identified, the script:
   - Loads the environment configuration using the `load_environment` function (which sets variables like `VERSION`, `PROJECT_NAME`, `TABLE_SUFFIX`, `REGION`, etc.)
   - Executes `build_and_push_images`, which builds and pushes the necessary Docker images.
   - Calls the `update_cfn_stack` function to update the CloudFormation stack.

#### CloudFormation Stack Update Details

- The `update_cfn_stack` function takes two parameters: the AWS region and the version.
- It uses the `PROJECT_NAME` value from the loaded environment JSON file as the stack name. This makes the stack name dynamic per environment.
- The CloudFormation stack is updated using the template URL:

```
https://flotorch-public.s3.us-east-1.amazonaws.com/${VERSION}/templates/master-template.yaml
```

- The function provides status messages to indicate whether the stack update was initiated successfully or if an error occurred.

---

## Running the Provision Script

To run the provision script, execute the following command in your terminal:

```bash
./provision.sh
```

Based on your environment setup (new or update), follow the on-screen prompts. Ensure that you have met all prerequisites mentioned above before executing the script.

---

## Troubleshooting and Verification

- **AWS CLI Errors:** Ensure that your AWS CLI is correctly configured with the necessary IAM permissions, especially for `cloudformation update-stack` operations.
- **JSON Parsing Errors:** Make sure the `jq` tool is installed, as it's used to load environment variables from the JSON files.
- **Docker Issues:** Verify that your Docker daemon is running if you encounter problems during the image build and push process.
- **CloudFormation Stack Update:** After the script updates the stack, check the AWS CloudFormation console to monitor the progress and status of the stack update.

---

## Summary

- **New Environment Creation**: The script collects configuration parameters, creates a JSON file in `.envs`, and provisions a new environment.
- **Environment Update**: The script loads an existing environment, builds and pushes Docker images, and updates the CloudFormation stack using dynamic parameters (with `PROJECT_NAME` as the stack name and a versioned template URL).

If you encounter any issues or have questions, please refer to this guide for troubleshooting or contact the support team.
