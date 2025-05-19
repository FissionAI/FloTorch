# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install FloTorch-core
RUN pip install FloTorch-core

# Copy the application code
COPY fargate/ fargate/
COPY fargate/handler/cost_compute/fargate_cost_compute_handler.py .

# Set environment variables (these can be overridden at runtime)
ENV experiment_table=your_experiment_table_name
ENV experiment_question_metrics_table=your_experiment_question_metrics_table_name
ENV experiment_question_metrics_index=your_experiment_question_metrics_index_name
ENV bedrock_limit_csv=your_bedrock_limit_csv_file
ENV s3_bucket=your_s3_bucket_name
ENV AWS_REGION=your_aws_region 
ENV AWS_ACCESS_KEY_ID=your_aws_access_key_id
ENV AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
ENV AWS_SESSION_TOKEN=your_aws_session_token
ENV AWS_DEFAULT_REGION=your_aws_default_region
ENV db_type=type_of_your_database

# Command to run the main application
CMD ["python", "fargate_cost_compute_handler.py"]