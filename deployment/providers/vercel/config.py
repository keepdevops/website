import json
import os
from typing import List, Dict, Any
from deployment.interface import (
    DeploymentProviderInterface,
    ServiceDefinition,
    ServiceType
)


class VercelDeploymentProvider(DeploymentProviderInterface):
    """Vercel deployment provider (for frontend/static sites)"""
    
    @property
    def provider_name(self) -> str:
        return "vercel"
    
    def generate_config(
        self,
        services: List[ServiceDefinition],
        output_path: str = "."
    ) -> str:
        """Generate vercel.json configuration file"""
        config = {
            "version": 2,
            "builds": [],
            "routes": [],
            "env": {},
            "build": {
                "env": {}
            }
        }
        
        for service in services:
            if not self.supports_service_type(service.type):
                print(f"Info: Skipping {service.type.value} - Vercel primarily for frontend")
                continue
            
            if service.type == ServiceType.STATIC:
                # Configure for Next.js or static builds
                framework = service.custom_config.get("framework", "nextjs") if service.custom_config else "nextjs"
                
                if framework == "nextjs":
                    # Next.js is auto-detected, minimal config needed
                    config["framework"] = "nextjs"
                
                # Add build environment variables
                if service.env_vars:
                    for key, value in service.env_vars.items():
                        if key.startswith("NEXT_PUBLIC_"):
                            config["build"]["env"][key] = value
                        else:
                            config["env"][key] = value
                
                # Add build command if specified
                if service.build_command:
                    config["buildCommand"] = service.build_command
                
                # Add output directory
                config["outputDirectory"] = ".next"
        
        # Add rewrites for SPA routing
        config["routes"] = [
            {
                "src": "/api/(.*)",
                "dest": "/api/$1"
            },
            {
                "src": "/(.*)",
                "dest": "/$1"
            }
        ]
        
        # Write to vercel.json
        output_file = os.path.join(output_path, "vercel.json")
        with open(output_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"Generated Vercel configuration: {output_file}")
        return output_file
    
    def validate_config(self, config_path: str) -> bool:
        """Validate vercel.json configuration"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Vercel config is quite flexible
            print(f"Vercel configuration is valid: {config_path}")
            return True
        
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in Vercel config: {str(e)}")
            return False
        except Exception as e:
            print(f"Error validating Vercel config: {str(e)}")
            return False
    
    def get_required_env_vars(self, service: ServiceDefinition) -> List[str]:
        """Get required environment variables for Vercel"""
        required = []
        
        # Vercel automatically provides VERCEL, VERCEL_URL, etc.
        
        if service.secrets:
            required.extend(service.secrets)
        
        return required
    
    def supports_service_type(self, service_type: ServiceType) -> bool:
        """Check if Vercel supports this service type"""
        supported = {
            ServiceType.STATIC,  # Primary use case
            ServiceType.WEB  # Serverless functions
        }
        return service_type in supported

