#!/bin/bash
# Integration test script for VittCott backend
# This script starts local DynamoDB (if Docker is available), runs create-table,
# starts the server, and runs a small smoke test.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

# Configuration
DYNAMODB_PORT="${DYNAMODB_PORT:-8000}"
SERVER_PORT="${SERVER_PORT:-3000}"
DYNAMODB_CONTAINER_NAME="vittcott-dynamodb-test"
CLEANUP_ON_EXIT="${CLEANUP_ON_EXIT:-true}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

cleanup() {
    log_info "Cleaning up..."
    
    # Stop the server if running
    if [ -n "$SERVER_PID" ] && kill -0 "$SERVER_PID" 2>/dev/null; then
        log_info "Stopping server (PID: $SERVER_PID)"
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
    
    # Stop DynamoDB container if we started it and cleanup is enabled
    if [ "$DYNAMODB_STARTED" = "true" ] && [ "$CLEANUP_ON_EXIT" = "true" ]; then
        log_info "Stopping DynamoDB container..."
        docker stop "$DYNAMODB_CONTAINER_NAME" 2>/dev/null || true
        docker rm "$DYNAMODB_CONTAINER_NAME" 2>/dev/null || true
    fi
}

trap cleanup EXIT

# Check if Docker is available
check_docker() {
    if command -v docker &> /dev/null; then
        if docker info &> /dev/null; then
            return 0
        else
            log_warn "Docker is installed but not running"
            return 1
        fi
    else
        log_warn "Docker is not installed"
        return 1
    fi
}

# Start local DynamoDB using Docker
start_dynamodb() {
    log_info "Starting local DynamoDB on port $DYNAMODB_PORT..."
    
    # Check if container already exists
    if docker ps -a --format '{{.Names}}' | grep -q "^${DYNAMODB_CONTAINER_NAME}$"; then
        if docker ps --format '{{.Names}}' | grep -q "^${DYNAMODB_CONTAINER_NAME}$"; then
            log_info "DynamoDB container already running"
            return 0
        else
            log_info "Removing existing stopped container..."
            docker rm "$DYNAMODB_CONTAINER_NAME" 2>/dev/null || true
        fi
    fi
    
    docker run -d \
        --name "$DYNAMODB_CONTAINER_NAME" \
        -p "$DYNAMODB_PORT:8000" \
        amazon/dynamodb-local:latest \
        -jar DynamoDBLocal.jar -sharedDb
    
    DYNAMODB_STARTED="true"
    
    # Wait for DynamoDB to be ready
    log_info "Waiting for DynamoDB to be ready..."
    for i in {1..30}; do
        if curl -s "http://localhost:$DYNAMODB_PORT" > /dev/null 2>&1; then
            log_info "DynamoDB is ready"
            return 0
        fi
        sleep 1
    done
    
    log_error "DynamoDB failed to start within 30 seconds"
    return 1
}

# Run table creation
create_table() {
    log_info "Creating DynamoDB table..."
    cd "$BACKEND_DIR"
    
    export DYNAMODB_ENDPOINT="http://localhost:$DYNAMODB_PORT"
    export AWS_ACCESS_KEY_ID="test"
    export AWS_SECRET_ACCESS_KEY="test"
    export AWS_REGION="us-east-1"
    
    npm run create-table || {
        # Table might already exist, which is fine
        log_info "Table creation completed (might already exist)"
    }
}

# Start the server
start_server() {
    log_info "Starting server on port $SERVER_PORT..."
    cd "$BACKEND_DIR"
    
    export DYNAMODB_ENDPOINT="http://localhost:$DYNAMODB_PORT"
    export AWS_ACCESS_KEY_ID="test"
    export AWS_SECRET_ACCESS_KEY="test"
    export AWS_REGION="us-east-1"
    export PORT="$SERVER_PORT"
    export AUTO_CREATE_TABLE="true"
    
    node server.js &
    SERVER_PID=$!
    
    # Wait for server to be ready
    log_info "Waiting for server to be ready..."
    for i in {1..30}; do
        if curl -s "http://localhost:$SERVER_PORT/" > /dev/null 2>&1; then
            log_info "Server is ready (PID: $SERVER_PID)"
            return 0
        fi
        sleep 1
    done
    
    log_error "Server failed to start within 30 seconds"
    return 1
}

# Run smoke tests
run_smoke_tests() {
    log_info "Running smoke tests..."
    local passed=0
    local failed=0
    
    # Test 1: Health check
    log_info "Test 1: Health check (GET /)"
    response=$(curl -s -w "\n%{http_code}" "http://localhost:$SERVER_PORT/")
    http_code=$(echo "$response" | tail -1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" = "200" ]; then
        log_info "  ✓ Health check passed (HTTP $http_code)"
        ((passed++))
    else
        log_error "  ✗ Health check failed (HTTP $http_code)"
        ((failed++))
    fi
    
    # Test 2: Register a new user
    log_info "Test 2: Register a new user (POST /register)"
    test_email="test_$(date +%s)@example.com"
    response=$(curl -s -w "\n%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$test_email\",\"password\":\"testpass123\",\"displayName\":\"Test User\"}" \
        "http://localhost:$SERVER_PORT/register")
    http_code=$(echo "$response" | tail -1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" = "201" ]; then
        log_info "  ✓ Registration passed (HTTP $http_code)"
        ((passed++))
    else
        log_error "  ✗ Registration failed (HTTP $http_code): $body"
        ((failed++))
    fi
    
    # Test 3: Try to register same email (should fail with 409)
    log_info "Test 3: Duplicate registration (POST /register)"
    response=$(curl -s -w "\n%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$test_email\",\"password\":\"testpass123\",\"displayName\":\"Test User\"}" \
        "http://localhost:$SERVER_PORT/register")
    http_code=$(echo "$response" | tail -1)
    
    if [ "$http_code" = "409" ]; then
        log_info "  ✓ Duplicate check passed (HTTP $http_code)"
        ((passed++))
    else
        log_error "  ✗ Duplicate check failed (HTTP $http_code, expected 409)"
        ((failed++))
    fi
    
    # Test 4: Login with the registered user
    log_info "Test 4: Login (POST /login)"
    response=$(curl -s -w "\n%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$test_email\",\"password\":\"testpass123\"}" \
        "http://localhost:$SERVER_PORT/login")
    http_code=$(echo "$response" | tail -1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" = "200" ]; then
        log_info "  ✓ Login passed (HTTP $http_code)"
        ((passed++))
        # Extract token for next test
        token=$(echo "$body" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
    else
        log_error "  ✗ Login failed (HTTP $http_code): $body"
        ((failed++))
    fi
    
    # Test 5: Access protected /me endpoint with token
    if [ -n "$token" ]; then
        log_info "Test 5: Protected endpoint (GET /me)"
        response=$(curl -s -w "\n%{http_code}" \
            -H "Authorization: Bearer $token" \
            "http://localhost:$SERVER_PORT/me")
        http_code=$(echo "$response" | tail -1)
        
        if [ "$http_code" = "200" ]; then
            log_info "  ✓ Protected endpoint passed (HTTP $http_code)"
            ((passed++))
        else
            log_error "  ✗ Protected endpoint failed (HTTP $http_code)"
            ((failed++))
        fi
    else
        log_warn "  - Skipping protected endpoint test (no token available)"
    fi
    
    # Test 6: Invalid login credentials
    log_info "Test 6: Invalid login (POST /login)"
    response=$(curl -s -w "\n%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d '{"email":"nonexistent@example.com","password":"wrongpassword"}' \
        "http://localhost:$SERVER_PORT/login")
    http_code=$(echo "$response" | tail -1)
    
    if [ "$http_code" = "401" ]; then
        log_info "  ✓ Invalid login check passed (HTTP $http_code)"
        ((passed++))
    else
        log_error "  ✗ Invalid login check failed (HTTP $http_code, expected 401)"
        ((failed++))
    fi
    
    # Summary
    echo ""
    log_info "============================================"
    log_info "Smoke Test Results: $passed passed, $failed failed"
    log_info "============================================"
    
    if [ "$failed" -gt 0 ]; then
        return 1
    fi
    return 0
}

# Main execution
main() {
    log_info "============================================"
    log_info "VittCott Integration Test"
    log_info "============================================"
    echo ""
    
    # Check for npm
    if ! command -v npm &> /dev/null; then
        log_error "npm is required but not installed"
        exit 1
    fi
    
    # Install dependencies if needed
    if [ ! -d "$BACKEND_DIR/node_modules" ]; then
        log_info "Installing backend dependencies..."
        cd "$BACKEND_DIR"
        npm install
    fi
    
    # Check for Docker and start DynamoDB
    if check_docker; then
        start_dynamodb
    else
        log_warn "Docker not available. Attempting to use existing DynamoDB instance..."
        log_warn "Make sure DynamoDB Local is running on port $DYNAMODB_PORT"
        
        # Check if DynamoDB is already running
        if ! curl -s "http://localhost:$DYNAMODB_PORT" > /dev/null 2>&1; then
            log_error "No DynamoDB instance found on port $DYNAMODB_PORT"
            log_error "Please start DynamoDB Local manually or install Docker"
            exit 1
        fi
    fi
    
    # Create table
    create_table
    
    # Start server
    start_server
    
    # Run smoke tests
    if run_smoke_tests; then
        log_info "All integration tests passed!"
        exit 0
    else
        log_error "Some integration tests failed"
        exit 1
    fi
}

main "$@"
