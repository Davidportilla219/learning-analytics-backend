#!/bin/bash

# Test script for Event Service
# This script tests the basic structure and configuration of the Event Service

echo "🚀 Starting Event Service Test..."

# Change to the correct directory
cd "$(dirname "$0")"

echo "📁 Checking directory structure..."
if [ ! -f "app/main.py" ]; then
    echo "❌ app/main.py not found"
    exit 1
fi

if [ ! -f "app/core/config.py" ]; then
    echo "❌ app/core/config.py not found"
    exit 1
fi

if [ ! -f "app/models/event.py" ]; then
    echo "❌ app/models/event.py not found"
    exit 1
fi

if [ ! -f "app/database.py" ]; then
    echo "❌ app/database.py not found"
    exit 1
fi

if [ ! -f "app/api/endpoints/events.py" ]; then
    echo "❌ app/api/endpoints/events.py not found"
    exit 1
fi

if [ ! -f "app/api/endpoints/health.py" ]; then
    echo "❌ app/api/endpoints/health.py not found"
    exit 1
fi

if [ ! -f "app/services/event_processor.py" ]; then
    echo "❌ app/services/event_processor.py not found"
    exit 1
fi

if [ ! -f "Dockerfile" ]; then
    echo "❌ Dockerfile not found"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found"
    exit 1
fi

echo "✅ Directory structure is correct"

echo "🔍 Checking Python syntax..."
for file in app/*.py app/**/*.py; do
    if [ -f "$file" ]; then
        if ! python3 -m py_compile "$file" 2>/dev/null; then
            echo "❌ Python syntax error in $file"
            exit 1
        fi
    fi
done

echo "✅ Python syntax is valid"

echo "📋 Checking required files..."
required_files=(
    "tests/conftest.py"
    "tests/test_events.py"
    "tests/test_models.py"
    "tests/test_processor.py"
    "tests/__init__.py"
    "pytest.ini"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Required test file missing: $file"
        exit 1
    fi
done

echo "✅ All required test files are present"

echo "📊 Testing basic functionality..."
# Test if we can import the main module
if ! python3 -c "import sys; sys.path.append('.'); from app.main import app; print('Main module imported successfully')" 2>/dev/null; then
    echo "❌ Cannot import main module"
    exit 1
fi

echo "✅ Basic functionality test passed"

echo "🏗️  Event Service test completed successfully!"
echo ""
echo "📋 Summary:"
echo "   ✅ Directory structure: OK"
echo "   ✅ Python syntax: OK"
echo "   ✅ Required files: OK"
echo "   ✅ Test files: OK"
echo "   ✅ Basic functionality: OK"
echo ""
echo "🚀 You can now run: docker compose up --build"
echo ""
echo "📝 To run tests (after installing dependencies):"
echo "   pip install -r requirements.txt"
echo "   pytest tests/ -v"
echo ""
echo "🔗 API Endpoints:"
echo "   • GET  /api/v1/health - Health check"
echo "   • GET  /api/v1/health/database - Database health"
echo "   • GET  /api/v1/health/rabbitmq - RabbitMQ health"
echo "   • GET  /api/v1/health/full - Full health check"
echo "   • POST /api/v1/events - Create single event"
echo "   • POST /api/v1/events/batch - Create multiple events"
echo "   • GET  /api/v1/events/{event_id} - Get specific event"
echo "   • GET  /api/v1/events - Get events with filters"
echo "   • GET  /api/v1/events/stats - Get event statistics"
echo "   • DELETE /api/v1/events/{event_id} - Delete event"
echo "   • GET  /api/v1/events/health - Events health check"
echo ""
echo "📚 Event Types Supported:"
echo "   • login, logout, page_view, video_play, video_pause"
echo "   • assignment_view, assignment_submit, quiz_start, quiz_submit"
echo "   • forum_post, forum_reply, resource_download, search"
echo "   • navigation, assessment, completion"