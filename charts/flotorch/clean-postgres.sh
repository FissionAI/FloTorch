#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}===== Clean PostgreSQL Resources =====${NC}"

# Step 1: Delete PostgreSQL Deployment and Service
echo -e "${YELLOW}Deleting PostgreSQL deployment and service...${NC}"
kubectl delete deployment postgres
kubectl delete service postgres

# Step 2: Delete PostgreSQL PVC
echo -e "${YELLOW}Deleting PostgreSQL PVC...${NC}"
kubectl delete pvc postgres-data-pvc

# Step 3: Delete PostgreSQL PV
echo -e "${YELLOW}Deleting PostgreSQL PV...${NC}"
kubectl delete pv flotorch-postgres-data-pv

# Step 4: Delete the corresponding directory on the host (adjust path if needed)
echo -e "${YELLOW}Removing PostgreSQL data directory on host...${NC}"
sudo rm -rf /mnt/data/postgres

# Step 5: Recreate the directory with proper permissions
echo -e "${YELLOW}Recreating PostgreSQL data directory...${NC}"
sudo mkdir -p /mnt/data/postgres
sudo chmod -R 777 /mnt/data/postgres

# Step 6: Reinstall the chart
echo -e "${GREEN}Reinstalling Flotorch chart...${NC}"
helm upgrade --install flotorch . --debug

# Step 7: Monitor the pods
echo -e "${YELLOW}Monitoring pod status...${NC}"
kubectl get pods -w
