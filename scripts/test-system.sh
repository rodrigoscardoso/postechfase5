#!/bin/bash

# FIAP X Video Processor - System Test Script

set -e

echo "🧪 FIAP X Video Processor - System Tests"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test configuration
API_BASE="http://localhost:8080/api"
TEST_USER="testuser"
TEST_PASSWORD="test123"
TOKEN=""

# Function to print test results
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        exit 1
    fi
}

# Function to make API calls
api_call() {
    local method=$1
    local endpoint=$2
    local data=$3
    local headers=$4
    
    if [ -n "$headers" ]; then
        curl -s -X $method "$API_BASE$endpoint" \
             -H "Content-Type: application/json" \
             -H "$headers" \
             -d "$data"
    else
        curl -s -X $method "$API_BASE$endpoint" \
             -H "Content-Type: application/json" \
             -d "$data"
    fi
}

echo "🔍 Testing system health..."

# Test 1: Health Check
echo "1. Testing health endpoints..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/health")
if [ "$response" = "200" ]; then
    print_result 0 "API Gateway health check"
else
    print_result 1 "API Gateway health check (HTTP $response)"
fi

# Test 2: Authentication
echo "2. Testing authentication..."

# Login test
login_response=$(api_call "POST" "/auth/login" '{"username":"'$TEST_USER'","password":"'$TEST_PASSWORD'"}')
if echo "$login_response" | grep -q "token"; then
    TOKEN=$(echo "$login_response" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
    print_result 0 "User login"
else
    print_result 1 "User login"
fi

# Token verification
if [ -n "$TOKEN" ]; then
    verify_response=$(api_call "POST" "/auth/verify" '{"token":"'$TOKEN'"}')
    if echo "$verify_response" | grep -q "valid"; then
        print_result 0 "Token verification"
    else
        print_result 1 "Token verification"
    fi
fi

# Test 3: Video Processing Endpoints
echo "3. Testing video processing endpoints..."

# Get user stats
if [ -n "$TOKEN" ]; then
    stats_response=$(api_call "GET" "/video/stats" "" "Authorization: Bearer $TOKEN")
    if echo "$stats_response" | grep -q "total_jobs"; then
        print_result 0 "Video stats endpoint"
    else
        print_result 1 "Video stats endpoint"
    fi
    
    # Get user jobs
    jobs_response=$(api_call "GET" "/video/jobs" "" "Authorization: Bearer $TOKEN")
    if echo "$jobs_response" | grep -q "jobs"; then
        print_result 0 "Video jobs listing"
    else
        print_result 1 "Video jobs listing"
    fi
fi

# Test 4: Service Health Aggregation
echo "4. Testing service health aggregation..."
health_all_response=$(curl -s "$API_BASE/health/all")
if echo "$health_all_response" | grep -q "overall_status"; then
    print_result 0 "Health aggregation endpoint"
else
    print_result 1 "Health aggregation endpoint"
fi

echo ""
echo "🎉 All tests completed successfully!"
echo ""
echo "📊 Test Summary:"
echo "- Authentication: ✅"
echo "- API Gateway: ✅"
echo "- Video Processing: ✅"
echo "- Health Monitoring: ✅"
echo ""
echo "🚀 System is ready for production!"

