FROM nginx:alpine

# envsubst comes with gettext, already included in nginx:alpine
RUN apk add --no-cache gettext

# Copy nginx configuration (internal service discovery, no envsubst needed)
COPY gateway/nginx.conf.template /etc/nginx/nginx.conf

# Keep the local docker-compose config available as fallback reference
COPY gateway/nginx.conf /etc/nginx/nginx.conf.local

RUN mkdir -p /usr/share/nginx/html

EXPOSE ${PORT:-80}

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD wget -qO- http://127.0.0.1:${PORT:-80}/health > /dev/null || exit 1

# Start nginx directly (internal service discovery configured)
CMD ["nginx", "-g", "daemon off;"]
