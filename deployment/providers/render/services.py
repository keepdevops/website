from typing import Dict, List, Any
from deployment.interface import ServiceDefinition, ServiceType


class RenderServiceBuilder:
    """Build Render-specific service configurations"""
    
    def build_web_service(self, service: ServiceDefinition) -> Dict[str, Any]:
        """Build Render web service configuration"""
        config = {
            "type": "web",
            "name": service.name,
            "env": self._get_runtime_env(service.runtime),
            "region": self._convert_region(service.region),
            "plan": service.custom_config.get("plan", "starter") if service.custom_config else "starter"
        }
        
        if service.build_command:
            config["buildCommand"] = service.build_command
        
        if service.start_command:
            config["startCommand"] = service.start_command
        
        # Add environment variables
        if service.env_vars or service.secrets:
            config["envVars"] = self._build_env_vars(service)
        
        # Add auto-scaling if configured
        if service.resources and service.resources.auto_scale:
            config["autoDeploy"] = True
        
        return config
    
    def build_cache_service(self, service: ServiceDefinition) -> Dict[str, Any]:
        """Build Render Redis configuration"""
        config = {
            "type": "redis",
            "name": service.name,
            "region": self._convert_region(service.region),
            "plan": service.custom_config.get("plan", "starter") if service.custom_config else "starter",
            "ipAllowList": []
        }
        
        return config
    
    def _get_runtime_env(self, runtime: str) -> str:
        """Map generic runtime to Render environment"""
        runtime_map = {
            "python": "python",
            "node": "node",
            "go": "go",
            "ruby": "ruby",
            "docker": "docker"
        }
        return runtime_map.get(runtime, "docker")
    
    def _convert_region(self, region: str) -> str:
        """Convert generic region to Render region"""
        region_map = {
            "us-west": "oregon",
            "us-east": "ohio",
            "eu-west": "frankfurt",
            "asia-pacific": "singapore"
        }
        return region_map.get(region, "oregon")
    
    def _build_env_vars(self, service: ServiceDefinition) -> List[Dict[str, Any]]:
        """Build environment variables list"""
        env_vars = []
        
        # Add regular environment variables
        if service.env_vars:
            for key, value in service.env_vars.items():
                env_vars.append({"key": key, "value": value})
        
        # Add secrets (with sync: false)
        if service.secrets:
            for secret in service.secrets:
                env_vars.append({"key": secret, "sync": False})
        
        return env_vars

