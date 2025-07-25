#!/bin/bash

# Neo4j Troubleshooting Script for Graphiti Deployment
# This script helps diagnose and fix common Neo4j issues

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to check if container is running
check_container() {
    local container_name=$1
    if docker ps --format "table {{.Names}}" | grep -q "^${container_name}$"; then
        return 0
    else
        return 1
    fi
}

# Function to check Neo4j health
check_neo4j_health() {
    print_status "Checking Neo4j health..."
    
    if ! check_container "graphiti-neo4j"; then
        print_error "Neo4j container is not running"
        return 1
    fi
    
    # Check if Neo4j is responding
    if curl -f http://localhost:7474 >/dev/null 2>&1; then
        print_success "Neo4j HTTP endpoint is responding"
    else
        print_warning "Neo4j HTTP endpoint is not responding"
    fi
    
    # Check container logs for errors
    print_status "Checking Neo4j logs for errors..."
    docker logs graphiti-neo4j --tail=20 | grep -i error || print_success "No recent errors found"
}

# Function to restart Neo4j with optimized settings
restart_neo4j() {
    print_status "Restarting Neo4j with optimized settings..."
    
    # Stop Neo4j
    docker stop graphiti-neo4j 2>/dev/null || true
    
    # Remove container
    docker rm graphiti-neo4j 2>/dev/null || true
    
    # Start Neo4j with optimized settings
    docker run -d \
        --name graphiti-neo4j \
        --network graphiti-network \
        -p 7474:7474 \
        -p 7687:7687 \
        -v neo4j_data:/data \
        -v neo4j_logs:/logs \
        --restart unless-stopped \
        --memory=2g \
        --cpus=1.0 \
        -e NEO4J_AUTH=neo4j/your_secure_password \
        -e NEO4J_server_memory_heap_initial__size=512m \
        -e NEO4J_server_memory_heap_max__size=1G \
        -e NEO4J_server_memory_pagecache_size=512m \
        neo4j:5.26.2
    
    print_success "Neo4j restarted with optimized settings"
}

# Function to check system resources
check_system_resources() {
    print_status "Checking system resources..."
    
    # Check available memory
    local available_mem=$(free -m | awk 'NR==2{printf "%.0f", $7*100/$2}')
    print_status "Available memory: ${available_mem}%"
    
    if [ "$available_mem" -lt 20 ]; then
        print_warning "Low memory available. Consider stopping other containers."
    fi
    
    # Check CPU usage
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    print_status "CPU usage: ${cpu_usage}%"
    
    # Check disk space
    local disk_usage=$(df -h / | awk 'NR==2{print $5}' | cut -d'%' -f1)
    print_status "Disk usage: ${disk_usage}%"
    
    if [ "$disk_usage" -gt 90 ]; then
        print_warning "High disk usage. Consider cleaning up."
    fi
}

# Function to optimize Docker settings
optimize_docker() {
    print_status "Optimizing Docker settings..."
    
    # Increase Docker daemon memory limit
    if [ -f /etc/docker/daemon.json ]; then
        print_status "Docker daemon config found"
    else
        print_warning "Consider creating /etc/docker/daemon.json with memory limits"
    fi
    
    # Check Docker network settings
    print_status "Checking Docker network..."
    docker network ls | grep graphiti || print_warning "Graphiti network not found"
}

# Function to test Neo4j connection
test_neo4j_connection() {
    print_status "Testing Neo4j connection..."
    
    # Test HTTP connection
    if curl -f http://localhost:7474 >/dev/null 2>&1; then
        print_success "HTTP connection successful"
    else
        print_error "HTTP connection failed"
    fi
    
    # Test Bolt connection (requires cypher-shell or similar)
    if command -v cypher-shell >/dev/null 2>&1; then
        if echo "RETURN 1;" | cypher-shell -u neo4j -p your_secure_password >/dev/null 2>&1; then
            print_success "Bolt connection successful"
        else
            print_error "Bolt connection failed"
        fi
    else
        print_warning "cypher-shell not available, skipping Bolt test"
    fi
}

# Function to show Neo4j configuration
show_neo4j_config() {
    print_status "Current Neo4j configuration:"
    
    if check_container "graphiti-neo4j"; then
        docker exec graphiti-neo4j env | grep NEO4J_ | sort
    else
        print_error "Neo4j container not running"
    fi
}

# Function to clear Neo4j logs
clear_neo4j_logs() {
    print_status "Clearing Neo4j logs..."
    
    if check_container "graphiti-neo4j"; then
        docker exec graphiti-neo4j rm -f /logs/neo4j.log.* 2>/dev/null || true
        print_success "Neo4j logs cleared"
    else
        print_error "Neo4j container not running"
    fi
}

# Function to show usage
show_usage() {
    echo "Neo4j Troubleshooting Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  health     - Check Neo4j health and logs"
    echo "  restart    - Restart Neo4j with optimized settings"
    echo "  resources  - Check system resources"
    echo "  docker     - Optimize Docker settings"
    echo "  test       - Test Neo4j connections"
    echo "  config     - Show Neo4j configuration"
    echo "  clear-logs - Clear Neo4j logs"
    echo "  all        - Run all checks and optimizations"
    echo "  help       - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 health    # Check Neo4j health"
    echo "  $0 restart   # Restart with optimized settings"
    echo "  $0 all       # Run all diagnostics"
}

# Main script logic
case "${1:-help}" in
    "health")
        check_neo4j_health
        ;;
    "restart")
        restart_neo4j
        ;;
    "resources")
        check_system_resources
        ;;
    "docker")
        optimize_docker
        ;;
    "test")
        test_neo4j_connection
        ;;
    "config")
        show_neo4j_config
        ;;
    "clear-logs")
        clear_neo4j_logs
        ;;
    "all")
        print_status "Running comprehensive Neo4j diagnostics..."
        check_system_resources
        optimize_docker
        check_neo4j_health
        test_neo4j_connection
        show_neo4j_config
        print_success "All diagnostics completed"
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