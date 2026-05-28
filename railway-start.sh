#!/bin/bash

# Learning Analytics Platform - Railway Startup Script
# This script handles the dynamic URLs provided by Railway service discovery

echo "🚀 Starting Learning Analytics API Gateway..."

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."

# Function to check if a service is available
check_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s --head "$url" > /dev/null 2>&1; then
            echo "✅ $service_name is ready"
            return 0
        fi
        echo "⏳ Waiting for $service_name... ($attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_name is not ready after $max_attempts attempts"
    return 1
}

# Check all services
echo "🔍 Checking service availability..."

# Railway provides these URLs dynamically
AUTH_SERVICE_URL="${AUTH_SERVICE_URL:-http://localhost:8001}"
EVENT_SERVICE_URL="${EVENT_SERVICE_URL:-http://localhost:8002}"
TELEMETRY_SERVICE_URL="${TELEMETRY_SERVICE_URL:-http://localhost:8003}"
RISK_SERVICE_URL="${RISK_SERVICE_URL:-http://localhost:8004}"
ALERT_SERVICE_URL="${ALERT_SERVICE_URL:-http://localhost:8005}"

echo "📡 Service URLs:"
echo "   Auth: $AUTH_SERVICE_URL"
echo "   Event: $EVENT_SERVICE_URL"
echo "   Telemetry: $TELEMETRY_SERVICE_URL"
echo "   Risk: $RISK_SERVICE_URL"
echo "   Alert: $ALERT_SERVICE_URL"

# Check services (optional - can be disabled for faster startup)
# check_service "$AUTH_SERVICE_URL" "Auth Service"
# check_service "$EVENT_SERVICE_URL" "Event Service"
# check_service "$TELEMETRY_SERVICE_URL" "Telemetry Service"
# check_service "$RISK_SERVICE_URL" "Risk Service"
# check_service "$ALERT_SERVICE_URL" "Alert Service"

echo "🚀 Starting API Gateway..."

# Start the gateway with all environment variables
export AUTH_SERVICE_URL="$AUTH_SERVICE_URL"
export EVENT_SERVICE_URL="$EVENT_SERVICE_URL"
export TELEMETRY_SERVICE_URL="$TELEMETRY_SERVICE_URL"
export RISK_SERVICE_URL="$RISK_SERVICE_URL"
export ALERT_SERVICE_URL="$ALERT_SERVICE_URL"

# Start the gateway
npm run start:gateway