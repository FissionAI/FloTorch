# Flotorch Helm Chart Deployment Guide

This guide outlines the steps to deploy the Flotorch application on your RKE Kubernetes cluster using Helm.

## Prerequisites

- A running RKE Kubernetes cluster
- Kubectl configured with access to your cluster
- Helm 3 installed
- Nginx ingress controller already installed

## Deployment Steps

1. Deploy the Flotorch Helm chart:

```bash
# Navigate to the deploy directory
cd /path/to/Flotorch-Enterprise/deploy

# Install the Helm chart
helm upgrade --install flotorch ./flotorch --namespace flotorch --create-namespace
```

2. Verify the deployment:

```bash
# Check the pods
kubectl get pods -n flotorch

# Check the services
kubectl get svc -n flotorch

# Check the ingress resources
kubectl get ingress -n flotorch
```

## Accessing the Applications

- Console: https://console.flotorch.com:30443
- Gateway: https://gateway.flotorch.com:30443

## Notes

- DNS records should be configured to point the domains to your RKE cluster node IP(s)
- If you need to update DNS, add entries in your hosts file for testing:
  ```
  <NODE_IP> console.flotorch.com gateway.flotorch.com
  ```
- The applications are configured to communicate internally using Kubernetes service names

## Customization

To customize the deployment, edit the `values.yaml` file before installing/upgrading.
