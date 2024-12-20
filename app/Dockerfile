FROM python:3.9-slim AS base
WORKDIR /app
RUN apt-get update
COPY app/requirements.txt app/requirements.txt
RUN pip install --no-cache-dir -r app/requirements.txt
COPY app/ app/
COPY core/ core/
COPY baseclasses/ baseclasses/
COPY config/ config/
COPY util/ util/
COPY constants/ constants/
ENV PYTHONPATH=/app
ENV NGINX_AUTH_PASSWORD=Flotorch@123

FROM node:22 AS uibuilder
RUN corepack enable pnpm
WORKDIR /app/
COPY ui/ /app/ui/
WORKDIR /app/ui
RUN pnpm install && pnpm run generate

FROM base AS release
WORKDIR /app

# Install required packages
RUN apt-get update && apt-get install -y \
    nginx \
    apache2-utils \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy UI files and configure nginx
COPY --from=uibuilder /app/ui/dist /usr/share/nginx/html
RUN rm -rf /etc/nginx/conf.d/default.conf
RUN rm -rf /etc/nginx/sites-enabled/default
COPY app/nginx /etc/nginx

# Create directory for supervisor configs
RUN mkdir -p /etc/supervisor/conf.d

# Create entrypoint script
COPY <<EOF /app/entrypoint.sh
#!/bin/bash

# Create nginx directory if it doesn't exist
mkdir -p /etc/nginx

NGINX_USER="\${NGINX_AUTH_USER:-admin}"
NGINX_PASS="\${NGINX_AUTH_PASSWORD:-Flotorch@123}"

if [ ! -f /etc/nginx/.htpasswd ] || [ ! -s /etc/nginx/.htpasswd ]; then
    echo "Creating new .htpasswd file with provided credentials"
    htpasswd -cb /etc/nginx/.htpasswd "\$NGINX_USER" "\$NGINX_PASS"
else
    echo "Updating existing .htpasswd file with new credentials"
    htpasswd -b /etc/nginx/.htpasswd "\$NGINX_USER" "\$NGINX_PASS"
fi

exec supervisord -n
EOF

RUN chmod +x /app/entrypoint.sh

COPY <<EOF /etc/supervisor/conf.d/flotorch.conf
[supervisord]
nodaemon=true

[program:nginx]
command=nginx -g "daemon off;"
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0

[program:uvicorn]
command=uvicorn app.main:app --host 0.0.0.0 --port 8000
directory=/app
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
EOF

ENTRYPOINT ["/app/entrypoint.sh"]
