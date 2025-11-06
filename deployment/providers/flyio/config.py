import toml
import os
from typing import List, Dict, Any
from deployment.interface import (
    DeploymentProviderInterface,
    ServiceDefinition,
    ServiceType
)


class FlyioDeploymentProvider(DeploymentProviderInterface):
    """Fly.io deployment provider"""
    
    @property
    def provider_name(self) -> str:
        return "flyio"
    
    def generate_config(
        self,
        services: List[ServiceDefinition],
        output_path: str = "."
    ) -> str:
        """Generate fly.toml configuration file"""
        config = {
            "app": "",
            "primary_region": "sea",
            "build": {},
            "deploy": {},
            "env": {},
            "http_service": {},
            "vm": {}
        }
        
        for service in services:
            if not self.supports_service_type(service.type):
                print(f"Warning: Fly.io does not support {service.type.value} type well")
                continue
            
            if service.type == ServiceType.WEB:
                config["app"] = service.name
                config["primary_region"] = self._convert_region(service.region)
                
                # Build configuration
                if service.build_command:
                    config["build"]["builder"] = "paketobuildpacks/builder:base"
                
                # HTTP service configuration
                config["http_service"] = {
                    "internal_port": 8080,
                    "force_https": True,
                    "auto_stop_machines": True,
                    "auto_start_machines": True,
                    "min_machines_running": 0
                }
                
                # Add health check
                if service.health_check:
                    config["http_service"]["checks"] = [{
                        "grace_period": "5s",
                        "interval": f"{service.health_check.interval}s",
                        "method": "GET",
                        "timeout": f"{service.health_check.timeout}s",
                        "path": service.health_check.path
                    }]
                
                # VM resources
                if service.resources:
                    config["vm"] = self._build_vm_config(service)
                
                # Environment variables (non-secret)
                if service.env_vars:
                    config["env"] = service.env_vars
        
        # Write to fly.toml
        output_file = os.path.join(output_path, "fly.toml")
        with open(output_file, 'w') as f:
            toml.dump(config, f)
        
        print(f"Generated Fly.io configuration: {output_file}")
        return output_file
    
    def _convert_region(self, region: str) -> str:
        """Convert generic region to Fly.io region code"""
        region_map = {
            "us-west": "sea",  # Seattle
            "us-east": "iad",  # Ashburn
            "eu-west": "ams",  # Amsterdam
            "asia-pacific": "sin"  # Singapore
        }
        return region_map.get(region, "sea")
    
    def _build_vm_config(self, service: ServiceDefinition) -> Dict[str, Any]:
        """Build VM configuration based on resources"""
        vm_config = {}
        
        if service.resources:
            # Parse memory (e.g., "512MB" -> 512)
            if service.resources.memory:
                memory_str = service.resources.memory.replace("MB", "").replace("GB", "000")
                vm_config["memory"] = f"{memory_str}mb"
            
            # Parse CPU
            if service.resources.cpu:
                vm_config["cpus"] = int(float(service.resources.cpu))
        
        return vm_config or {"memory": "256mb", "cpus": 1}
    
    def validate_config(self, config_path: str) -> bool:
        """Validate fly.toml configuration"""
        try:
            with open(config_path, 'r') as f:
                config = toml.load(f)
            
            # Check required fields
            if "app" not in config or not config["app"]:
                print("Error: 'app' name is required in fly.toml")
                return False
            
            print(f"Fly.io configuration is valid: {config_path}")
            return True
        
        except toml.TomlDecodeError as e:
            print(f"Error: Invalid TOML in Fly.io config: {str(e)}")
            return False
        except Exception as e:
            print(f"Error validating Fly.io config: {str(e)}")
            return False
    
    def get_required_env_vars(self, service: ServiceDefinition) -> List[str]:
        """Get required environment variables for Fly.io"""
        required = []
        
        # Fly.io provides FLY_APP_NAME, FLY_REGION, etc. automatically
        
        if service.secrets:
            required.extend(service.secrets)
        
        return required
    
    def supports_service_type(self, service_type: ServiceType) -> bool:
        """Check if Fly.io supports this service type"""
        supported = {
            ServiceType.WEB,
            ServiceType.WORKER,
            ServiceType.CACHE,  # Via Fly.io Redis (Upstash)
            ServiceType.DATABASE  # Via Fly.io Postgres
        }
        return service_type in supported

