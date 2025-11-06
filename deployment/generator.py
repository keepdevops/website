#!/usr/bin/env python3
"""
Deployment Configuration Generator

Generates provider-specific deployment configurations from shared config.yaml
"""

import argparse
import yaml
import sys
from pathlib import Path
from typing import List

from deployment.interface import (
    ServiceDefinition,
    ServiceType,
    ResourceSpec,
    HealthCheck
)
from deployment.providers.render import RenderDeploymentProvider
from deployment.providers.railway import RailwayDeploymentProvider
from deployment.providers.flyio import FlyioDeploymentProvider
from deployment.providers.vercel import VercelDeploymentProvider


class DeploymentGenerator:
    """Generate deployment configurations for different providers"""
    
    def __init__(self, config_path: str = "deployment/config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.providers = {
            "render": RenderDeploymentProvider(),
            "railway": RailwayDeploymentProvider(),
            "flyio": FlyioDeploymentProvider(),
            "vercel": VercelDeploymentProvider()
        }
    
    def _load_config(self) -> dict:
        """Load shared configuration file"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Error: Configuration file not found: {self.config_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Error parsing YAML: {str(e)}")
            sys.exit(1)
    
    def _parse_services(self) -> List[ServiceDefinition]:
        """Parse services from config into ServiceDefinition objects"""
        services = []
        
        for name, service_config in self.config.get("services", {}).items():
            # Parse service type
            service_type = ServiceType(service_config["type"])
            
            # Parse resources if present
            resources = None
            if "resources" in service_config:
                res_config = service_config["resources"]
                resources = ResourceSpec(
                    memory=res_config.get("memory"),
                    instances=res_config.get("instances", 1),
                    auto_scale=res_config.get("auto_scale", False),
                    min_instances=res_config.get("min_instances", 1),
                    max_instances=res_config.get("max_instances", 10)
                )
            
            # Parse health check if present
            health_check = None
            if "health_check" in service_config:
                hc_config = service_config["health_check"]
                health_check = HealthCheck(
                    path=hc_config.get("path", "/health"),
                    interval=hc_config.get("interval", 30),
                    timeout=hc_config.get("timeout", 10)
                )
            
            # Create service definition
            service = ServiceDefinition(
                name=service_config.get("name", name),
                type=service_type,
                runtime=service_config.get("runtime"),
                version=service_config.get("version"),
                build_command=service_config.get("build_command"),
                start_command=service_config.get("start_command"),
                env_vars=service_config.get("env_vars"),
                secrets=service_config.get("secrets"),
                resources=resources,
                health_check=health_check,
                region=service_config.get("region", "us-west"),
                custom_config=service_config.get("custom_config")
            )
            
            services.append(service)
        
        return services
    
    def generate(self, provider: str, output_path: str = ".") -> str:
        """Generate configuration for a specific provider"""
        if provider not in self.providers:
            print(f"Error: Unknown provider '{provider}'")
            print(f"Available providers: {', '.join(self.providers.keys())}")
            sys.exit(1)
        
        services = self._parse_services()
        provider_instance = self.providers[provider]
        
        print(f"\nGenerating {provider} configuration...")
        print(f"Services: {', '.join([s.name for s in services])}")
        
        return provider_instance.generate_config(services, output_path)
    
    def generate_all(self, output_path: str = "."):
        """Generate configurations for all providers"""
        for provider_name in self.providers.keys():
            try:
                self.generate(provider_name, output_path)
            except Exception as e:
                print(f"Error generating {provider_name} config: {str(e)}")
    
    def validate(self, provider: str, config_path: str) -> bool:
        """Validate a provider configuration"""
        if provider not in self.providers:
            print(f"Error: Unknown provider '{provider}'")
            return False
        
        provider_instance = self.providers[provider]
        return provider_instance.validate_config(config_path)


def main():
    parser = argparse.ArgumentParser(
        description="Generate deployment configurations for various providers"
    )
    parser.add_argument(
        "--provider",
        "-p",
        choices=["render", "railway", "flyio", "vercel"],
        help="Deployment provider"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate configurations for all providers"
    )
    parser.add_argument(
        "--output",
        "-o",
        default=".",
        help="Output directory (default: current directory)"
    )
    parser.add_argument(
        "--config",
        "-c",
        default="deployment/config.yaml",
        help="Path to shared configuration file"
    )
    parser.add_argument(
        "--validate",
        help="Validate a configuration file"
    )
    
    args = parser.parse_args()
    
    generator = DeploymentGenerator(args.config)
    
    if args.validate:
        # Validate configuration
        provider = args.provider or "render"
        success = generator.validate(provider, args.validate)
        sys.exit(0 if success else 1)
    
    elif args.all:
        # Generate all configurations
        generator.generate_all(args.output)
    
    elif args.provider:
        # Generate for specific provider
        generator.generate(args.provider, args.output)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

