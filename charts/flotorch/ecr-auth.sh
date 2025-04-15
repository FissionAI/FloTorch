#!/bin/bash

# Colors for output
YELLOW='\033[0;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${YELLOW}===== Setting up Amazon ECR Authentication =====${NC}"

# Step 1: Get AWS credentials
echo -e "${YELLOW}Getting AWS credentials...${NC}"
AWS_ACCOUNT_ID=677276078734
AWS_REGION=us-east-1

# Step 2: Login to ECR and get the authentication token
echo -e "${YELLOW}Authenticating with AWS ECR...${NC}"
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Step 3: Create a Kubernetes secret with the Docker config
echo -e "${YELLOW}Creating Kubernetes secret for ECR authentication...${NC}"
# Get the docker config file with credentials
DOCKER_CONFIG_FILE="$HOME/.docker/config.json"

# Check if the file exists
if [ ! -f "$DOCKER_CONFIG_FILE" ]; then
    echo "Docker config file does not exist. Please run 'docker login' first."
    exit 1
fi

# Create or update the Kubernetes secret
kubectl create secret generic ecr-credentials \
    --from-file=.dockerconfigjson=$DOCKER_CONFIG_FILE \
    --type=kubernetes.io/dockerconfigjson \
    --dry-run=client -o yaml | kubectl apply -f -

# Step 4: Update service accounts to use the pull secret
echo -e "${YELLOW}Updating default service account to use ECR credentials...${NC}"
kubectl patch serviceaccount default -p '{"imagePullSecrets": [{"name": "ecr-credentials"}]}'

# Step 5: Restart the deployments to use the new credentials
echo -e "${GREEN}Restarting deployments to use the new credentials...${NC}"
kubectl rollout restart deployment console
kubectl rollout restart deployment gateway

# Step 6: Check the status
echo -e "${YELLOW}Checking pod status...${NC}"
kubectl get pods
