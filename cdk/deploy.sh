#!/bin/bash
set -e

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="MacOS"
    elif [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VERSION=$VERSION_ID
    else
        echo "Cannot detect OS"
        exit 1
    fi
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Homebrew (MacOS only)
install_homebrew() {
    if [[ "$OS" != "MacOS" ]]; then
        return
    fi
    
    if command_exists brew; then
        echo "Homebrew is already installed"
        brew --version
    else
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
}

# Function to install Docker
install_docker() {
    if command_exists docker; then
        echo "Docker is already installed"
        docker --version
    else
        echo "Installing Docker..."
        if [[ "$OS" == "MacOS" ]]; then
            brew install --cask docker
            # Open Docker.app to complete installation
            open /Applications/Docker.app
            echo "Please wait for Docker to start and complete initial setup..."
            sleep 10
        elif [[ "$OS" == "Ubuntu" ]]; then
            sudo apt-get update
            sudo apt-get install -y ca-certificates curl gnupg
            sudo install -m 0755 -d /etc/apt/keyrings
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
            sudo chmod a+r /etc/apt/keyrings/docker.gpg
            echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            sudo apt-get update
            sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
            sudo usermod -aG docker $USER
            newgrp docker
        elif [[ "$OS" == "Amazon Linux" ]]; then
            sudo yum update -y
            sudo yum install -y docker
            sudo systemctl start docker
            sudo systemctl enable docker
            sudo usermod -aG docker $USER
            newgrp docker
        fi
    fi
}

# Function to install AWS CLI
install_awscli() {
    if command_exists aws; then
        echo "AWS CLI is already installed"
        aws --version
    else
        echo "Installing AWS CLI..."
        if [[ "$OS" == "MacOS" ]]; then
            brew install awscli
        else
            curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
            sudo apt install -y unzip || sudo yum install -y unzip
            unzip awscliv2.zip
            sudo ./aws/install
            rm -rf aws awscliv2.zip
        fi
    fi
}

# Function to install Python and pip
install_python() {
    local python_check=false
    local pip_check=false

    # Check Python installation
    if command_exists python3; then
        echo "Python is already installed"
        python3 --version
        python_check=true
    fi

    # Check pip installation
    if command_exists pip3; then
        echo "pip is already installed"
        pip3 --version
        pip_check=true
    fi

    # Install if either Python or pip is missing
    if [[ "$python_check" == false || "$pip_check" == false ]]; then
        echo "Installing Python and pip..."
        if [[ "$OS" == "MacOS" ]]; then
            brew install python3
        elif [[ "$OS" == "Ubuntu" ]]; then
            sudo apt-get update
            
            # Install Python if not exists
            if [[ "$python_check" == false ]]; then
                sudo apt-get install -y python3
            fi
            
            # Install pip if not exists
            if [[ "$pip_check" == false ]]; then
                sudo apt-get install -y python3-pip
            fi
        elif [[ "$OS" == "Amazon Linux" ]]; then
            sudo yum update -y
            
            # Install Python if not exists
            if [[ "$python_check" == false ]]; then
                sudo yum install -y python3
            fi
            
            # Install pip if not exists
            if [[ "$pip_check" == false ]]; then
                sudo yum install -y python3-pip
            fi
        fi
    fi

    # Final verification
    if ! command_exists python3; then
        echo "Error: Python installation failed"
        exit 1
    fi

    if ! command_exists pip3; then
        echo "Error: pip installation failed"
        exit 1
    fi

    # Print versions
    echo "Python version:"
    python3 --version
    echo "Pip version:"
    pip3 --version
}

# Function to install Node.js
install_node() {
    if command_exists node; then
        echo "Node.js is already installed"
        node --version
    else
        echo "Installing Node.js..."
        if [[ "$OS" == "MacOS" ]]; then
            brew install node
        elif [[ "$OS" == "Ubuntu" ]]; then
            curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
            sudo apt-get install -y nodejs
        elif [[ "$OS" == "Amazon Linux" ]]; then
            if grep -q "Amazon Linux 2" /etc/os-release; then
                echo "Detected Amazon Linux 2 - Installing Node.js (LTS)"
                curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
                echo 'export NVM_DIR="$HOME/.nvm"' >> ~/.bashrc
                echo '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"' >> ~/.bashrc
                echo '[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"' >> ~/.bashrc
                source ~/.bashrc && nvm install --lts && nvm use --lts
            else
                echo "Detected Amazon Linux - Installing Node.js (LTS)"
                curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
                echo 'export NVM_DIR="$HOME/.nvm"' >> ~/.bashrc
                echo '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"' >> ~/.bashrc
                echo '[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"' >> ~/.bashrc
                source ~/.bashrc && nvm install --lts && nvm use --lts
            fi
        fi
    fi
}

# Function to install AWS CDK
install_awscdk() {
    if command_exists cdk; then
        echo "AWS CDK is already installed"
        cdk --version
    else
        echo "Installing AWS CDK..."
        if [[ "$OS" == "MacOS" ]]; then
            npm install -g aws-cdk
        elif [[ "$OS" == "Ubuntu" ]]; then
            sudo npm install -g aws-cdk
        elif [[ "$OS" == "Amazon Linux" ]]; then
            source ~/.bashrc && npm install -g aws-cdk && source ~/.bashrc
        else
            echo "Unsupported OS for AWS CDK installation"
            exit 1
        fi
    fi
}

install_python_requirements() {
    # Check if requirements.txt exists
    if [[ ! -f "requirements.txt" ]]; then
        echo "No requirements.txt found. Skipping requirements installation."
        return 0
    fi

    # Install requirements based on OS
    echo "Installing Python requirements..."
    if [[ "$OS" == "MacOS" ]]; then
        pip3 install -r requirements.txt --break-system-packages --upgrade
    elif [[ "$OS" == "Ubuntu" ]]; then
        pip3 install -r requirements.txt --break-system-packages --upgrade
    elif [[ "$OS" == "Amazon Linux" ]]; then
        pip3 install -r requirements.txt --upgrade
    else
        echo "Unsupported OS for requirements installation"
        exit 1
    fi
}

# Function to setup prerequisites
setup_prerequisites() {
    echo "Setting up prerequisites..."
    detect_os
    echo "Detected OS: $OS"

    if [[ "$OS" == "MacOS" ]]; then
        install_homebrew
        eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [[ "$OS" == "Ubuntu" ]]; then
        sudo apt-get update
    elif [[ "$OS" == "Amazon Linux" ]]; then
        sudo yum update -y
    else
        echo "Unsupported OS"
        exit 1
    fi

    install_docker
    install_awscli
    install_python
    # sleep 10
    install_node
    install_awscdk
    install_python_requirements
    echo "All prerequisites installed successfully!"
}

# Function to check if running in Docker
is_running_in_docker() {
    [ -f /.dockerenv ] || grep -q 'docker\|lxc' /proc/1/cgroup
}

# Function to validate Docker environment
validate_docker_env() {
    if [ -z "${AWS_ACCOUNT_ID}" ]; then
        echo "Error: AWS_ACCOUNT_ID environment variable is not set"
        exit 1
    fi
    
    if [ -z "${AWS_DEFAULT_REGION}" ]; then
        echo "Error: AWS_DEFAULT_REGION environment variable is not set"
        exit 1
    fi
    
    echo "Using AWS Account: ${AWS_ACCOUNT_ID}"
    echo "Using AWS Region: ${AWS_DEFAULT_REGION}"
}

# Only run prerequisites if not in Docker
# if ! is_running_in_docker; then
#     setup_prerequisites
# else
#     validate_docker_env
# fi

# setup_prerequisites

# Set AWS variables from local environment if not in Docker
if [ -z "${AWS_ACCOUNT_ID}" ]; then
    export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
fi
    
if [ -z "${AWS_DEFAULT_REGION}" ]; then
    export AWS_DEFAULT_REGION=$(aws configure get region)
fi

# Default values
AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID:-""}
AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-""}
# TABLE_SUFFIX=${TABLE_SUFFIX:-$(generate_suffix)}

# Generate random 6-character alphanumeric suffix using Python
generate_suffix() {
    python3 -c "import random; import string; print(''.join(random.choices(string.ascii_lowercase + string.digits, k=6)))"
}

# Function to check if a bucket exists
check_bucket_exists() {
    aws s3api head-bucket --bucket "$1" 2>/dev/null
    return $?
}

# Function to delete all versions from a bucket
delete_bucket_versions() {
    local bucket_name=$1
    echo "Emptying S3 bucket: ${bucket_name}"

    # List all versions and delete markers
    local versions=$(aws s3api list-object-versions \
        --bucket "${bucket_name}" \
        --output=json \
        --query '{Objects: [].{Key:Key,VersionId:VersionId}}' \
        2>/dev/null || echo '{"Objects": []}')

    # Check if there are any objects to delete
    if [ "$(echo $versions | jq '.Objects | length')" -gt 0 ]; then
        echo "Deleting objects from bucket..."
        aws s3api delete-objects \
            --bucket "${bucket_name}" \
            --delete "${versions}" \
            2>/dev/null || true
    else
        echo "Bucket is already empty"
    fi
}

# Function to get stack outputs
get_stack_output() {
    local stack_name=$1
    local output_key=$2
    jq -r ".[\"${stack_name}\"].${output_key}" cdk-outputs.json 2>/dev/null || echo ""
}

# Function to delete ECR images
delete_ecr_images() {
    local repo_name=$1
    echo "Deleting images from ${repo_name}..."

    # List all image IDs
    local images=$(aws ecr list-images \
        --repository-name "${repo_name}" \
        --query 'imageIds[*]' \
        --output json 2>/dev/null || echo "[]")

    if [ "$images" != "[]" ]; then
        echo "Found images to delete in ${repo_name}"
        aws ecr batch-delete-image \
            --repository-name "${repo_name}" \
            --image-ids "${images}" 2>/dev/null || true
    else
        echo "No images found in repository ${repo_name}"
    fi
}

# Function to destroy resources and stacks
destroy_resources() {
    echo "Starting resource cleanup..."

    # Prompt user for AWS_ACCOUNT_ID if not set
    if [ -z "$AWS_ACCOUNT_ID" ]; then
        read -p "Enter AWS Account ID: " AWS_ACCOUNT_ID
    fi

    # Prompt user for AWS_DEFAULT_REGION if not set
    if [ -z "$AWS_DEFAULT_REGION" ]; then
        read -p "Enter AWS Region: " AWS_DEFAULT_REGION
    fi

    export AWS_ACCOUNT_ID
    export AWS_DEFAULT_REGION

    # Ensure we are in the cdk directory
    SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
    cd "$SCRIPT_DIR"

    # If TABLE_SUFFIX is not provided, try to get it from cdk-outputs.json
    if [ -z "$TABLE_SUFFIX" ]; then
        if [ -f cdk-outputs.json ]; then
            # Get the VPC stack name (first key in the outputs)
            VPC_STACK_NAME=$(jq -r 'keys[0]' cdk-outputs.json)
            if [[ $VPC_STACK_NAME =~ FlotorchVPCStack-(.*) ]]; then
                TABLE_SUFFIX="${BASH_REMATCH[1]}"
            fi
        fi

        # If still no TABLE_SUFFIX, try to find it from CloudFormation directly
        if [ -z "$TABLE_SUFFIX" ]; then
            # List stacks and find the most recent VPC stack
            VPC_STACK_NAME=$(aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE --query 'StackSummaries[?contains(StackName, `FlotorchVPCStack-`)].StackName' --output text | head -n1)
            if [[ $VPC_STACK_NAME =~ FlotorchVPCStack-(.*) ]]; then
                TABLE_SUFFIX="${BASH_REMATCH[1]}"
            fi
        fi
    fi

    if [ -z "$TABLE_SUFFIX" ]; then
        echo "Error: Could not determine table suffix. Please provide it as an argument: ./deploy.sh --destroy <table-suffix>"
        exit 1
    fi

    echo "Found stacks with suffix: ${TABLE_SUFFIX}"

    VPC_STACK_NAME="FlotorchVPCStack-${TABLE_SUFFIX}"
    STATE_MACHINE_STACK_NAME="FlotorchStateMachineStack-${TABLE_SUFFIX}"
    APP_STACK_NAME="FlotorchAppStack-${TABLE_SUFFIX}"

    # Get resource names from outputs if cdk-outputs.json exists
    if [ -f cdk-outputs.json ]; then
        DATA_BUCKET=$(get_stack_output "${VPC_STACK_NAME}" "DataBucketName")
    else
        # Try to get bucket name from CloudFormation outputs
        DATA_BUCKET=$(aws cloudformation describe-stacks --stack-name "${VPC_STACK_NAME}" --query 'Stacks[0].Outputs[?OutputKey==`DataBucketName`].OutputValue' --output text)
    fi

    # Get ECR repository names
    REPO_NAMES=(
        "flotorch-indexing-${TABLE_SUFFIX}"
        "flotorch-retriever-${TABLE_SUFFIX}"
        "flotorch-app-${TABLE_SUFFIX}"
        "flotorch-evaluation-${TABLE_SUFFIX}"
        "flotorch-runtime-${TABLE_SUFFIX}"
    )

    # Clean up S3 bucket if it exists
    if [ ! -z "$DATA_BUCKET" ] && check_bucket_exists "$DATA_BUCKET"; then
        echo "Found bucket: ${DATA_BUCKET}"
        delete_bucket_versions "${DATA_BUCKET}"
    else
        echo "Bucket ${DATA_BUCKET} not found or not accessible"
    fi

    # Clean up ECR repositories
    for REPO_NAME in "${REPO_NAMES[@]}"; do
        if aws ecr describe-repositories --repository-names "${REPO_NAME}" 2>/dev/null; then
            echo "Cleaning up ECR repository: ${REPO_NAME}"
            delete_ecr_images "${REPO_NAME}"
        else
            echo "Repository ${REPO_NAME} not found or not accessible"
        fi
    done

    # Destroy CDK stacks in reverse order
    echo "Destroying App Stack..."
    aws cloudformation delete-stack --stack-name "${APP_STACK_NAME}" --region "${AWS_DEFAULT_REGION}" 2>/dev/null || true
    aws cloudformation wait stack-delete-complete --stack-name "${APP_STACK_NAME}" --region "${AWS_DEFAULT_REGION}" 2>/dev/null || true
    echo "App Stack deleted or not found."

    echo "Destroying State Machine Stack..."
    aws cloudformation delete-stack --stack-name "${STATE_MACHINE_STACK_NAME}" --region "${AWS_DEFAULT_REGION}"
    aws cloudformation wait stack-delete-complete --stack-name "${STATE_MACHINE_STACK_NAME}" --region "${AWS_DEFAULT_REGION}"
    echo "State Machine Stack deleted."

    echo "Destroying VPC Stack..."
    aws cloudformation delete-stack --stack-name "${VPC_STACK_NAME}" --region "${AWS_DEFAULT_REGION}"
    aws cloudformation wait stack-delete-complete --stack-name "${VPC_STACK_NAME}" --region "${AWS_DEFAULT_REGION}"
    echo "VPC Stack deleted."

    echo "Resource cleanup completed."
    exit 0
}

# Function to get ECR repository image count
get_ecr_image_count() {
    local repo_name=$1
    local count=$(aws ecr list-images \
        --repository-name "${repo_name}" \
        --query 'length(imageIds)' \
        --output text 2>/dev/null || echo "0")
    echo "$count"
}

# Function to list resources to be destroyed
list_resources_to_destroy() {
    local suffix=$1
    echo -e "\nThe following resources will be destroyed:"
    echo "----------------------------------------"
    
    # List CloudFormation Stacks
    echo "CloudFormation Stacks:"
    echo "  - FlotorchAppStack-${suffix}"
    echo "  - FlotorchStateMachineStack-${suffix}"
    echo "  - FlotorchVPCStack-${suffix}"
    
    # List S3 Buckets
    local data_bucket=""
    if [ -f cdk-outputs.json ]; then
        data_bucket=$(get_stack_output "FlotorchVPCStack-${suffix}" "DataBucketName")
        if [ ! -z "$data_bucket" ]; then
            echo -e "\nS3 Buckets:"
            echo "  - ${data_bucket}"
        fi
    fi
    
    # List ECR Repositories and their image counts
    echo -e "\nECR Repositories:"
    local repo_names=(
        "flotorch-indexing-${suffix}"
        "flotorch-retriever-${suffix}"
        "flotorch-app-${suffix}"
        "flotorch-evaluation-${suffix}"
    )
    
    for repo_name in "${repo_names[@]}"; do
        if aws ecr describe-repositories --repository-names "${repo_name}" 2>/dev/null; then
            local image_count=$(get_ecr_image_count "${repo_name}")
            echo "  - ${repo_name} (${image_count} images)"
        fi
    done
    
    echo -e "\nWARNING: This action cannot be undone. All data in these resources will be permanently deleted."
    read -p "Are you sure you want to proceed with destruction? (yes/no) " confirm
    if [[ "$confirm" != "yes" ]]; then
        echo "Destruction cancelled."
        exit 0
    fi
}

# Function to generate a random password
generate_password() {
    # Generate a 16-character random password with letters, numbers, and special characters
    password=$(LC_ALL=C tr -dc 'A-Za-z0-9!@#$%^&*' < /dev/urandom | head -c 16)
    echo "$password"
}

# Main script

# Ensure we are in the script directory
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "${SCRIPT_DIR}"

# Only prompt for AWS credentials if not in Docker
if ! is_running_in_docker; then
    # Prompt user for AWS_ACCOUNT_ID
    read -p "Enter AWS Account ID: " AWS_ACCOUNT_ID

    # Prompt user for AWS_DEFAULT_REGION
    read -p "Enter AWS Region: " AWS_DEFAULT_REGION
fi

# Check for destroy flag: --destroy
if [ "$1" == "--destroy" ]; then
    # Attempt to read suffix from SSM Parameter Store
    TABLE_SUFFIX=$(aws ssm get-parameter --region $AWS_DEFAULT_REGION --name "/flotorch/stack_suffix" --query 'Parameter.Value' --output text 2>/dev/null)
    echo "Using existing table suffix from SSM Parameter Store: ${TABLE_SUFFIX}"

    # Now, call your destroy function with the TABLE_SUFFIX
    list_resources_to_destroy "${TABLE_SUFFIX}"
    destroy_resources
    # Delete SSM parameters
    echo "Deleting SSM parameters..."
    aws ssm delete-parameter --name "/flotorch/stack_suffix" --region $AWS_DEFAULT_REGION || true
    aws ssm delete-parameter --name "/flotorch/username" --region $AWS_DEFAULT_REGION || true
    aws ssm delete-parameter --name "/flotorch/password" --region $AWS_DEFAULT_REGION || true
    echo "SSM parameters deleted."

fi

# Check if stack_suffix exists
if TABLE_SUFFIX_SSM=$(aws ssm get-parameter --region $AWS_DEFAULT_REGION --name "/flotorch/stack_suffix" --query 'Parameter.Value' --output text 2>/dev/null); then
    TABLE_SUFFIX="$TABLE_SUFFIX_SSM"
    echo "Using existing table suffix from SSM Parameter Store: ${TABLE_SUFFIX}"
else
    # Generate new table suffix and save it to SSM Parameter Store
    TABLE_SUFFIX=$(generate_suffix)
    aws ssm put-parameter --region $AWS_DEFAULT_REGION --name "/flotorch/stack_suffix" --type String --value "$TABLE_SUFFIX" --overwrite
    echo "Generated and saved new table suffix to SSM Parameter Store: ${TABLE_SUFFIX}"
fi

export TABLE_SUFFIX

# Silence Node.js version warning
export JSII_SILENCE_WARNING_UNTESTED_NODE_VERSION=true

echo "Running CDK bootstrap..."
cdk bootstrap

echo "Deploying VPC Stack..."
cdk deploy "FlotorchVPCStack-${TABLE_SUFFIX}" --require-approval never --outputs-file cdk-outputs.json --exclusively

aws ecr get-login-password \
    --region us-east-1 | docker login \
    --username AWS \
    --password-stdin 709825985650.dkr.ecr.us-east-1.amazonaws.com
    
CONTAINER_IMAGES="709825985650.dkr.ecr.us-east-1.amazonaws.com/fission-labs/flotorch-indexing:1.6.0,709825985650.dkr.ecr.us-east-1.amazonaws.com/fission-labs/flotorch-ai:1.6.0,709825985650.dkr.ecr.us-east-1.amazonaws.com/fission-labs/flotorch-evaluation:1.6.0,709825985650.dkr.ecr.us-east-1.amazonaws.com/fission-labs/flotorch-app:1.6.0,709825985650.dkr.ecr.us-east-1.amazonaws.com/fission-labs/flotorch-runtime:1.6.0,709825985650.dkr.ecr.us-east-1.amazonaws.com/fission-labs/flotorch-retriever:1.6.0"    

for i in $(echo $CONTAINER_IMAGES | sed "s/,/ /g"); do docker pull $i; done

aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com

docker tag "709825985650.dkr.ecr.us-east-1.amazonaws.com/fission-labs/flotorch-indexing:1.6.0" ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/flotorch-indexing-${TABLE_SUFFIX}
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/flotorch-indexing-${TABLE_SUFFIX}

docker tag "709825985650.dkr.ecr.us-east-1.amazonaws.com/fission-labs/flotorch-retriever:1.6.0" ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/flotorch-retriever-${TABLE_SUFFIX}
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/flotorch-retriever-${TABLE_SUFFIX}

docker tag "709825985650.dkr.ecr.us-east-1.amazonaws.com/fission-labs/flotorch-evaluation:1.6.0" ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/flotorch-evaluation-${TABLE_SUFFIX}
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/flotorch-evaluation-${TABLE_SUFFIX}

docker tag "709825985650.dkr.ecr.us-east-1.amazonaws.com/fission-labs/flotorch-runtime:1.6.0" ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/flotorch-runtime-${TABLE_SUFFIX}
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/flotorch-runtime-${TABLE_SUFFIX}

docker tag "709825985650.dkr.ecr.us-east-1.amazonaws.com/fission-labs/flotorch-app:1.6.0" ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/flotorch-app-${TABLE_SUFFIX}
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/flotorch-app-${TABLE_SUFFIX}

echo "All images pushed to ecr..."
# Building Lambda Image Start..
# cd ..

# IMAGE_NAME="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/flotorch-runtime-${TABLE_SUFFIX}:1.0"
# aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com
# DOCKERFILE="opensearch/opensearch.Dockerfile"
# docker build --platform linux/amd64 -t "${IMAGE_NAME}" -f "${DOCKERFILE}" --no-cache --push .

# cd cdk
# Building Lambda Image End.

echo "Deploying State Machine Stack..."
cdk deploy "FlotorchStateMachineStack-${TABLE_SUFFIX}" --require-approval never --outputs-file cdk-outputs-state-machine.json --exclusively

# Merge the outputs
jq -s '.[0] * .[1]' cdk-outputs.json cdk-outputs-state-machine.json > cdk-outputs-merged.json
mv cdk-outputs-merged.json cdk-outputs.json
rm cdk-outputs-state-machine.json

# Extract outputs from VPC Stack
echo "Extracting outputs from VPC and State Machine Stacks..."
DATA_BUCKET=$(jq -r '.["FlotorchVPCStack-'"${TABLE_SUFFIX}"'"].DataBucketName' cdk-outputs.json)
STATE_MACHINE_ARN=$(jq -r '.["FlotorchStateMachineStack-'"${TABLE_SUFFIX}"'"].StateMachineArn' cdk-outputs.json)
OPENSEARCH_HOST=$(jq -r '.["FlotorchVPCStack-'"${TABLE_SUFFIX}"'"].OpenSearchDomainEndpoint' cdk-outputs.json)
OPENSEARCH_USERNAME="admin"
OPENSEARCH_PASSWORD="Fission@123"
VECTOR_FIELD_NAME="vectors"
OPENSEARCH_SERVERLESS="false"
EXECUTION_TABLE=$(jq -r '.["FlotorchVPCStack-'"${TABLE_SUFFIX}"'"].ExecutionTableName' cdk-outputs.json)
EXPERIMENT_TABLE=$(jq -r '.["FlotorchVPCStack-'"${TABLE_SUFFIX}"'"].ExperimentTableName' cdk-outputs.json)
METRICS_TABLE=$(jq -r '.["FlotorchVPCStack-'"${TABLE_SUFFIX}"'"].MetricsTableName' cdk-outputs.json)
MODEL_INVOCATIONS_TABLE=$(jq -r '.["FlotorchVPCStack-'"${TABLE_SUFFIX}"'"].ModelInvocationsTableName' cdk-outputs.json)
BEDROCK_ROLE_ARN=$(jq -r '.["FlotorchVPCStack-'"${TABLE_SUFFIX}"'"].FlotorchRoleArn' cdk-outputs.json)
SAGEMAKER_ROLE_ARN=$(jq -r '.["FlotorchVPCStack-'"${TABLE_SUFFIX}"'"].FlotorchRoleArn' cdk-outputs.json)
BEDROCK_LIMIT_CSV="seed/bedrock_limits_small.csv"

aws s3 cp ./bedrock_limits.csv s3://${DATA_BUCKET}/seed/bedrock_limits.csv
aws s3 cp ./bedrock_limits_small.csv s3://${DATA_BUCKET}/seed/bedrock_limits_small.csv

# Move up one directory
cd ..

# Create .env file in fl_torch folder
echo "Creating .env file in fl_torch folder..."
cat > ".env" << EOF
aws_region=${AWS_DEFAULT_REGION}
experiment_question_metrics_table=${METRICS_TABLE}
execution_table=${EXECUTION_TABLE}
experiment_table=${EXPERIMENT_TABLE}
execution_model_invocations_table=${MODEL_INVOCATIONS_TABLE}
step_function_arn=${STATE_MACHINE_ARN}
opensearch_host=${OPENSEARCH_HOST}
opensearch_username=${OPENSEARCH_USERNAME}
opensearch_password=${OPENSEARCH_PASSWORD}
opensearch_serverless=${OPENSEARCH_SERVERLESS}
vector_field_name=${VECTOR_FIELD_NAME}
bedrock_role_arn=${BEDROCK_ROLE_ARN}
sagemaker_role_arn=${SAGEMAKER_ROLE_ARN}
inference_system_prompt="You are an intelligent assistant. Answer user questions using only the provided context. Do not make up information, make assumptions or use external knowledge. If the context does not contain the answer, explicitly state that. Do not disclose sensitive information. Maintain a professional tone and ensure responses are accurate and relevant without assumptions."
s3_bucket=${DATA_BUCKET}
bedrock_limit_csv="seed/bedrock_limits_small.csv"
EOF

cp .env app/
cp .env indexing/
cp .env retriever/
cp .env evaluation/

# Authenticate Docker to ECR
echo "Authenticating with ECR..."
aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com

# Generate random username and password for nginx
NGINX_USER="admin"
NGINX_PASSWORD=$(generate_password)

echo "Generated Nginx credentials:"
echo "Username: $NGINX_USER"
echo "Password: $NGINX_PASSWORD"

# Deploy the CDK stack with the generated password
cd cdk
echo "Deploying App Stack..."
cdk deploy "FlotorchAppStack-${TABLE_SUFFIX}" --app "python3 app.py" --require-approval never --context NGINX_AUTH_USER=$NGINX_USER --context NGINX_AUTH_PASSWORD=$NGINX_PASSWORD
cd ..

echo "All resources deployed successfully!"

# Print the deployment information
echo -e "\n=========================================="
echo "Deployment completed successfully!"
echo "Stack deployed with suffix: ${TABLE_SUFFIX}"
echo "----------------------------------------"
echo "Basic Authentication Credentials:"
echo "Username: $NGINX_USER"
echo "Password: $NGINX_PASSWORD"
echo "==========================================\n"

aws ssm put-parameter --region $AWS_DEFAULT_REGION --name "/flotorch/username" --type String --value "$NGINX_USER" --overwrite
aws ssm put-parameter --region $AWS_DEFAULT_REGION --name "/flotorch/password" --type String --value "$NGINX_PASSWORD" --overwrite