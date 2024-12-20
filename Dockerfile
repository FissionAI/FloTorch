# Use Amazon Linux 2023 as base image
FROM amazonlinux:2023

# Install system dependencies in stages to handle package conflicts properly
RUN dnf update -y && \
    dnf clean all

# Install basic build tools first
RUN dnf install -y \
    gcc-c++ \
    make \
    shadow-utils \
    openssl \
    openssl-devel \
    && dnf clean all

# Install Python and development tools
RUN dnf install -y \
    python3 \
    python3-pip \
    git \
    && dnf clean all

# Install compression tools
RUN dnf install -y \
    tar \
    gzip \
    unzip \
    && dnf clean all

# Install jq
RUN dnf install -y \
    jq && \
    dnf clean all

# Install Docker and required dependencies
RUN dnf install -y docker iptables procps && \
    dnf clean all

# Create necessary directories with proper permissions
RUN mkdir -p /run/docker && \
    mkdir -p /var/lib/docker && \
    mkdir -p /etc/docker

# Configure Docker daemon
RUN echo '{"storage-driver": "vfs"}' > /etc/docker/daemon.json

# Install Node.js and npm using nvm
ENV NVM_DIR=/root/.nvm
ENV NODE_VERSION=22.12.0

RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash && \
    . $NVM_DIR/nvm.sh && \
    nvm install $NODE_VERSION && \
    nvm alias default $NODE_VERSION && \
    nvm use default

# Add node and npm to path so the commands are available
ENV NODE_PATH $NVM_DIR/v$NODE_VERSION/lib/node_modules
ENV PATH $NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH

# Verify Node.js and npm versions
RUN node -v && npm -v

# Install AWS CLI v2
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf aws awscliv2.zip

# Install AWS CDK globally
RUN npm install -g aws-cdk && \
    cdk --version

# Set working directory
WORKDIR /FloTorch

# Copy the entire FloTorch directory
COPY . .

# Make deploy.sh executable
RUN chmod +x /FloTorch/cdk/deploy.sh

# Install required Python packages
RUN pip3 install -r cdk/requirements.txt --upgrade

# Create the entrypoint script
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'set -e' >> /entrypoint.sh && \
    echo '' >> /entrypoint.sh && \
    echo '# Start Docker daemon if not running' >> /entrypoint.sh && \
    echo 'if ! pgrep dockerd >/dev/null 2>&1; then' >> /entrypoint.sh && \
    echo '    echo "Starting Docker daemon..."' >> /entrypoint.sh && \
    echo '    dockerd --host=unix:///var/run/docker.sock --host=tcp://0.0.0.0:2375 --storage-driver=vfs &' >> /entrypoint.sh && \
    echo '    echo "Waiting for Docker daemon to start..."' >> /entrypoint.sh && \
    echo '    for i in $(seq 1 30); do' >> /entrypoint.sh && \
    echo '        if docker info >/dev/null 2>&1; then' >> /entrypoint.sh && \
    echo '            echo "Docker daemon started successfully"' >> /entrypoint.sh && \
    echo '            break' >> /entrypoint.sh && \
    echo '        fi' >> /entrypoint.sh && \
    echo '        echo "Waiting for Docker daemon... ($i/30)"' >> /entrypoint.sh && \
    echo '        sleep 1' >> /entrypoint.sh && \
    echo '    done' >> /entrypoint.sh && \
    echo 'fi' >> /entrypoint.sh && \
    echo '' >> /entrypoint.sh && \
    echo '# Print environment for debugging' >> /entrypoint.sh && \
    echo 'echo "AWS credentials setup..."' >> /entrypoint.sh && \
    echo 'aws configure list' >> /entrypoint.sh && \
    echo '' >> /entrypoint.sh && \
    echo '# Verify required environment variables' >> /entrypoint.sh && \
    echo 'if [ -z "${AWS_ACCOUNT_ID}" ] || [ -z "${AWS_DEFAULT_REGION}" ]; then' >> /entrypoint.sh && \
    echo '    echo "Error: AWS_ACCOUNT_ID and AWS_DEFAULT_REGION must be provided"' >> /entrypoint.sh && \
    echo '    exit 1' >> /entrypoint.sh && \
    echo 'fi' >> /entrypoint.sh && \
    echo '' >> /entrypoint.sh && \
    echo '# Run deployment with verbose output' >> /entrypoint.sh && \
    echo 'cd /FloTorch/cdk' >> /entrypoint.sh && \
    echo 'echo "Starting deployment process..."' >> /entrypoint.sh && \
    echo 'echo "Using AWS Account: ${AWS_ACCOUNT_ID}"' >> /entrypoint.sh && \
    echo 'echo "Using AWS Region: ${AWS_DEFAULT_REGION}"' >> /entrypoint.sh && \
    echo './deploy.sh' >> /entrypoint.sh && \
    echo 'echo "Deployment completed."' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]
