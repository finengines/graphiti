#!/usr/bin/env python3
"""
Startup script for Graphiti Knowledge Server
Handles proper initialization and connection retries
"""

import asyncio
import logging
import os
import sys
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def wait_for_neo4j(uri: str, max_retries: int = 30, retry_delay: float = 2.0) -> bool:
    """Wait for Neo4j to be ready"""
    import socket
    
    # Extract host and port from URI
    if uri.startswith('bolt://'):
        uri = uri[6:]  # Remove 'bolt://'
    
    if ':' in uri:
        host, port_str = uri.split(':', 1)
        port = int(port_str)
    else:
        host = uri
        port = 7687
    
    logger.info(f"Waiting for Neo4j at {host}:{port}")
    
    for attempt in range(max_retries):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                logger.info(f"Neo4j is ready at {host}:{port}")
                return True
            else:
                logger.warning(f"Neo4j not ready (attempt {attempt + 1}/{max_retries})")
                
        except Exception as e:
            logger.warning(f"Connection attempt failed (attempt {attempt + 1}/{max_retries}): {e}")
        
        if attempt < max_retries - 1:
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 1.2, 10)  # Gradual backoff
    
    logger.error("Neo4j failed to become ready after all retries")
    return False


async def main():
    """Main startup function"""
    # Get Neo4j URI from environment
    neo4j_uri = os.getenv('NEO4J_URI', 'bolt://neo4j:7687')
    
    logger.info("Starting Graphiti Knowledge Server initialization")
    
    # Wait for Neo4j to be ready
    if not await wait_for_neo4j(neo4j_uri):
        logger.error("Failed to connect to Neo4j, exiting")
        sys.exit(1)
    
    logger.info("Neo4j is ready, starting server")
    
    # Import and run the FastAPI app
    try:
        from graph_service.main import app
        import uvicorn
        
        # Start the server
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 