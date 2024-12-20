FROM public.ecr.aws/lambda/python:3.9

# Create and set working directory
WORKDIR /var/task

# Copy requirements file
COPY retriever/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt --target .

# Copy the necessary files and directories
COPY baseclasses/ baseclasses/
COPY config/ config/
COPY core/ core/
COPY retriever/ retriever/
COPY util/ util/
COPY lambda_handlers/retriever_handler.py .

# Set environment variables
ENV PYTHONPATH=/var/task
ENV PYTHONUNBUFFERED=1

# Set the CMD to your handler
CMD ["retriever_handler.lambda_handler"]
