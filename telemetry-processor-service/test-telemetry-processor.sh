#!/bin/bash

# Test script for Telemetry Processor Service
# This script runs comprehensive tests for the telemetry processor

set -e

echo "🚀 Starting Telemetry Processor Service tests..."

# Function to check if a service is healthy
check_health() {
    local service_url=$1
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$service_url/health" > /dev/null 2>&1; then
            echo "✅ $service_url is healthy"
            return 0
        fi
        echo "⏳ Waiting for $service_url... (attempt $attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_url failed to become healthy"
    return 1
}

# Function to test an endpoint
test_endpoint() {
    local method=$1
    local url=$2
    local data=$3
    local expected_status=$4
    
    echo "🧪 Testing $method $url..."
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "%{http_code}" "$url" -o /tmp/response.json 2>/dev/null)
    else
        response=$(curl -s -w "%{http_code}" -X "$method" -H "Content-Type: application/json" -d "$data" "$url" -o /tmp/response.json 2>/dev/null)
    fi
    
    if [ "$response" = "$expected_status" ]; then
        echo "✅ $method $url returned $expected_status"
        if [ -f /tmp/response.json ]; then
            echo "📄 Response: $(cat /tmp/response.json)"
        fi
        return 0
    else
        echo "❌ $method $url returned $response (expected $expected_status)"
        if [ -f /tmp/response.json ]; then
            echo "📄 Response: $(cat /tmp/response.json)"
        fi
        return 1
    fi
}

# Function to test event processing
test_event_processing() {
    echo "🧪 Testing event processing..."
    
    # Test event data
    local event_data='{
        "event_id": "telemetry-test-001",
        "event_type": "login",
        "user_id": "user-001",
        "timestamp": "2024-01-01T10:00:00Z",
        "data": {
            "ip_address": "192.168.1.1",
            "user_agent": "Mozilla/5.0"
        }
    }'
    
    # Test event processing endpoint
    if test_endpoint "POST" "http://localhost:8080/telemetry-processor/api/v1/events/process" "$event_data" "201"; then
        echo "✅ Event processing test passed"
        return 0
    else
        echo "❌ Event processing test failed"
        return 1
    fi
}

# Function to test batch processing
test_batch_processing() {
    echo "🧪 Testing batch event processing..."
    
    # Test batch event data
    local batch_data='{
        "events": [
            {
                "event_id": "telemetry-batch-001",
                "event_type": "page_view",
                "user_id": "user-001",
                "timestamp": "2024-01-01T10:05:00Z",
                "data": {
                    "page": "/dashboard",
                    "duration": 30
                }
            },
            {
                "event_id": "telemetry-batch-002",
                "event_type": "assignment_view",
                "user_id": "user-001",
                "timestamp": "2024-01-01T10:10:00Z",
                "data": {
                    "assignment_id": "assignment-001",
                    "title": "Math Assignment"
                }
            }
        ]
    }'
    
    # Test batch processing endpoint
    if test_endpoint "POST" "http://localhost:8080/telemetry-processor/api/v1/events/batch-process" "$batch_data" "201"; then
        echo "✅ Batch processing test passed"
        return 0
    else
        echo "❌ Batch processing test failed"
        return 1
    fi
}

# Function to test risk assessment
test_risk_assessment() {
    echo "🧪 Testing risk assessment..."
    
    # Test high-risk event (quiz with low score)
    local high_risk_event='{
        "event_id": "telemetry-risk-001",
        "event_type": "quiz_submit",
        "user_id": "user-001",
        "timestamp": "2024-01-01T10:15:00Z",
        "data": {
            "quiz_id": "quiz-001",
            "score": 0.2,
            "max_score": 100,
            "time_spent": 300
        }
    }'
    
    # Test event processing with risk assessment
    if test_endpoint "POST" "http://localhost:8080/telemetry-processor/api/v1/events/process" "$high_risk_event" "201"; then
        echo "✅ Risk assessment test passed"
        return 0
    else
        echo "❌ Risk assessment test failed"
        return 1
    fi
}

# Function to test statistics
test_statistics() {
    echo "🧪 Testing statistics endpoint..."
    
    if test_endpoint "GET" "http://localhost:8080/telemetry-processor/api/v1/events/stats" "" "200"; then
        echo "✅ Statistics test passed"
        return 0
    else
        echo "❌ Statistics test failed"
        return 1
    fi
}

# Main test execution
main() {
    echo "🔍 Starting comprehensive Telemetry Processor Service tests..."
    
    # Check if service is healthy
    if ! check_health "http://localhost:8080/telemetry-processor"; then
        echo "❌ Telemetry Processor Service is not healthy"
        exit 1
    fi
    
    # Run tests
    local tests_passed=0
    local tests_total=5
    
    # Test individual endpoints
    if test_endpoint "GET" "http://localhost:8080/telemetry-processor/api/v1/health" "" "200"; then
        tests_passed=$((tests_passed + 1))
    fi
    
    if test_endpoint "GET" "http://localhost:8080/telemetry-processor/api/v1/health/database" "" "200"; then
        tests_passed=$((tests_passed + 1))
    fi
    
    if test_endpoint "GET" "http://localhost:8080/telemetry-processor/api/v1/health/full" "" "200"; then
        tests_passed=$((tests_passed + 1))
    fi
    
    # Test processing endpoints
    if test_event_processing; then
        tests_passed=$((tests_passed + 1))
    fi
    
    if test_batch_processing; then
        tests_passed=$((tests_passed + 1))
    fi
    
    if test_risk_assessment; then
        tests_passed=$((tests_passed + 1))
    fi
    
    if test_statistics; then
        tests_passed=$((tests_passed + 1))
    fi
    
    # Summary
    echo ""
    echo "📊 Test Summary:"
    echo "   Tests passed: $tests_passed/$tests_total"
    
    if [ $tests_passed -eq $tests_total ]; then
        echo "🎉 All tests passed!"
        exit 0
    else
        echo "❌ Some tests failed!"
        exit 1
    fi
}

# Run main function
main