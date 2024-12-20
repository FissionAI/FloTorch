# Use the official AWS Lambda Python 3.9 runtime base image
FROM --platform=linux/amd64 public.ecr.aws/lambda/python:3.9

# Create and set the working directory inside the container
WORKDIR /var/task

# Copy the requirements file to the working directory
COPY opensearch/opensearch_requirements.txt ./requirements.txt

# Install dependencies into the /var/task directory (where Lambda expects them)
RUN pip install --no-cache-dir -r requirements.txt --target .

# Copy the necessary files and directories
COPY baseclasses/ baseclasses/
COPY config/ config/
COPY core/ core/
COPY util/ util/
COPY opensearch/ opensearch/
COPY lambda_handlers/opensearch_handler.py .

# Set environment variables
ENV PYTHONPATH=/var/task
ENV PYTHONUNBUFFERED=1

# Lambda runtime will look for the handler function here
CMD ["opensearch_handler.lambda_handler"]
