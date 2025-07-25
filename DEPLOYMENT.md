# Graphiti Production Deployment Guide

This guide explains how to deploy the Graphiti knowledge server and MCP server on your personal server using Docker. The deployment includes both servers alongside a Neo4j database, with optional Nginx reverse proxy for unified access.

## Architecture Overview

The deployment consists of the following components:

- **Neo4j Database** (port 7474/7687) - Shared graph database
- **Graphiti Knowledge Server** (port 8000) - REST API for knowledge graph operations
- **Graphiti MCP Server** (port 8001) - Model Context Protocol server for AI assistants
- **Nginx Reverse Proxy** (port 80/443) - Optional unified access point

## Prerequisites

1. **Docker and Docker Compose** installed on your server
2. **OpenAI API Key** for LLM operations
3. **Domain name** (optional, for SSL certificates)
4. **Server with at least 4GB RAM** (recommended 8GB+)

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository (if not already done)
git clone https://github.com/getzep/graphiti.git
cd graphiti

# Make deployment script executable
chmod +x deploy.sh
```

### 2. Configure Environment

```bash
# Copy environment template
cp env.example .env

# Edit the .env file with your configuration
nano .env
```

**Required Configuration:**
- `OPENAI_API_KEY` - Your OpenAI API key
- `NEO4J_PASSWORD` - Secure password for Neo4j database

**Optional Configuration:**
- `MODEL_NAME` - LLM model to use (default: gpt-4o-mini)
- `SEMAPHORE_LIMIT` - Concurrency limit (default: 10)

### 3. Deploy Services

```bash
# Deploy all services
./deploy.sh deploy

# Or manually with Docker Compose
docker compose -f docker-compose.production.yml up -d --build
```

### 4. Verify Deployment

```bash
# Check service status
./deploy.sh status

# Check service health
./deploy.sh health

# View logs
./deploy.sh logs
```

## Service Endpoints

Once deployed, the following endpoints will be available:

### Direct Access
- **Neo4j Browser**: http://your-server:7474
- **Graphiti Knowledge Server**: http://your-server:8000
- **Graphiti MCP Server**: http://your-server:8001

### API Documentation
- **Graphiti API Docs**: http://your-server:8000/docs
- **Graphiti ReDoc**: http://your-server:8000/redoc

### Health Checks
- **Knowledge Server Health**: http://your-server:8000/healthcheck
- **MCP Server Health**: http://your-server:8001/healthcheck

## Configuration Options

### Environment Variables

The deployment uses the following environment variables (configured in `.env`):

#### Required
- `OPENAI_API_KEY` - Your OpenAI API key
- `NEO4J_PASSWORD` - Secure Neo4j password

#### Optional
- `MODEL_NAME` - Primary LLM model (default: gpt-4o-mini)
- `SMALL_MODEL_NAME` - Small LLM model (default: gpt-4o-mini)
- `EMBEDDING_MODEL_NAME` - Embedding model (default: text-embedding-3-small)
- `LLM_TEMPERATURE` - LLM temperature (0.0-2.0, default: 0.0)
- `SEMAPHORE_LIMIT` - Concurrency limit (default: 10)
- `OPENAI_BASE_URL` - Custom OpenAI endpoint (for Azure, etc.)

### Neo4j Configuration

The Neo4j database is configured with:
- **Memory**: 2GB heap, 1GB page cache
- **Authentication**: Username `neo4j`, password from environment
- **Ports**: 7474 (HTTP), 7687 (Bolt)

### Performance Tuning

For production deployments, consider:

1. **Increase Neo4j memory** if you have large graphs:
   ```yaml
   environment:
     - NEO4J_server_memory_heap_max__size=4G
     - NEO4J_server_memory_pagecache_size=2G
   ```

2. **Adjust concurrency** based on your OpenAI rate limits:
   ```bash
   SEMAPHORE_LIMIT=5  # Lower for rate-limited accounts
   ```

3. **Use persistent volumes** for data persistence:
   ```yaml
   volumes:
     - /path/to/neo4j/data:/data
     - /path/to/neo4j/logs:/logs
   ```

## SSL/HTTPS Configuration

### Option 1: Let's Encrypt (Recommended)

1. Install Certbot:
   ```bash
   sudo apt-get update
   sudo apt-get install certbot
   ```

2. Generate certificates:
   ```bash
   sudo certbot certonly --standalone -d your-domain.com
   ```

3. Update Nginx configuration:
   ```nginx
   ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
   ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
   ```

### Option 2: Self-Signed Certificates

For testing, you can generate self-signed certificates:

```bash
# Create SSL directory
mkdir -p nginx/ssl

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

## Monitoring and Maintenance

### Health Monitoring

The deployment includes health checks for all services:

```bash
# Check all services
./deploy.sh health

# Individual service checks
curl http://localhost:8000/healthcheck
curl http://localhost:8001/healthcheck
```

### Log Management

```bash
# View all logs
./deploy.sh logs

# View specific service logs
docker compose -f docker-compose.production.yml logs graphiti-server
docker compose -f docker-compose.production.yml logs graphiti-mcp
```

### Backup and Recovery

#### Neo4j Backup

```bash
# Create backup
docker exec graphiti-neo4j neo4j-admin dump --database=neo4j --to=/backups/

# Restore backup
docker exec graphiti-neo4j neo4j-admin load --from=/backups/neo4j.dump --database=neo4j --force
```

#### Volume Backup

```bash
# Backup Neo4j data
docker run --rm -v graphiti_neo4j_data:/data -v $(pwd):/backup alpine tar czf /backup/neo4j-backup.tar.gz -C /data .

# Restore Neo4j data
docker run --rm -v graphiti_neo4j_data:/data -v $(pwd):/backup alpine tar xzf /backup/neo4j-backup.tar.gz -C /data
```

## Troubleshooting

### Common Issues

#### 1. Services Not Starting

```bash
# Check service status
./deploy.sh status

# View detailed logs
./deploy.sh logs

# Check Docker resources
docker system df
docker stats
```

#### 2. OpenAI Rate Limits

If you encounter 429 errors, reduce concurrency:

```bash
# Edit .env file
SEMAPHORE_LIMIT=5

# Restart services
docker compose -f docker-compose.production.yml restart graphiti-server graphiti-mcp
```

#### 3. Neo4j Connection Issues

```bash
# Check Neo4j logs
docker compose -f docker-compose.production.yml logs neo4j

# Test Neo4j connection
curl http://localhost:7474

# Reset Neo4j password if needed
docker exec graphiti-neo4j neo4j-admin set-initial-password newpassword
```

#### 4. Memory Issues

If services are running out of memory:

```bash
# Check memory usage
docker stats

# Increase Neo4j memory in docker-compose.production.yml
environment:
  - NEO4J_server_memory_heap_max__size=4G
```

### Performance Optimization

1. **Database Optimization**:
   - Create indexes for frequently queried properties
   - Monitor query performance in Neo4j Browser

2. **API Optimization**:
   - Use pagination for large result sets
   - Implement caching for frequently accessed data

3. **Resource Monitoring**:
   ```bash
   # Monitor resource usage
   docker stats
   
   # Monitor disk usage
   docker system df
   ```

## Security Considerations

### Network Security

1. **Firewall Configuration**:
   ```bash
   # Allow only necessary ports
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw allow 7474/tcp  # Only if external Neo4j access needed
   ```

2. **VPN Access** (Recommended):
   - Restrict Neo4j access to VPN only
   - Use internal network for service communication

### Data Security

1. **Environment Variables**:
   - Never commit `.env` files to version control
   - Use secure password generation for Neo4j

2. **SSL/TLS**:
   - Always use HTTPS in production
   - Regularly update SSL certificates

3. **Backup Security**:
   - Encrypt backup files
   - Store backups in secure location

## Integration with Dokploy

This deployment is compatible with Dokploy (D-O-K-P-L-O-Y). The Docker Compose configuration follows standard practices and can be integrated into your Dokploy workflow.

### Dokploy Integration Steps

1. **Add to Dokploy Configuration**:
   ```yaml
   services:
     graphiti:
       dockerfile: Dockerfile
       ports:
         - "8000:8000"
       environment:
         - OPENAI_API_KEY=${OPENAI_API_KEY}
         - NEO4J_URI=bolt://neo4j:7687
         - NEO4J_USER=${NEO4J_USER}
         - NEO4J_PASSWORD=${NEO4J_PASSWORD}
   ```

2. **Environment Management**:
   - Use Dokploy's environment variable management
   - Configure secrets for API keys and passwords

3. **Health Checks**:
   - Configure Dokploy health checks using the `/healthcheck` endpoints
   - Set appropriate timeout and retry values

## API Usage Examples

### Graphiti Knowledge Server

```bash
# Add episode to knowledge graph
curl -X POST "http://localhost:8000/ingest/episode" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Meeting Notes",
    "episode_body": "Discussed project timeline and requirements",
    "source": "text"
  }'

# Search for nodes
curl -X POST "http://localhost:8000/retrieve/search/nodes" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "project timeline",
    "max_nodes": 10
  }'
```

### Graphiti MCP Server

The MCP server is designed for integration with AI assistants like Claude Desktop or Cursor. Configure your MCP client to connect to:

```
http://localhost:8001/sse
```

## Support and Updates

### Updating Services

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart services
docker compose -f docker-compose.production.yml up -d --build
```

### Getting Help

- **Documentation**: Check the main Graphiti README
- **Issues**: Report issues on the GitHub repository
- **Community**: Join the Graphiti community discussions

## License

This deployment configuration follows the same license as the Graphiti project. 