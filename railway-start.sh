#!/bin/bash

# Learning Analytics Platform - Railway Startup Script
# This script handles Railway-specific deployment logic

set -e

echo "🚆 Starting Learning Analytics Platform on Railway..."

# Wait for database to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
until docker compose -f docker-compose.railway.yml exec -T postgres pg_isready -U postgres; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 2
done

echo "✅ PostgreSQL is ready!"

# Wait for RabbitMQ to be ready
echo "⏳ Waiting for RabbitMQ to be ready..."
until docker compose -f docker-compose.railway.yml exec -T rabbitmq rabbitmq-diagnostics -q ping; do
    echo "RabbitMQ is unavailable - sleeping"
    sleep 2
done

echo "✅ RabbitMQ is ready!"

# Run database migrations if needed
echo "🗃️ Running database migrations..."
for service in auth-service event-service telemetry-processor-service academic-risk-service alert-service; do
    if [ -f "${service}/migrate.sh" ]; then
        echo "🔄 Running migrations for ${service}..."
        docker compose -f docker-compose.railway.yml exec -T ${service} /bin/sh -c "cd /app && ./migrate.sh"
    fi
done

echo "🎯 Starting all services..."
docker compose -f docker-compose.railway.yml up -d

echo "🔍 Verifying services..."
sleep 10

# Health checks
echo "🏥 Running health checks..."
curl -sS http://localhost:8080/health || echo "❌ Gateway health check failed"
curl -sS http://localhost:8080/auth/api/v1/health || echo "❌ Auth service health check failed"
curl -sS http://localhost:8080/event-capture/api/v1/health || echo "❌ Event service health check failed"

echo "🎉 Learning Analytics Platform started successfully!"
echo "📊 Gateway URL: http://localhost:8080"
echo "🐰 RabbitMQ Management: http://localhost:15672 (guest:guest)"