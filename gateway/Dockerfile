FROM nginx:alpine

# envsubst comes with gettext, already included in nginx:alpine
RUN apk add --no-cache gettext

# Copy the template — envsubst fills in the real URLs at container start
COPY gateway/nginx.conf.template /etc/nginx/nginx.conf.template

# Keep the local docker-compose config available as fallback reference
COPY gateway/nginx.conf /etc/nginx/nginx.conf.local

RUN mkdir -p /usr/share/nginx/html

EXPOSE ${PORT:-80}

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD wget -qO- http://127.0.0.1:${PORT:-80}/health > /dev/null || exit 1

# At startup: substitute env vars into the template, then launch nginx
CMD ["/bin/sh", "-c", \
    "envsubst '${AUTH_SERVICE_URL} ${EVENT_SERVICE_URL} ${TELEMETRY_SERVICE_URL} ${RISK_SERVICE_URL} ${ALERT_SERVICE_URL} ${PORT}' \
    < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf && \
    nginx -g 'daemon off;'"]
