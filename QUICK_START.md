# Graphiti Quick Start Deployment

This guide provides the essential steps to deploy Graphiti knowledge server and MCP server on your personal server.

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key
- Server with at least 4GB RAM

## Quick Deployment

### 1. Setup Environment

```bash
# Copy environment template
cp env.example .env

# Edit with your OpenAI API key and secure Neo4j password
nano .env
```

**Required in `.env`:**
```
OPENAI_API_KEY=your_actual_openai_api_key
NEO4J_PASSWORD=your_secure_password
```

### 2. Deploy Services

**Option A: Full deployment with Nginx (recommended)**
```bash
docker compose -f docker-compose.production.yml up -d --build
```

**Option B: Minimal deployment (no Nginx)**
```bash
docker compose -f docker-compose.minimal.yml up -d --build
```

### 3. Verify Deployment

```bash
# Check if services are running
docker ps

# Test endpoints
curl http://localhost:8000/healthcheck  # Knowledge Server
curl http://localhost:8001/healthcheck  # MCP Server
curl http://localhost:7474              # Neo4j Browser
```

## Service Endpoints

| Service | URL | Description |
|---------|-----|-------------|
| Neo4j Browser | http://your-server:7474 | Database management interface |
| Graphiti Knowledge Server | http://your-server:8000 | REST API for knowledge graph |
| Graphiti MCP Server | http://your-server:8001 | MCP server for AI assistants |
| API Documentation | http://your-server:8000/docs | Interactive API docs |

## MCP Client Configuration

For AI assistants like Claude Desktop or Cursor, configure your MCP client to connect to:

```
http://your-server:8001/sse
```

## Management Commands

```bash
# View logs
docker compose -f docker-compose.production.yml logs

# Stop services
docker compose -f docker-compose.production.yml down

# Restart services
docker compose -f docker-compose.production.yml restart

# Update and redeploy
git pull
docker compose -f docker-compose.production.yml up -d --build
```

## Troubleshooting

### Common Issues

1. **Services not starting**: Check logs with `docker compose logs`
2. **OpenAI rate limits**: Reduce `SEMAPHORE_LIMIT` in `.env`
3. **Memory issues**: Increase Neo4j memory in docker-compose file
4. **Port conflicts**: Ensure ports 7474, 7687, 8000, 8001 are available

### Health Checks

```bash
# Individual service health
curl http://localhost:8000/healthcheck
curl http://localhost:8001/healthcheck
curl http://localhost:7474

# Docker health status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

## Security Notes

- Change default Neo4j password in `.env`
- Use HTTPS in production (configure SSL certificates)
- Restrict access to Neo4j Browser (port 7474) if not needed externally
- Consider using a VPN for secure access

## Next Steps

- Read `DEPLOYMENT.md` for detailed configuration options
- Configure SSL certificates for HTTPS
- Set up monitoring and backups
- Integrate with your Dokploy platform

## Support

- Check logs: `docker compose logs [service-name]`
- View detailed documentation: `DEPLOYMENT.md`
- Report issues on GitHub repository 