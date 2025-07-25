# Graphiti Deployment Guide for Dokploy

## Overview

This guide covers deploying Graphiti Knowledge Server on Dokploy platform with proper configuration and troubleshooting.

## Prerequisites

- Dokploy account and project setup
- OpenAI API key
- Docker and Docker Compose knowledge

## Quick Deployment

### 1. Environment Configuration

Create a `.env` file in your project root with the following variables:

```bash
# Required: OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Neo4j Database Configuration
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_secure_password_here

# LLM Model Configuration
MODEL_NAME=gpt-4o-mini
SMALL_MODEL_NAME=gpt-4o-mini
EMBEDDING_MODEL_NAME=text-embedding-3-small
LLM_TEMPERATURE=0.0

# Performance Configuration
SEMAPHORE_LIMIT=10
```

### 2. Deployment Steps

1. **Upload your code** to Dokploy
2. **Set environment variables** in Dokploy dashboard
3. **Use the docker-compose.dokploy.yml** file
4. **Deploy the stack**

### 3. Service Architecture

The deployment includes three services:

- **Neo4j Database**: Graph database backend
- **Graphiti Knowledge Server**: REST API server (port 8000)
- **Graphiti MCP Server**: Model Context Protocol server (port 8001)

## Troubleshooting

### Common Issues

#### 1. Neo4j Connection Failures

**Symptoms:**
```
Transaction failed and will be retried in 1.182745825845585s (Couldn't connect to neo4j:7687
```

**Solutions:**
- Ensure Neo4j container is healthy before starting other services
- Check that `NEO4J_URI=bolt://neo4j:7687` is set correctly
- Verify Neo4j credentials in environment variables
- Wait for Neo4j to fully initialize (can take 2-3 minutes)

#### 2. 404 Errors on Root Path

**Symptoms:**
```
INFO: 10.0.1.57:60038 - "GET / HTTP/1.1" 404 Not Found
```

**Solutions:**
- The server now includes a root endpoint that returns API information
- Check that the server is running on port 8000
- Verify health check endpoint at `/healthcheck`

#### 3. Health Check Failures

**Symptoms:**
- Container restarting repeatedly
- Health check timeouts

**Solutions:**
- Increase health check start period (now set to 60s)
- Check logs for specific error messages
- Verify all environment variables are set correctly

### Debugging Steps

1. **Check container logs:**
   ```bash
   docker logs graphiti-knowledge-server
   docker logs neo4j
   ```

2. **Verify Neo4j is running:**
   ```bash
   docker exec neo4j cypher-shell -u neo4j -p your_password
   ```

3. **Test API endpoints:**
   ```bash
   curl http://localhost:8000/
   curl http://localhost:8000/healthcheck
   ```

4. **Check network connectivity:**
   ```bash
   docker exec graphiti-knowledge-server ping neo4j
   ```

## Configuration Details

### Neo4j Configuration

- **Memory settings**: Optimized for Dokploy (1GB heap, 512MB page cache)
- **Bolt protocol**: Enabled on port 7687
- **HTTP interface**: Available on port 7474 for browser access
- **Authentication**: Uses environment variables for username/password

### Server Configuration

- **Startup retry logic**: Automatically retries Neo4j connection up to 30 times
- **Health checks**: Improved health check scripts
- **Resource limits**: 1GB memory, 0.5 CPU cores per service
- **Logging**: Structured logging with proper error reporting

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `NEO4J_USER` | Neo4j username | neo4j |
| `NEO4J_PASSWORD` | Neo4j password | your_secure_password |
| `MODEL_NAME` | Primary LLM model | gpt-4o-mini |
| `EMBEDDING_MODEL_NAME` | Embedding model | text-embedding-3-small |
| `SEMAPHORE_LIMIT` | Concurrency limit | 10 |

## API Endpoints

- `GET /` - Server information and available endpoints
- `GET /healthcheck` - Health check endpoint
- `POST /ingest/` - Ingest data into knowledge graph
- `GET /retrieve/` - Retrieve information from knowledge graph

## Monitoring

### Health Checks

- **Neo4j**: HTTP endpoint on port 7474
- **Graphiti Server**: Custom health check script
- **MCP Server**: HTTP health check on port 8000

### Logs

- All services log to stdout/stderr
- Logs are available in Dokploy dashboard
- Structured logging with timestamps and log levels

## Performance Tuning

### Memory Settings

- **Neo4j**: 1GB heap, 512MB page cache
- **Graphiti Server**: 1GB memory limit
- **MCP Server**: 1GB memory limit

### Concurrency

- **SEMAPHORE_LIMIT**: Controls concurrent operations (default: 10)
- Adjust based on your OpenAI rate limits and server capacity

## Security Considerations

1. **Change default passwords** for Neo4j
2. **Use secure API keys** for OpenAI
3. **Limit network access** to necessary ports only
4. **Monitor logs** for suspicious activity
5. **Regular updates** of base images

## Support

For issues specific to this deployment:

1. Check the logs for error messages
2. Verify environment variables are set correctly
3. Ensure Neo4j is healthy before other services start
4. Test connectivity between services
5. Review the troubleshooting section above

For Graphiti-specific issues, refer to the main documentation and GitHub repository. 