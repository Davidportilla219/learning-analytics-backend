#!/bin/bash

# Comprehensive test suite for Learning Analytics Platform
# Tests all microservices and their endpoints

set -e

BASE_URL="http://localhost:8080"
SERVICE_PORTS=(
    "auth:8000"
    "event-capture:8002" 
    "telemetry-processor:8003"
    "academic-risk:8004"
    "alert:8005"
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Helper functions
log_test() {
    echo -e "${YELLOW}[TEST $TOTAL_TESTS]${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓ PASSED${NC} $1"
    ((PASSED_TESTS++))
}

log_error() {
    echo -e "${RED}✗ FAILED${NC} $1"
    ((FAILED_TESTS++))
}

test_endpoint() {
    local name="$1"
    local url="$2"
    local expected_status="${3:-200}"
    local method="${4:-GET}"
    local data="$5"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    log_test "$name"
    
    if [ "$method" = "POST" ] && [ -n "$data" ]; then
        response=$(curl -s -w "%{http_code}" -X POST -H "Content-Type: application/json" -d "$data" "$url")
    else
        response=$(curl -s -w "%{http_code}" "$url")
    fi
    
    status_code="${response: -3}"
    response_body="${response%???}"
    
    if [ "$status_code" = "$expected_status" ]; then
        log_success "$name (Status: $status_code)"
        echo "Response: $response_body"
    else
        log_error "$name (Expected: $expected_status, Got: $status_code)"
        echo "Response: $response_body"
    fi
}

test_service_health() {
    local service_name="$1"
    local port="$2"
    
    echo "=== Testing $service_name Health ==="
    
    # Test direct service health
    test_endpoint "Direct Health Check" "http://localhost:$port/health" "200"
    
    # Test gateway routing
    test_endpoint "Gateway Health Check" "$BASE_URL/$service_name/health" "200"
    
    # Test API health endpoint
    test_endpoint "API Health Check" "$BASE_URL/$service_name/api/v1/health" "200"
}

echo "Starting Learning Analytics Platform Test Suite"
echo "=================================================="

# Test 1: Gateway Health
echo -e "\n${YELLOW}=== Phase 1: Gateway Tests ===${NC}"
test_endpoint "Gateway Root" "$BASE_URL/" "200"
test_endpoint "Gateway Health" "$BASE_URL/health" "200"

# Test 2: Auth Service
echo -e "\n${YELLOW}=== Phase 2: Auth Service Tests ===${NC}"
test_service_health "auth" "8000"

test_endpoint "User Login" "$BASE_URL/auth/api/v1/users/login" "200" "POST" '{"username":"testuser","password":"testpass"}'
test_endpoint "User Registration" "$BASE_URL/auth/api/v1/users/register" "201" "POST" '{"username":"testuser","password":"testpass","email":"test@example.com"}'
test_endpoint "Token Validation" "$BASE_URL/auth/api/v1/token/validate" "200" "POST" '{"token":"test-token"}'

# Test 3: Event Capture Service
echo -e "\n${YELLOW}=== Phase 3: Event Capture Service Tests ===${NC}"
test_service_health "event-capture" "8002"

test_endpoint "Create Single Event" "$BASE_URL/event-capture/api/v1/events" "201" "POST" '{
    "event_id": "test-event-001",
    "event_type": "login",
    "user_id": "user-001",
    "timestamp": "2026-05-27T15:05:00",
    "data": {"ip_address": "192.168.1.1"},
    "event_metadata": {"device": "desktop"}
}'

test_endpoint "Create Batch Events" "$BASE_URL/event-capture/api/v1/events/batch" "201" "POST" '{
    "events": [
        {
            "event_id": "test-event-002",
            "event_type": "page_view",
            "user_id": "user-001",
            "timestamp": "2026-05-27T15:05:00",
            "data": {"page": "/dashboard"}
        },
        {
            "event_id": "test-event-003",
            "event_type": "assignment_submit",
            "user_id": "user-001",
            "timestamp": "2026-05-27T15:05:00",
            "data": {"assignment_id": "assign-001"}
        }
    ]
}'

test_endpoint "Get Events" "$BASE_URL/event-capture/api/v1/events" "200"
test_endpoint "Get Event by ID" "$BASE_URL/event-capture/api/v1/events/test-event-001" "200"
test_endpoint "Get Event Stats" "$BASE_URL/event-capture/api/v1/events/stats" "200"

# Test 4: Telemetry Processor Service
echo -e "\n${YELLOW}=== Phase 4: Telemetry Processor Service Tests ===${NC}"
test_service_health "telemetry-processor" "8003"

test_endpoint "Process Event" "$BASE_URL/telemetry-processor/api/v1/events/process" "200" "POST" '{
    "event_id": "processed-event-001",
    "event_type": "login",
    "user_id": "user-001",
    "timestamp": "2026-05-27T15:05:00",
    "data": {"ip_address": "192.168.1.1"},
    "event_metadata": {"device": "desktop"}
}'

test_endpoint "Get Processed Events" "$BASE_URL/telemetry-processor/api/v1/events" "200"
test_endpoint "Get Processing Stats" "$BASE_URL/telemetry-processor/api/v1/events/stats" "200"

# Test 5: Academic Risk Service
echo -e "\n${YELLOW}=== Phase 5: Academic Risk Service Tests ===${NC}"
test_service_health "academic-risk" "8004"

test_endpoint "Assess Risk" "$BASE_URL/academic-risk/api/v1/risk/assess?user_id=user-001" "200"
test_endpoint "Get User Risk Profile" "$BASE_URL/academic-risk/api/v1/risk/profile/user-001" "200"
test_endpoint "Get Users at Risk" "$BASE_URL/academic-risk/api/v1/risk/users" "200"
test_endpoint "Get Risk Alerts" "$BASE_URL/academic-risk/api/v1/risk/alerts" "200"
test_endpoint "Get Risk Statistics" "$BASE_URL/academic-risk/api/v1/risk/stats" "200"

# Test 6: Alert Service
echo -e "\n${YELLOW}=== Phase 6: Alert Service Tests ===${NC}"
test_service_health "alert" "8005"

test_endpoint "Create Alert" "$BASE_URL/alert/api/v1/alerts" "201" "POST" '{
    "alert_id": "alert-001",
    "user_id": "user-001",
    "risk_score": 0.75,
    "risk_level": "high",
    "alert_type": "academic_risk",
    "message": "Student at high risk",
    "timestamp": "2026-05-27T15:05:00"
}'

test_endpoint "Get Alerts" "$BASE_URL/alert/api/v1/alerts" "200"
test_endpoint "Get Alert by ID" "$BASE_URL/alert/api/v1/alerts/alert-001" "200"
test_endpoint "Acknowledge Alert" "$BASE_URL/alert/api/v1/alerts/alert-001/acknowledge" "200" "POST"
test_endpoint "Resolve Alert" "$BASE_URL/alert/api/v1/alerts/alert-001/resolve" "200" "POST"
test_endpoint "Get Alert Statistics" "$BASE_URL/alert/api/v1/alerts/stats" "200"

# Test 7: Error Handling
echo -e "\n${YELLOW}=== Phase 7: Error Handling Tests ===${NC}"

test_endpoint "Invalid Event Type" "$BASE_URL/event-capture/api/v1/events" "422" "POST" '{
    "event_id": "invalid-event",
    "event_type": "invalid_type",
    "user_id": "user-001",
    "timestamp": "2026-05-27T15:05:00"
}'

test_endpoint "Missing Required Fields" "$BASE_URL/auth/api/v1/users/login" "422" "POST" '{"username":"testuser"}'

test_endpoint "Non-existent Event" "$BASE_URL/event-capture/api/v1/events/non-existent" "404"

test_endpoint "Invalid User ID" "$BASE_URL/academic-risk/api/v1/risk/profile/invalid-user" "404"

# Test 8: Performance Tests
echo -e "\n${YELLOW}=== Phase 8: Performance Tests ===${NC}"

echo "Testing concurrent requests..."
for i in {1..5}; do
    test_endpoint "Concurrent Request $i" "$BASE_URL/health" "200" &
done
wait

echo "Testing bulk event creation..."
bulk_data='{"events": ['
for i in {1..10}; do
    bulk_data+='{
        "event_id": "bulk-event-'$i'",
        "event_type": "page_view",
        "user_id": "user-001",
        "timestamp": "2026-05-27T15:05:00",
        "data": {"page": "/page-'$i'"}
    },'
done
bulk_data=${bulk_data%,}
bulk_data+=']}'

test_endpoint "Bulk Event Creation" "$BASE_URL/event-capture/api/v1/events/batch" "201" "POST" "$bulk_data"

# Test 9: Database Integration Tests
echo -e "\n${YELLOW}=== Phase 9: Database Integration Tests ===${NC}"

# Test that events are stored and retrieved
test_endpoint "Store Event" "$BASE_URL/event-capture/api/v1/events" "201" "POST" '{
    "event_id": "db-test-event",
    "event_type": "login",
    "user_id": "db-test-user",
    "timestamp": "2026-05-27T15:05:00",
    "data": {"ip_address": "192.168.1.1"}
}'

test_endpoint "Retrieve Stored Event" "$BASE_URL/event-capture/api/v1/events/db-test-event" "200"

# Test 10: Cross-Service Communication
echo -e "\n${YELLOW}=== Phase 10: Cross-Service Communication Tests ===${NC}"

# Create an event that should trigger risk assessment
test_endpoint "Create Event for Risk Assessment" "$BASE_URL/event-capture/api/v1/events" "201" "POST" '{
    "event_id": "risk-trigger-event",
    "event_type": "assignment_submit",
    "user_id": "risk-test-user",
    "timestamp": "2026-05-27T15:05:00",
    "data": {"assignment_id": "assign-001", "score": 45}
}'

# Check if risk assessment was triggered
test_endpoint "Check Risk Assessment" "$BASE_URL/academic-risk/api/v1/risk/profile/risk-test-user" "200"

# Generate alert based on risk
test_endpoint "Create Alert from Risk" "$BASE_URL/alert/api/v1/alerts" "201" "POST" '{
    "alert_id": "risk-alert-test",
    "user_id": "risk-test-user",
    "risk_score": 0.8,
    "risk_level": "high",
    "alert_type": "academic_risk",
    "message": "High risk student detected",
    "timestamp": "2026-05-27T15:05:00"
}'

# Summary
echo -e "\n${YELLOW}=== Test Suite Complete ===${NC}"
echo "Total Tests: $TOTAL_TESTS"
echo "Passed: $PASSED_TESTS"
echo "Failed: $FAILED_TESTS"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ $FAILED_TESTS tests failed${NC}"
    exit 1
fi