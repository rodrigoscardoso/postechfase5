#!/bin/bash

# FIAP X Video Processor - Development Setup Script

set -e

echo "🚀 FIAP X Video Processor - Development Setup"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is installed
print_status "Checking Docker installation..."
if command -v docker &> /dev/null; then
    print_success "Docker is installed"
else
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
print_status "Checking Docker Compose installation..."
if command -v docker-compose &> /dev/null; then
    print_success "Docker Compose is installed"
else
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create environment file if it doesn't exist
print_status "Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env
    print_success "Created .env file from template"
    print_warning "Please edit .env file with your configuration"
else
    print_success "Environment file already exists"
fi

# Build and start infrastructure services
print_status "Starting infrastructure services..."
docker-compose up -d postgres redis rabbitmq

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

# Check service health
print_status "Checking service health..."

# Check PostgreSQL
if docker-compose exec -T postgres pg_isready -U fiapx_user -d fiapx_videos &> /dev/null; then
    print_success "PostgreSQL is ready"
else
    print_warning "PostgreSQL is not ready yet"
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping &> /dev/null; then
    print_success "Redis is ready"
else
    print_warning "Redis is not ready yet"
fi

# Check RabbitMQ
if docker-compose exec -T rabbitmq rabbitmq-diagnostics ping &> /dev/null; then
    print_success "RabbitMQ is ready"
else
    print_warning "RabbitMQ is not ready yet"
fi

# Build application services
print_status "Building application services..."
docker-compose build auth-service video-processor notification-service api-gateway

# Start application services
print_status "Starting application services..."
docker-compose up -d auth-service video-processor notification-service api-gateway

# Build and start frontend
print_status "Building and starting frontend..."
docker-compose build frontend
docker-compose up -d frontend

# Start monitoring services
print_status "Starting monitoring services..."
docker-compose up -d prometheus grafana

print_success "Development environment setup complete!"

echo ""
echo "🌐 Access URLs:"
echo "- Frontend: http://localhost:3000"
echo "- API Gateway: http://localhost:8080"
echo "- RabbitMQ Management: http://localhost:15672 (user: fiapx_user, pass: fiapx_password)"
echo "- Grafana: http://localhost:3001 (user: admin, pass: admin)"
echo "- Prometheus: http://localhost:9090"
echo ""
echo "👥 Test Users:"
echo "- Admin: username: admin, password: admin123"
echo "- Test: username: testuser, password: test123"
echo ""
echo "🧪 Run tests with: ./scripts/test-system.sh"
echo "📊 Check logs with: docker-compose logs -f [service-name]"

