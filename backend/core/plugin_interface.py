from abc import ABC, abstractmethod
from typing import Optional
from fastapi import APIRouter

class PluginInterface(ABC):
    def __init__(self):
        self.name: str = self.__class__.__name__
        self.version: str = "1.0.0"
        self.enabled: bool = True
    
    @abstractmethod
    def get_router(self) -> Optional[APIRouter]:
        pass
    
    @abstractmethod
    async def initialize(self):
        pass
    
    @abstractmethod
    async def shutdown(self):
        pass
    
    def get_metadata(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "enabled": self.enabled
        }

class BasePlugin(PluginInterface):
    def __init__(self):
        super().__init__()
        self._router: Optional[APIRouter] = None
    
    def get_router(self) -> Optional[APIRouter]:
        return self._router
    
    async def initialize(self):
        pass
    
    async def shutdown(self):
        pass
    
    def register_event_listeners(self, event_bus):
        pass
    
    def create_router(self, prefix: str, tags: list[str]) -> APIRouter:
        self._router = APIRouter(prefix=prefix, tags=tags)
        return self._router

