import json
import os
from typing import List, Dict, Any
from deployment.interface import (
    DeploymentProviderInterface,
    ServiceDefinition,
    ServiceType
)


class RailwayDeploymentProvider(DeploymentProviderInterface):
    """Railway.app deployment provider"""
    
    @property
    def provider_name(self) -> str:
        return "railway"
    
    def generate_config(
        self,
        services: List[ServiceDefinition],
        output_path: str = "."
    ) -> str:
        """Generate railway.json or railway.toml configuration"""
        config = {
            "$schema": "https://railway.app/railway.schema.json",
            "build": {},
            "deploy": {}
        }
        
        for service in services:
            if not self.supports_service_type(service.type):
                print(f"Warning: Railway does not support {service.type.value} type")
                continue
            
            if service.type == ServiceType.WEB:
                config["build"]["builder"] = "NIXPACKS"
                
                if service.build_command:
                    config["build"]["buildCommand"] = service.build_command
                
                if service.start_command:
                    config["deploy"]["startCommand"] = service.start_command
                
                # Add restart policy
                config["deploy"]["restartPolicyType"] = "ON_FAILURE"
                config["deploy"]["restartPolicyMaxRetries"] = 10
        
        # Write to railway.json
        output_file = os.path.join(output_path, "railway.json")
        with open(output_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Also generate nixpacks.toml for build configuration
        self._generate_nixpacks_config(services, output_path)
        
        print(f"Generated Railway configuration: {output_file}")
        return output_file
    
    def _generate_nixpacks_config(
        self,
        services: List[ServiceDefinition],
        output_path: str
    ):
        """Generate nixpacks.toml for build configuration"""
        nixpacks_config = []
        
        for service in services:
            if service.type == ServiceType.WEB and service.runtime:
                if service.runtime == "python":
                    nixpacks_config.append("[phases.setup]")
                    if service.version:
                        nixpacks_config.append(f'nixPkgs = ["python{service.version.replace(".", "")}"]')
                    else:
                        nixpacks_config.append('nixPkgs = ["python311"]')
                
                elif service.runtime == "node":
                    nixpacks_config.append("[phases.setup]")
                    nixpacks_config.append(f'nixPkgs = ["nodejs-{service.version or "20"}_x"]')
        
        if nixpacks_config:
            output_file = os.path.join(output_path, "nixpacks.toml")
            with open(output_file, 'w') as f:
                f.write('\n'.join(nixpacks_config))
            print(f"Generated Nixpacks configuration: {output_file}")
    
    def validate_config(self, config_path: str) -> bool:
        """Validate railway.json configuration"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Railway config is quite flexible, just check it's valid JSON
            print(f"Railway configuration is valid: {config_path}")
            return True
        
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in Railway config: {str(e)}")
            return False
        except Exception as e:
            print(f"Error validating Railway config: {str(e)}")
            return False
    
    def get_required_env_vars(self, service: ServiceDefinition) -> List[str]:
        """Get required environment variables for Railway"""
        required = []
        
        # Railway provides some env vars automatically
        # Like RAILWAY_ENVIRONMENT, RAILWAY_PROJECT_ID, etc.
        
        if service.secrets:
            required.extend(service.secrets)
        
        return required
    
    def supports_service_type(self, service_type: ServiceType) -> bool:
        """Check if Railway supports this service type"""
        supported = {
            ServiceType.WEB,
            ServiceType.WORKER,
            ServiceType.CRON,
            ServiceType.CACHE,  # Via Railway Redis plugin
            ServiceType.DATABASE  # Via Railway database plugins
        }
        return service_type in supported

