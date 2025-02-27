#!/bin/bash
# Create nginx directory if it doesn't exist
mkdir -p /etc/nginx
NGINX_USER="${NGINX_AUTH_USER:-admin}"
NGINX_PASS="${NGINX_AUTH_PASSWORD:-Flotorch@123}"
if [ ! -f /etc/nginx/.htpasswd ] || [ ! -s /etc/nginx/.htpasswd ]; then
    echo "Creating new .htpasswd file with provided credentials"
    htpasswd -cb /etc/nginx/.htpasswd "$NGINX_USER" "$NGINX_PASS"
else
    echo "Updating existing .htpasswd file with new credentials"
    htpasswd -b /etc/nginx/.htpasswd "$NGINX_USER" "$NGINX_PASS"
fi
exec supervisord -n
