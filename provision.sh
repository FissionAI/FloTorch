#!/bin/bash

# Function to validate password complexity
validate_password() {
    local password=$1
    [[ ${#password} -ge 8 && ${#password} -le 41 ]] &&
    [[ "$password" =~ [A-Za-z] ]] &&
    [[ "$password" =~ [0-9] ]] &&
    [[ "$password" =~ [^A-Za-z0-9] ]]
}

# Function to prompt for password with validation
prompt_password() {
    local prompt_text=$1
    local confirm_text=$2
    while true; do
        read -s -p "$prompt_text" password
        echo
        if validate_password "$password"; then
            read -s -p "$confirm_text" password_confirm
            echo
            if [ "$password" = "$password_confirm" ]; then
                echo "$password"
                break
            else
                echo "Error: Passwords do not match. Please try again."
            fi
        else
            echo "Error: Password must be 12-41 characters with at least one letter, one number, and one symbol."
        fi
    done
}

# Function to save environment to JSON
save_environment() {
    local suffix=$1
    mkdir -p .envs
    cat > ".envs/${suffix}.json" << EOF
{
    "version": "${VERSION}",
    "project_name": "${PROJECT_NAME}",
    "table_suffix": "${TABLE_SUFFIX}",
    "client_name": "${CLIENT_NAME}",
    "opensearch_user": "${OPENSEARCH_USER}",
    "opensearch_password": "${OPENSEARCH_PASSWORD}",
    "nginx_password": "${NGINX_PASSWORD}",
    "region": "${REGION}",
    "prerequisites_met": "${PREREQUISITES_MET}",
    "need_opensearch": "${NEED_OPENSEARCH}"
}
EOF
    echo "Environment configuration saved to .envs/${suffix}.json"
}

# Function to load environment from JSON
load_environment() {
    local env_file=".envs/$1.json"
    if [ -f "$env_file" ]; then
        VERSION=$(jq -r '.version' "$env_file")
        PROJECT_NAME=$(jq -r '.project_name' "$env_file")
        TABLE_SUFFIX=$(jq -r '.table_suffix' "$env_file")
        CLIENT_NAME=$(jq -r '.client_name' "$env_file")
        OPENSEARCH_USER=$(jq -r '.opensearch_user' "$env_file")
        OPENSEARCH_PASSWORD=$(jq -r '.opensearch_password' "$env_file")
        NGINX_PASSWORD=$(jq -r '.nginx_password' "$env_file")
        REGION=$(jq -r '.region' "$env_file")
        PREREQUISITES_MET=$(jq -r '.prerequisites_met' "$env_file")
        NEED_OPENSEARCH=$(jq -r '.need_opensearch' "$env_file")
    else
        echo "Environment file not found: $env_file"
        exit 1
    fi
}

# Function to list available environments
list_environments() {
    if [ -d ".envs" ]; then
        local envs=($(ls .envs/*.json 2>/dev/null | xargs -n 1 basename | sed 's/\.json$//'))
        if [ ${#envs[@]} -eq 0 ]; then
            echo "No environments found"
            return 1
        fi
        echo "Available environments:"
        for env in "${envs[@]}"; do
            echo "  - $env"
        done
        return 0
    else
        echo "No environments found"
        return 1
    fi
}

# Function to build and push Docker images
build_and_push_images() {
    local suffix=$1
    local region=$2

    echo "Building and pushing Docker images for environment ${suffix}..."

    # Get AWS account ID
    local account_id=$(aws sts get-caller-identity --query Account --output text)

    # Login to ECR
    aws ecr get-login-password --region "$region" | docker login --username AWS --password-stdin ${account_id}.dkr.ecr."$region".amazonaws.com

    # Create repositories if they don't exist
    echo "Ensuring ECR repositories exist..."
    local repos=("flotorch-app" "flotorch-indexing" "flotorch-retriever" "flotorch-evaluation" "flotorch-runtime" "flotorch-costcompute")
    for repo in "${repos[@]}"; do
        local repo_name="${repo}-${suffix}"
        if ! aws ecr describe-repositories --repository-names "$repo_name" --region "$region" >/dev/null 2>&1; then
            echo "Creating repository: $repo_name"
            aws ecr create-repository --repository-name "$repo_name" --region "$region" --image-scanning-configuration scanOnPush=true
        else
            echo "Repository $repo_name already exists"
        fi
    done

    # Build and push Docker images
    echo "Building and pushing Docker images..."
    docker build --platform linux/amd64 -t ${account_id}.dkr.ecr."$region".amazonaws.com/flotorch-app-"$suffix":latest -f app/Dockerfile --push .
    docker build --platform linux/amd64 -t ${account_id}.dkr.ecr."$region".amazonaws.com/flotorch-evaluation-"$suffix":latest -f evaluation/fargate_evaluation.Dockerfile --push .
    docker build --platform linux/amd64 -t ${account_id}.dkr.ecr."$region".amazonaws.com/flotorch-runtime-"$suffix":latest -f opensearch/opensearch.Dockerfile --push .

    rm -rf flotorch-indexer
    git clone https://github.com/FissionAI/flotorch-indexer.git
    cd flotorch-indexer
    docker build --platform linux/amd64 -t ${account_id}.dkr.ecr."$region".amazonaws.com/flotorch-indexing-"$suffix":latest -f fargate/handler/indexing/Dockerfile --push .
    cd ..
    rm -rf flotorch-indexer

    rm -rf flotorch-retriever
    git clone https://github.com/FissionAI/flotorch-retriever.git
    cd flotorch-retriever
    docker build --platform linux/amd64 -t ${account_id}.dkr.ecr."$region".amazonaws.com/flotorch-retriever-"$suffix":latest -f fargate/handler/retriever/Dockerfile --push .
    cd ..
    rm -rf flotorch-retriever

    # Build cost compute image
    cd lambda_handlers
    docker build --platform linux/amd64 -t ${account_id}.dkr.ecr."$region".amazonaws.com/flotorch-costcompute-"$suffix":latest -f cost_handler/Dockerfile --push .
    cd ..

    echo "Docker images updated successfully"
}

# Function to update CloudFormation stack
update_cfn_stack() {
    local region="$1"
    local version="$2"
    local stack_name="${PROJECT_NAME}"
    
    echo "Updating CloudFormation stack '${stack_name}'..."
    aws cloudformation update-stack \
        --stack-name "$stack_name" \
        --template-url "https://flotorch-public.s3.us-east-1.amazonaws.com/${version}/templates/master-template.yaml" \
        --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
        --disable-rollback \
        --region "$region"
    
    if [ $? -eq 0 ]; then
        echo "Stack update initiated successfully. Please check AWS Console for status."
    else
        echo "Error: Failed to update CloudFormation stack"
        exit 1
    fi
}

# Function to create OpenSearch service-linked role
create_opensearch_service_role() {
    echo "Creating OpenSearch service-linked role..."
    aws iam get-role --role-name "AWSServiceRoleForAmazonOpenSearchService" >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        aws iam create-service-linked-role --aws-service-name opensearchservice.amazonaws.com || {
            echo "Failed to create OpenSearch service-linked role"
            return 1
        }
        echo "OpenSearch service-linked role created successfully"
    else
        echo "OpenSearch service-linked role already exists"
    fi
}

# Function to update an existing environment
update_environment() {
    local update_suffix=$1
    echo "Loading environment ${update_suffix}..."
    load_environment "$update_suffix"
    
    echo "FloTorch Deployment Update Configuration"
    echo "----------------------------------------"
    echo "Current values shown in brackets. Press Enter to keep current value."
    
    # Get Prerequisites confirmation with current value as default
    while true; do
        read -p "Subscribed to FloTorch on AWS Marketplace? (yes/no) [${PREREQUISITES_MET}]: " new_prerequisites
        new_prerequisites=${new_prerequisites:-$PREREQUISITES_MET}
        if [[ "$new_prerequisites" =~ ^(yes|no)$ ]]; then
            PREREQUISITES_MET=$new_prerequisites
            break
        else
            echo "Error: Please enter either 'yes' or 'no'"
        fi
    done

    # Get OpenSearch confirmation with current value as default
    while true; do
        read -p "Do you need OpenSearch? (yes/no) [${NEED_OPENSEARCH}]: " new_opensearch
        new_opensearch=${new_opensearch:-$NEED_OPENSEARCH}
        if [[ "$new_opensearch" =~ ^(yes|no)$ ]]; then
            NEED_OPENSEARCH=$new_opensearch
            break
        else
            echo "Error: Please enter either 'yes' or 'no'"
        fi
    done

    # Keep VERSION as is or allow update
    read -p "Enter Version [${VERSION}]: " new_version
    VERSION=${new_version:-$VERSION}

    # Get Project Name with current value as default
    read -p "Enter Project Name [${PROJECT_NAME}]: " new_project_name
    PROJECT_NAME=${new_project_name:-$PROJECT_NAME}

    # Table Suffix should not be changeable during update as it would break references
    echo "Table Suffix: ${TABLE_SUFFIX} (cannot be changed during update)"

    # Validate Client Name with current value as default
    while true; do
        read -p "Enter Client Name [${CLIENT_NAME}]: " new_client_name
        new_client_name=${new_client_name:-$CLIENT_NAME}
        if [[ "$new_client_name" =~ ^[a-z0-9-]{3,20}$ ]]; then
            CLIENT_NAME=$new_client_name
            break
        else
            echo "Error: Must be 3-20 lowercase letters, numbers, or hyphens"
        fi
    done

    # Only ask for OpenSearch credentials if NEED_OPENSEARCH is yes
    if [ "$NEED_OPENSEARCH" = "yes" ]; then
        read -p "Enter OpenSearch admin username [${OPENSEARCH_USER}]: " new_opensearch_user
        OPENSEARCH_USER=${new_opensearch_user:-$OPENSEARCH_USER}
        
        # For passwords, always prompt but allow keeping the old value
        read -s -p "Enter OpenSearch admin password (leave empty to keep current): " new_opensearch_password
        echo
        if [ -n "$new_opensearch_password" ]; then
            if validate_password "$new_opensearch_password"; then
                OPENSEARCH_PASSWORD=$new_opensearch_password
            else
                echo "Invalid password format. Keeping existing password."
            fi
        fi
    fi

    # Get NGINX password
    read -s -p "Enter NGINX password (leave empty to keep current): " new_nginx_password
    echo
    if [ -n "$new_nginx_password" ]; then
        if validate_password "$new_nginx_password"; then
            NGINX_PASSWORD=$new_nginx_password
        else
            echo "Invalid password format. Keeping existing password."
        fi
    fi

    # Get Region with current value as default
    while true; do
        read -p "Enter AWS region [${REGION}]: " new_region
        new_region=${new_region:-$REGION}
        if [[ "$new_region" =~ ^[a-z]{2}-[a-z]+-[0-9]{1}$ ]]; then
            REGION=$new_region
            break
        else
            echo "Error: Invalid region format. Please use format like us-east-1"
        fi
    done

    # Save updated environment
    save_environment "$TABLE_SUFFIX"
    
    # If prerequisites are not met, build and push Docker images
    if [ "$PREREQUISITES_MET" = "no" ]; then
        build_and_push_images "$TABLE_SUFFIX" "$REGION"
    fi
    
    # Update CloudFormation stack
    echo -e "\nUpdating CloudFormation stack..."
    aws cloudformation update-stack \
        --stack-name $PROJECT_NAME \
        --template-url "https://flotorch-public.s3.us-east-1.amazonaws.com/${VERSION}/templates/master-template.yaml" \
        --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
        --disable-rollback \
        --region "$REGION" \
        --parameters \
            ParameterKey=PrerequisitesMet,ParameterValue="$PREREQUISITES_MET" \
            ParameterKey=NeedOpensearch,ParameterValue="$NEED_OPENSEARCH" \
            ParameterKey=ProjectName,ParameterValue="$PROJECT_NAME" \
            ParameterKey=TableSuffix,ParameterValue="$TABLE_SUFFIX" \
            ParameterKey=ClientName,ParameterValue="$CLIENT_NAME" \
            ParameterKey=OpenSearchAdminUser,ParameterValue="$OPENSEARCH_USER" \
            ParameterKey=OpenSearchAdminPassword,ParameterValue="$OPENSEARCH_PASSWORD" \
            ParameterKey=NginxAuthPassword,ParameterValue="$NGINX_PASSWORD"

    echo -e "\nUpdate initiated. Check AWS CloudFormation console for progress."
}

# Check if any environments exist
if [ -d ".envs" ] && [ "$(ls -A .envs 2>/dev/null)" ]; then
    echo "Existing environments found."
    while true; do
        read -p "Do you want to create a new environment or update an existing one? (new/update): " ACTION
        if [[ "$ACTION" =~ ^(new|update)$ ]]; then
            break
        else
            echo "Error: Please enter either 'new' or 'update'"
        fi
    done

    if [ "$ACTION" = "update" ]; then
        if list_environments; then
            while true; do
                read -p "Enter the environment suffix to update: " UPDATE_SUFFIX
                if [ -f ".envs/${UPDATE_SUFFIX}.json" ]; then
                    update_environment "$UPDATE_SUFFIX"
                    exit 0
                else
                    echo "Error: Environment ${UPDATE_SUFFIX} not found"
                fi
            done
        fi
    fi
fi

# Collect parameters interactively for new environment
echo "FloTorch Deployment Configuration"
echo "----------------------------------"

# Get Prerequisites confirmation
while true; do
    read -p "Subscribed to FloTorch on AWS Marketplace? (yes/no): " PREREQUISITES_MET
    if [[ "$PREREQUISITES_MET" =~ ^(yes|no)$ ]]; then
        break
    else
        echo "Error: Please enter either 'yes' or 'no'"
    fi
done

# Get OpenSearch confirmation
while true; do
    read -p "Do you need OpenSearch? (yes/no) [yes]: " NEED_OPENSEARCH
    NEED_OPENSEARCH=${NEED_OPENSEARCH:-yes}
    if [[ "$NEED_OPENSEARCH" =~ ^(yes|no)$ ]]; then
        break
    else
        echo "Error: Please enter either 'yes' or 'no'"
    fi
done

VERSION="latest"

# Get Project Name
read -p "Enter Project Name [flotorch]: " PROJECT_NAME
PROJECT_NAME=${PROJECT_NAME:-flotorch}

# Validate Table Suffix
while true; do
    read -p "Enter Table Suffix (exactly 6 lowercase letters): " TABLE_SUFFIX
    if [[ "$TABLE_SUFFIX" =~ ^[a-z]{6}$ ]]; then
        break
    else
        echo "Error: Must contain exactly 6 lowercase letters"
    fi
done

# Validate Client Name
while true; do
    read -p "Enter Client Name [flotorch]: " CLIENT_NAME
    CLIENT_NAME=${CLIENT_NAME:-flotorch}
    if [[ "$CLIENT_NAME" =~ ^[a-z0-9-]{3,20}$ ]]; then
        break
    else
        echo "Error: Must be 3-20 lowercase letters, numbers, or hyphens"
    fi
done

# Only ask for OpenSearch credentials if NEED_OPENSEARCH is yes
OPENSEARCH_USER="admin"
OPENSEARCH_PASSWORD="Flotorch@123"
if [ "$NEED_OPENSEARCH" = "yes" ]; then
    read -p "Enter OpenSearch admin username [admin]: " OPENSEARCH_USER
    OPENSEARCH_USER=${OPENSEARCH_USER:-admin}
    
    # Create OpenSearch service-linked role if needed
    create_opensearch_service_role || {
        echo "Failed to create OpenSearch service-linked role. Please ensure you have sufficient IAM permissions."
        exit 1
    }
    read -s -p "Enter OpenSearch admin password: " OPENSEARCH_PASSWORD
    echo
fi

# Get NGINX password
read -s -p "Enter NGINX password: " NGINX_PASSWORD
echo

# Get Region
while true; do
    read -p "Enter AWS region [us-east-1]: " REGION
    REGION=${REGION:-us-east-1}
    if [[ "$REGION" =~ ^[a-z]{2}-[a-z]+-[0-9]{1}$ ]]; then
        break
    else
        echo "Error: Invalid region format. Please use format like us-east-1"
    fi
done

# Create .envs directory if it doesn't exist
mkdir -p .envs

# Save environment variables to JSON file
save_environment "$TABLE_SUFFIX"

# If prerequisites are not met, build and push Docker images
if [ "$PREREQUISITES_MET" = "no" ]; then
    build_and_push_images "$TABLE_SUFFIX" "$REGION"
fi

# Execute CloudFormation deployment
echo -e "\nStarting CloudFormation deployment..."
aws cloudformation create-stack \
    --stack-name $PROJECT_NAME \
    --template-url "https://flotorch-public.s3.us-east-1.amazonaws.com/${VERSION}/templates/master-template.yaml" \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
    --disable-rollback \
    --region "$REGION" \
    --parameters \
        ParameterKey=PrerequisitesMet,ParameterValue="$PREREQUISITES_MET" \
        ParameterKey=NeedOpensearch,ParameterValue="$NEED_OPENSEARCH" \
        ParameterKey=ProjectName,ParameterValue="$PROJECT_NAME" \
        ParameterKey=TableSuffix,ParameterValue="$TABLE_SUFFIX" \
        ParameterKey=ClientName,ParameterValue="$CLIENT_NAME" \
        ParameterKey=OpenSearchAdminUser,ParameterValue="$OPENSEARCH_USER" \
        ParameterKey=OpenSearchAdminPassword,ParameterValue="$OPENSEARCH_PASSWORD" \
        ParameterKey=NginxAuthPassword,ParameterValue="$NGINX_PASSWORD"

echo -e "\nDeployment initiated. Check AWS CloudFormation console for progress."