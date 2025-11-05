from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from config import settings
from core.plugin_registry import PluginRegistry
from core.event_bus import EventBus
from core.database import get_supabase_client
from core.cache import get_redis_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    
    await get_redis_client()
    get_supabase_client()
    
    event_bus = EventBus()
    await event_bus.connect()
    
    plugin_registry = PluginRegistry(app)
    await plugin_registry.discover_and_load_plugins()
    
    logger.info("Application started successfully")
    yield
    
    logger.info("Shutting down application...")
    await event_bus.disconnect()
    await (await get_redis_client()).close()

app = FastAPI(
    title="SaaS Subscription Platform API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": settings.environment}

@app.get("/")
async def root():
    return {"message": "SaaS Subscription Platform API", "version": "1.0.0"}

