import yaml
import os
from typing import List
from deployment.interface import (
    DeploymentProviderInterface,
    ServiceDefinition,
    ServiceType
)
from .services import RenderServiceBuilder


class RenderDeploymentProvider(DeploymentProviderInterface):
    """Render.com deployment provider"""
    
    def __init__(self):
        self.service_builder = RenderServiceBuilder()
    
    @property
    def provider_name(self) -> str:
        return "render"
    
    def generate_config(
        self,
        services: List[ServiceDefinition],
        output_path: str = "."
    ) -> str:
        """Generate render.yaml configuration file"""
        config = {"services": []}
        
        for service in services:
            if not self.supports_service_type(service.type):
                print(f"Warning: Render does not support {service.type.value} type directly")
                continue
            
            if service.type == ServiceType.WEB:
                config["services"].append(
                    self.service_builder.build_web_service(service)
                )
            elif service.type == ServiceType.CACHE:
                config["services"].append(
                    self.service_builder.build_cache_service(service)
                )
        
        # Write to render.yaml
        output_file = os.path.join(output_path, "render.yaml")
        with open(output_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        print(f"Generated Render configuration: {output_file}")
        return output_file
    
    def validate_config(self, config_path: str) -> bool:
        """Validate render.yaml configuration"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            if "services" not in config:
                print("Error: 'services' key required in render.yaml")
                return False
            
            for service in config["services"]:
                if "type" not in service:
                    print(f"Error: Service missing 'type' field: {service.get('name', 'unknown')}")
                    return False
                
                if "name" not in service:
                    print(f"Error: Service missing 'name' field")
                    return False
            
            print(f"Render configuration is valid: {config_path}")
            return True
        
        except Exception as e:
            print(f"Error validating Render config: {str(e)}")
            return False
    
    def get_required_env_vars(self, service: ServiceDefinition) -> List[str]:
        """Get required environment variables for Render"""
        required = []
        
        if service.type == ServiceType.WEB:
            if service.runtime == "python":
                required.append("PYTHON_VERSION")
            elif service.runtime == "node":
                required.append("NODE_VERSION")
        
        # Add service-specific secrets
        if service.secrets:
            required.extend(service.secrets)
        
        return required
    
    def supports_service_type(self, service_type: ServiceType) -> bool:
        """Check if Render supports this service type"""
        supported = {
            ServiceType.WEB,
            ServiceType.WORKER,
            ServiceType.CRON,
            ServiceType.CACHE,
            ServiceType.DATABASE
        }
        return service_type in supported

