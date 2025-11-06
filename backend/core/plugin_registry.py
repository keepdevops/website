import os
import importlib
import inspect
from typing import List, Dict
from fastapi import FastAPI
from core.plugin_interface import PluginInterface
from core.event_bus import get_event_bus
import logging

logger = logging.getLogger(__name__)

class PluginRegistry:
    def __init__(self, app: FastAPI):
        self.app = app
        self.plugins: Dict[str, PluginInterface] = {}
        self.event_bus = get_event_bus()
    
    async def discover_and_load_plugins(self):
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        plugin_dirs = [
            "auth",
            "subscriptions",
            "webhooks",
            "customers",
            "docker_registry",
            "campaigns",
            "analytics",
            "two_factor"
        ]
        
        for plugin_dir in plugin_dirs:
            plugin_path = os.path.join(backend_dir, plugin_dir)
            if os.path.exists(plugin_path):
                await self._load_plugin_from_directory(plugin_dir)
    
    async def _load_plugin_from_directory(self, plugin_name: str):
        try:
            router_module = importlib.import_module(f"{plugin_name}.router")
            
            if hasattr(router_module, "router"):
                self.app.include_router(router_module.router)
                logger.info(f"Loaded router for plugin: {plugin_name}")
            
            for name, obj in inspect.getmembers(router_module):
                if inspect.isclass(obj) and issubclass(obj, PluginInterface) and obj != PluginInterface:
                    plugin_instance = obj()
                    await plugin_instance.initialize()
                    
                    if hasattr(plugin_instance, 'register_event_listeners'):
                        plugin_instance.register_event_listeners(self.event_bus)
                    
                    self.plugins[plugin_name] = plugin_instance
                    logger.info(f"Initialized plugin: {plugin_name}")
        
        except ModuleNotFoundError:
            logger.warning(f"Plugin module not found: {plugin_name}")
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_name}: {str(e)}")
    
    async def reload_plugin(self, plugin_name: str):
        if plugin_name in self.plugins:
            await self.plugins[plugin_name].shutdown()
            del self.plugins[plugin_name]
        
        await self._load_plugin_from_directory(plugin_name)
    
    def get_plugin(self, plugin_name: str) -> PluginInterface:
        return self.plugins.get(plugin_name)
    
    def get_all_plugins(self) -> List[Dict]:
        return [plugin.get_metadata() for plugin in self.plugins.values()]
    
    async def shutdown_all(self):
        for plugin in self.plugins.values():
            await plugin.shutdown()


