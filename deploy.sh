#!/bin/bash

# Graphiti Production Deployment Script
# This script sets up and deploys the Graphiti knowledge server and MCP server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Docker and Docker Compose
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to setup environment
setup_environment() {
    print_status "Setting up environment..."
    
    # Create logs directory
    mkdir -p logs
    
    # Create nginx ssl directory
    mkdir -p nginx/ssl
    
    # Check if .env file exists
    if [ ! -f .env ]; then
        if [ -f env.example ]; then
            print_warning ".env file not found. Creating from example..."
            cp env.example .env
            print_warning "Please edit .env file with your actual configuration values"
            print_warning "Especially update OPENAI_API_KEY and NEO4J_PASSWORD"
        else
            print_error "env.example file not found. Please create a .env file manually."
            exit 1
        fi
    else
        print_success ".env file found"
    fi
    
    # Validate required environment variables
    if ! grep -q "OPENAI_API_KEY=" .env || grep -q "OPENAI_API_KEY=your_openai_api_key_here" .env; then
        print_error "Please set your OPENAI_API_KEY in the .env file"
        exit 1
    fi
    
    if ! grep -q "NEO4J_PASSWORD=" .env || grep -q "NEO4J_PASSWORD=your_secure_neo4j_password_here" .env; then
        print_error "Please set a secure NEO4J_PASSWORD in the .env file"
        exit 1
    fi
    
    print_success "Environment setup completed"
}

# Function to deploy services
deploy_services() {
    print_status "Deploying Graphiti services..."
    
    # Build and start services
    if command_exists docker-compose; then
        docker-compose -f docker-compose.production.yml up -d --build
    else
        docker compose -f docker-compose.production.yml up -d --build
    fi
    
    print_success "Services deployment initiated"
}

# Function to check service health
check_health() {
    print_status "Checking service health..."
    
    # Wait for services to start
    sleep 30
    
    # Check Neo4j
    if curl -f http://localhost:7474 >/dev/null 2>&1; then
        print_success "Neo4j is running on http://localhost:7474"
    else
        print_warning "Neo4j health check failed"
    fi
    
    # Check Graphiti Knowledge Server
    if curl -f http://localhost:8000/healthcheck >/dev/null 2>&1; then
        print_success "Graphiti Knowledge Server is running on http://localhost:8000"
    else
        print_warning "Graphiti Knowledge Server health check failed"
    fi
    
    # Check Graphiti MCP Server
    if curl -f http://localhost:8001/healthcheck >/dev/null 2>&1; then
        print_success "Graphiti MCP Server is running on http://localhost:8001"
    else
        print_warning "Graphiti MCP Server health check failed"
    fi
}

# Function to show service status
show_status() {
    print_status "Service status:"
    
    if command_exists docker-compose; then
        docker-compose -f docker-compose.production.yml ps
    else
        docker compose -f docker-compose.production.yml ps
    fi
}

# Function to show logs
show_logs() {
    print_status "Showing recent logs..."
    
    if command_exists docker-compose; then
        docker-compose -f docker-compose.production.yml logs --tail=50
    else
        docker compose -f docker-compose.production.yml logs --tail=50
    fi
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    
    if command_exists docker-compose; then
        docker-compose -f docker-compose.production.yml down
    else
        docker compose -f docker-compose.production.yml down
    fi
    
    print_success "Services stopped"
}

# Function to show usage
show_usage() {
    echo "Graphiti Production Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy     - Deploy all services (default)"
    echo "  status     - Show service status"
    echo "  logs       - Show recent logs"
    echo "  stop       - Stop all services"
    echo "  health     - Check service health"
    echo "  help       - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy    # Deploy all services"
    echo "  $0 status    # Check service status"
    echo "  $0 logs      # View logs"
}

# Main script logic
case "${1:-deploy}" in
    "deploy")
        check_prerequisites
        setup_environment
        deploy_services
        check_health
        print_success "Deployment completed!"
        print_status "Services available at:"
        print_status "  - Neo4j Browser: http://localhost:7474"
        print_status "  - Graphiti Knowledge Server: http://localhost:8000"
        print_status "  - Graphiti MCP Server: http://localhost:8001"
        print_status "  - API Documentation: http://localhost:8000/docs"
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs
        ;;
    "stop")
        stop_services
        ;;
    "health")
        check_health
        ;;
    "help"|"-h"|"--help")
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac 