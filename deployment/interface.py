from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ServiceType(Enum):
    """Types of services that can be deployed"""
    WEB = "web"
    WORKER = "worker"
    CRON = "cron"
    STATIC = "static"
    CACHE = "cache"
    DATABASE = "database"


@dataclass
class ResourceSpec:
    """Resource specifications for a service"""
    cpu: Optional[str] = None  # e.g., "1", "2", "0.5"
    memory: Optional[str] = None  # e.g., "512MB", "1GB", "2GB"
    storage: Optional[str] = None  # e.g., "1GB", "10GB"
    instances: int = 1
    auto_scale: bool = False
    min_instances: int = 1
    max_instances: int = 10


@dataclass
class HealthCheck:
    """Health check configuration"""
    path: str = "/health"
    interval: int = 30  # seconds
    timeout: int = 10  # seconds
    unhealthy_threshold: int = 3
    healthy_threshold: int = 2


@dataclass
class BuildConfig:
    """Build configuration"""
    command: str
    dockerfile: Optional[str] = None
    build_args: Optional[Dict[str, str]] = None


@dataclass
class ServiceDefinition:
    """Abstract service definition"""
    name: str
    type: ServiceType
    runtime: Optional[str] = None  # e.g., "python", "node", "go"
    version: Optional[str] = None  # e.g., "3.11", "18", "1.20"
    build_command: Optional[str] = None
    start_command: Optional[str] = None
    env_vars: Optional[Dict[str, str]] = None
    secrets: Optional[List[str]] = None  # Secret keys to be set
    resources: Optional[ResourceSpec] = None
    health_check: Optional[HealthCheck] = None
    region: str = "us-west"
    custom_config: Optional[Dict[str, Any]] = None


class DeploymentProviderInterface(ABC):
    """Abstract interface for deployment providers"""
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of this deployment provider"""
        pass
    
    @abstractmethod
    def generate_config(
        self,
        services: List[ServiceDefinition],
        output_path: str = "."
    ) -> str:
        """
        Generate provider-specific configuration file(s).
        
        Args:
            services: List of service definitions
            output_path: Path where config files should be written
        
        Returns:
            Path to generated config file(s)
        """
        pass
    
    @abstractmethod
    def validate_config(self, config_path: str) -> bool:
        """
        Validate provider-specific configuration.
        
        Args:
            config_path: Path to config file
        
        Returns:
            True if valid, False otherwise
        """
        pass
    
    @abstractmethod
    def get_required_env_vars(self, service: ServiceDefinition) -> List[str]:
        """
        Get list of required environment variables for a service.
        
        Args:
            service: Service definition
        
        Returns:
            List of required environment variable names
        """
        pass
    
    @abstractmethod
    def supports_service_type(self, service_type: ServiceType) -> bool:
        """
        Check if provider supports a service type.
        
        Args:
            service_type: Type of service
        
        Returns:
            True if supported, False otherwise
        """
        pass

