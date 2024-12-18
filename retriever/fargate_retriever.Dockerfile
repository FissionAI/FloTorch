# Use the official AWS Lambda Python 3.9 runtime base image
FROM --platform=linux/amd64 python:3.9-slim

# Create and set the working directory inside the container
WORKDIR /var/task

# Copy the requirements file to the working directory
COPY retriever/requirements.txt .

# Install dependencies into the /var/task directory (where Lambda expects them)
RUN pip install --no-cache-dir -r requirements.txt --target .

# Copy the necessary files and directories
COPY baseclasses/ baseclasses/
COPY config/ config/
COPY core/ core/
COPY retriever/ retriever/
COPY util/ util/
COPY handlers/task_processor.py .
COPY handlers/fargate_retriever_handler.py .
COPY .env .

# Set environment variables
ENV PYTHONPATH=/var/task
ENV PYTHONUNBUFFERED=1

CMD ["python", "fargate_retriever_handler.py"]