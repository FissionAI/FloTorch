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
RUN npm install -g corepack@latest
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

# Copy the entrypoint script and supervisor config
COPY app/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
COPY app/supervisor/flotorch.conf /etc/supervisor/conf.d/flotorch.conf

ENTRYPOINT ["/app/entrypoint.sh"]
