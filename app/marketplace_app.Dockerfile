FROM 709825985650.dkr.ecr.us-east-1.amazonaws.com/fission-labs/flotorch-app:1.0.0

WORKDIR /app
COPY .env app/.env
ENV PYTHONPATH=/app

# Add build argument for the password
ARG BASIC_AUTH_PASSWORD
RUN test -n "$BASIC_AUTH_PASSWORD" || (echo "BASIC_AUTH_PASSWORD build argument is required" && false)

# Create htpasswd file with provided password
RUN htpasswd -cb /etc/nginx/.htpasswd admin "${BASIC_AUTH_PASSWORD}"

CMD ["sh", "-c", "nginx -g 'daemon off;' & uvicorn app.main:app --host 0.0.0.0 --port 8000"]