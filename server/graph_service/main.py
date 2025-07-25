import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from graph_service.config import get_settings
from graph_service.routers import ingest, retrieve
from graph_service.zep_graphiti import initialize_graphiti

# Configure logging
logging.basicConfig(level=logging.INFO)
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager with Neo4j connection waiting"""
    settings = get_settings()
    
    # Wait for Neo4j to be ready
    neo4j_uri = settings.neo4j_uri
    if not await wait_for_neo4j(neo4j_uri):
        logger.error("Failed to connect to Neo4j, but continuing startup")
    
    # Initialize Graphiti
    try:
        await initialize_graphiti(settings)
        logger.info("Graphiti initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Graphiti: {e}")
        # Continue startup even if Graphiti fails to initialize
    
    yield
    
    # Shutdown
    logger.info("Shutting down Graphiti server")


app = FastAPI(lifespan=lifespan)

app.include_router(retrieve.router)
app.include_router(ingest.router)


@app.get('/')
async def root():
    return JSONResponse(content={
        'message': 'Graphiti Knowledge Server',
        'version': '1.0.0',
        'endpoints': {
            'healthcheck': '/healthcheck',
            'ingest': '/ingest',
            'retrieve': '/retrieve'
        }
    }, status_code=200)


@app.get('/healthcheck')
async def healthcheck():
    return JSONResponse(content={'status': 'healthy'}, status_code=200)
