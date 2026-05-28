FROM nginx:alpine

RUN apk add --no-cache gettext

COPY gateway/nginx.conf.template /etc/nginx/nginx.conf.template

RUN mkdir -p /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD wget -qO- http://127.0.0.1:${PORT:-80}/health > /dev/null || exit 1

# Substitute PORT at runtime then start nginx
CMD ["/bin/sh", "-c", "envsubst '${PORT}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf && nginx -g 'daemon off;'"]
