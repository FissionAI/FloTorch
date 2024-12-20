FROM public.ecr.aws/lambda/python:3.9

# Create and set working directory
WORKDIR /var/task

# Copy requirements file
COPY cost_handler/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt --target .

# Copy the necessary files and directories
COPY cost_handler/cost_compute_handler.py .
COPY cost_handler/pricing.py .
COPY cost_handler/utils.py .

# Set environment variables
ENV PYTHONPATH=/var/task
ENV PYTHONUNBUFFERED=1

# Set the CMD to your handler
CMD ["cost_compute_handler.lambda_handler"]