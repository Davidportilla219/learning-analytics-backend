#!/bin/bash

# Test script for Learning Analytics Platform
# This script tests the basic infrastructure setup

echo "🚀 Starting Learning Analytics Platform Infrastructure Test..."

# Change to the correct directory
cd "$(dirname "$0")"

echo "📁 Checking directory structure..."
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found"
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "❌ .env file not found"
    exit 1
fi

if [ ! -d "shared" ]; then
    echo "❌ shared directory not found"
    exit 1
fi

echo "✅ Directory structure is correct"

echo "🐳 Testing Docker Compose configuration..."
if ! docker compose config > /dev/null 2>&1; then
    echo "❌ Docker Compose configuration is invalid"
    exit 1
fi

echo "✅ Docker Compose configuration is valid"

echo "📋 Checking required files..."
required_files=(
    "shared/contracts/__init__.py"
    "shared/contracts/events.py"
    "shared/contracts/dtos.py"
    "shared/contracts/enums.py"
    "shared/utils/__init__.py"
    "shared/utils/logging.py"
    "shared/utils/database.py"
    "gateway/Dockerfile"
    "gateway/nginx.conf"
    "gateway/requirements.txt"
    "README.md"
    ".gitignore"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Required file missing: $file"
        exit 1
    fi
done

echo "✅ All required files are present"

echo "🔍 Checking Python syntax for shared contracts..."
cd shared/contracts
for file in *.py; do
    if ! python3 -m py_compile "$file" 2>/dev/null; then
        echo "❌ Python syntax error in $file"
        exit 1
    fi
done
cd ../..

echo "✅ Python syntax is valid"

echo "📊 Testing environment variables..."
if [ ! -f ".env" ]; then
    echo "❌ .env file not found"
    exit 1
fi

# Check if required environment variables are set
required_vars=(
    "DB_HOST"
    "DB_PORT"
    "DB_USER"
    "DB_PASSWORD"
    "RABBITMQ_HOST"
    "RABBITMQ_PORT"
    "RABBITMQ_USER"
    "RABBITMQ_PASSWORD"
    "JWT_SECRET"
    "JWT_ALGORITHM"
    "JWT_EXPIRE_MINUTES"
)

missing_vars=()
for var in "${required_vars[@]}"; do
    if ! grep -q "^$var=" .env; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -gt 0 ]; then
    echo "❌ Missing environment variables: ${missing_vars[*]}"
    exit 1
fi

echo "✅ All required environment variables are set"

echo "🏗️  Infrastructure test completed successfully!"
echo ""
echo "📋 Summary:"
echo "   ✅ Directory structure: OK"
echo "   ✅ Docker Compose: OK"
echo "   ✅ Required files: OK"
echo "   ✅ Python syntax: OK"
echo "   ✅ Environment variables: OK"
echo ""
echo "🚀 You can now run: docker compose up --build"