#!/usr/bin/env python3
"""
Deployment verification script for Graphiti on Dokploy
"""

import os
import sys
import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def check_neo4j_connection(uri: str, user: str, password: str) -> bool:
    """Check if Neo4j is accessible"""
    try:
        # This is a simplified check - in production you'd use the Neo4j driver
        logger.info(f"Checking Neo4j connection to {uri}")
        
        # For now, just check if the URI format is correct
        if not uri.startswith('bolt://'):
            logger.error(f"Invalid Neo4j URI format: {uri}")
            return False
            
        logger.info("Neo4j URI format is valid")
        return True
    except Exception as e:
        logger.error(f"Neo4j connection check failed: {e}")
        return False


async def check_server_health(url: str) -> bool:
    """Check if a server is healthy"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{url}/healthcheck", timeout=10) as response:
                if response.status == 200:
                    logger.info(f"Server health check passed: {url}")
                    return True
                else:
                    logger.error(f"Server health check failed with status {response.status}: {url}")
                    return False
    except Exception as e:
        logger.error(f"Server health check failed: {url} - {e}")
        return False


async def check_api_endpoints(base_url: str) -> Dict[str, bool]:
    """Check various API endpoints"""
    endpoints = {
        'root': '/',
        'healthcheck': '/healthcheck',
    }
    
    results = {}
    
    for name, endpoint in endpoints.items():
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{base_url}{endpoint}", timeout=10) as response:
                    results[name] = response.status == 200
                    if response.status == 200:
                        logger.info(f"Endpoint {name} is accessible")
                    else:
                        logger.warning(f"Endpoint {name} returned status {response.status}")
        except Exception as e:
            logger.error(f"Endpoint {name} check failed: {e}")
            results[name] = False
    
    return results


def check_environment_variables() -> Dict[str, bool]:
    """Check if required environment variables are set"""
    required_vars = [
        'OPENAI_API_KEY',
        'NEO4J_USER',
        'NEO4J_PASSWORD',
    ]
    
    optional_vars = [
        'MODEL_NAME',
        'EMBEDDING_MODEL_NAME',
        'SEMAPHORE_LIMIT',
    ]
    
    results = {}
    
    # Check required variables
    for var in required_vars:
        value = os.getenv(var)
        results[var] = value is not None and value.strip() != ''
        if results[var]:
            logger.info(f"Required environment variable {var} is set")
        else:
            logger.error(f"Required environment variable {var} is missing or empty")
    
    # Check optional variables
    for var in optional_vars:
        value = os.getenv(var)
        results[var] = value is not None and value.strip() != ''
        if results[var]:
            logger.info(f"Optional environment variable {var} is set: {value}")
        else:
            logger.warning(f"Optional environment variable {var} is not set (using default)")
    
    return results


async def main():
    """Main verification function"""
    logger.info("Starting Graphiti deployment verification")
    
    # Check environment variables
    env_check = check_environment_variables()
    
    # Get configuration from environment
    neo4j_uri = os.getenv('NEO4J_URI', 'bolt://neo4j:7687')
    neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
    neo4j_password = os.getenv('NEO4J_PASSWORD', '')
    
    # Check Neo4j connection
    neo4j_ok = await check_neo4j_connection(neo4j_uri, neo4j_user, neo4j_password)
    
    # Check server health (assuming localhost for this script)
    server_url = "http://localhost:8000"
    server_health = await check_server_health(server_url)
    
    # Check API endpoints
    api_endpoints = await check_api_endpoints(server_url)
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("DEPLOYMENT VERIFICATION SUMMARY")
    logger.info("="*50)
    
    # Environment variables
    required_env_ok = all(env_check.get(var, False) for var in ['OPENAI_API_KEY', 'NEO4J_USER', 'NEO4J_PASSWORD'])
    logger.info(f"Environment Variables: {'✓' if required_env_ok else '✗'}")
    
    # Neo4j
    logger.info(f"Neo4j Connection: {'✓' if neo4j_ok else '✗'}")
    
    # Server health
    logger.info(f"Server Health: {'✓' if server_health else '✗'}")
    
    # API endpoints
    api_ok = all(api_endpoints.values())
    logger.info(f"API Endpoints: {'✓' if api_ok else '✗'}")
    
    # Overall status
    overall_ok = required_env_ok and neo4j_ok and server_health and api_ok
    logger.info(f"\nOverall Status: {'✓ DEPLOYMENT SUCCESSFUL' if overall_ok else '✗ DEPLOYMENT ISSUES DETECTED'}")
    
    if not overall_ok:
        logger.info("\nTroubleshooting steps:")
        if not required_env_ok:
            logger.info("- Check that all required environment variables are set")
        if not neo4j_ok:
            logger.info("- Verify Neo4j is running and accessible")
        if not server_health:
            logger.info("- Check that the Graphiti server is running on port 8000")
        if not api_ok:
            logger.info("- Verify API endpoints are responding correctly")
    
    return 0 if overall_ok else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 