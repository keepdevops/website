import redis.asyncio as redis
from typing import Callable, Dict, List, Any
import json
import asyncio
from functools import lru_cache
from config import settings
import logging

logger = logging.getLogger(__name__)

class EventBus:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._redis_client: redis.Redis = None
        self._pubsub: redis.client.PubSub = None
        self._listeners: Dict[str, List[Callable]] = {}
        self._running = False
        self._initialized = True
    
    async def connect(self):
        if self._redis_client is None:
            self._redis_client = await redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            self._pubsub = self._redis_client.pubsub()
    
    async def disconnect(self):
        if self._pubsub:
            await self._pubsub.close()
        if self._redis_client:
            await self._redis_client.close()
    
    def subscribe(self, event_name: str, callback: Callable):
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)
        logger.info(f"Subscribed to event: {event_name}")
    
    async def publish(self, event_name: str, data: Any):
        if self._redis_client is None:
            await self.connect()
        
        payload = json.dumps({"event": event_name, "data": data})
        await self._redis_client.publish(event_name, payload)
        logger.info(f"Published event: {event_name}")
        
        await self._trigger_local_listeners(event_name, data)
    
    async def _trigger_local_listeners(self, event_name: str, data: Any):
        if event_name in self._listeners:
            for callback in self._listeners[event_name]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data)
                    else:
                        callback(data)
                except Exception as e:
                    logger.error(f"Error in event listener for {event_name}: {str(e)}")
    
    async def start_listening(self):
        if self._running:
            return
        
        self._running = True
        channel_names = list(self._listeners.keys())
        
        if not channel_names:
            return
        
        await self._pubsub.subscribe(*channel_names)
        
        asyncio.create_task(self._listen_loop())
    
    async def _listen_loop(self):
        async for message in self._pubsub.listen():
            if message["type"] == "message":
                try:
                    payload = json.loads(message["data"])
                    event_name = payload["event"]
                    data = payload["data"]
                    await self._trigger_local_listeners(event_name, data)
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")

@lru_cache
def get_event_bus() -> EventBus:
    return EventBus()

