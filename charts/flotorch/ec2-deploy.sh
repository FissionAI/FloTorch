#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Uninstall the existing Helm release
echo -e "${YELLOW}Uninstalling existing Helm release...${NC}"
helm uninstall flotorch || true

# Wait for resources to be cleaned up
echo -e "${YELLOW}Waiting for resources to be cleaned up...${NC}"
sleep 10

# Delete all PVCs and PVs
echo -e "${YELLOW}Deleting any stuck PVCs and PVs...${NC}"
kubectl delete pvc --all || true
kubectl delete pv --all || true
sleep 5

# Step 2: Create the necessary directories directly on the EC2 instance
echo -e "${YELLOW}Creating directories on the EC2 host...${NC}"
sudo mkdir -p /mnt/data/redis /mnt/data/clickhouse-data /mnt/data/clickhouse-logs /mnt/data/postgres
sudo chmod -R 777 /mnt/data
echo -e "${GREEN}Directories created with permissions:${NC}"
ls -la /mnt/data

# Step 3: Install the Helm chart with debug output
echo -e "${YELLOW}Installing Flotorch Helm chart...${NC}"
helm upgrade --install flotorch . --debug --timeout 10m

# Step 4: Display deployment status
echo -e "${YELLOW}Checking initial deployment status...${NC}"
sleep 15

echo -e "${YELLOW}Persistent Volumes:${NC}"
kubectl get pv

echo -e "${YELLOW}Persistent Volume Claims:${NC}"
kubectl get pvc

echo -e "${YELLOW}Pods:${NC}"
kubectl get pods

echo -e "${GREEN}===== Deployment Instructions =====${NC}"
echo -e "1. If pods are still pending, check events with: ${YELLOW}kubectl describe pod <pod-name>${NC}"
echo -e "2. To check logs: ${YELLOW}kubectl logs <pod-name>${NC}"
echo -e "3. After all pods are running, access your application at:"
echo -e "   Console: ${GREEN}https://console.flotorch.com:30443${NC}"
echo -e "   Gateway: ${GREEN}https://gateway.flotorch.com:30443${NC}"
