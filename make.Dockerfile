# Use the official AWS Lambda Python 3.9 runtime base image
FROM python:3.9-slim as base

# Create and set the working directory inside the container
WORKDIR /var/task

# Copy the requirements file to the working directory
COPY ${BUILD_DIR}/requirements.txt .

# Install dependencies into the /var/task directory (where Lambda expects them)
RUN pip install --no-cache-dir -r requirements.txt --target .

# Copy the necessary files and directories
COPY ${BUILD_DIR}/baseclasses/ baseclasses/
COPY ${BUILD_DIR}/config/ config/
COPY ${BUILD_DIR}/core/ core/
COPY ${BUILD_DIR}/util/ util/
COPY ${BUILD_DIR}/lambda_handlers/ lambda_handlers/
COPY ${BUILD_DIR}/handlers/ handlers/

# Set environment variables
ENV PYTHONPATH=/var/task
ENV PYTHONUNBUFFERED=1

# Lambda runtime will look for the handler function here
CMD ["retriever_handler.lambda_handler"]