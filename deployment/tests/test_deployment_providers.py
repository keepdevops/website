import pytest
import os
import tempfile
import yaml
import json
import toml
from pathlib import Path

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


@pytest.fixture
def temp_dir():
    """Create temporary directory for test output"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def web_service():
    """Create a sample web service definition"""
    return ServiceDefinition(
        name="test-backend",
        type=ServiceType.WEB,
        runtime="python",
        version="3.11",
        build_command="pip install -r requirements.txt",
        start_command="uvicorn main:app --host 0.0.0.0 --port $PORT",
        env_vars={"ENVIRONMENT": "test"},
        secrets=["DATABASE_URL", "API_KEY"],
        resources=ResourceSpec(memory="512MB", instances=1, auto_scale=True),
        health_check=HealthCheck(path="/health", interval=30),
        region="us-west"
    )


@pytest.fixture
def cache_service():
    """Create a sample cache service definition"""
    return ServiceDefinition(
        name="test-redis",
        type=ServiceType.CACHE,
        version="7",
        region="us-west"
    )


class TestRenderProvider:
    """Test Render deployment provider"""
    
    def test_provider_name(self):
        """Test provider name"""
        provider = RenderDeploymentProvider()
        assert provider.provider_name == "render"
    
    def test_generate_web_service(self, web_service, temp_dir):
        """Test generating Render web service configuration"""
        provider = RenderDeploymentProvider()
        output_file = provider.generate_config([web_service], temp_dir)
        
        assert os.path.exists(output_file)
        
        with open(output_file, 'r') as f:
            config = yaml.safe_load(f)
        
        assert "services" in config
        assert len(config["services"]) == 1
        
        service = config["services"][0]
        assert service["type"] == "web"
        assert service["name"] == "test-backend"
        assert service["env"] == "python"
    
    def test_generate_cache_service(self, cache_service, temp_dir):
        """Test generating Render Redis configuration"""
        provider = RenderDeploymentProvider()
        output_file = provider.generate_config([cache_service], temp_dir)
        
        with open(output_file, 'r') as f:
            config = yaml.safe_load(f)
        
        service = config["services"][0]
        assert service["type"] == "redis"
        assert service["name"] == "test-redis"
    
    def test_validate_valid_config(self, web_service, temp_dir):
        """Test validating a valid Render configuration"""
        provider = RenderDeploymentProvider()
        output_file = provider.generate_config([web_service], temp_dir)
        
        assert provider.validate_config(output_file) is True
    
    def test_supports_service_types(self):
        """Test service type support"""
        provider = RenderDeploymentProvider()
        
        assert provider.supports_service_type(ServiceType.WEB) is True
        assert provider.supports_service_type(ServiceType.CACHE) is True
        assert provider.supports_service_type(ServiceType.WORKER) is True


class TestRailwayProvider:
    """Test Railway deployment provider"""
    
    def test_provider_name(self):
        """Test provider name"""
        provider = RailwayDeploymentProvider()
        assert provider.provider_name == "railway"
    
    def test_generate_config(self, web_service, temp_dir):
        """Test generating Railway configuration"""
        provider = RailwayDeploymentProvider()
        output_file = provider.generate_config([web_service], temp_dir)
        
        assert os.path.exists(output_file)
        
        with open(output_file, 'r') as f:
            config = json.load(f)
        
        assert "build" in config
        assert "deploy" in config
    
    def test_nixpacks_generation(self, web_service, temp_dir):
        """Test nixpacks.toml generation"""
        provider = RailwayDeploymentProvider()
        provider.generate_config([web_service], temp_dir)
        
        nixpacks_file = os.path.join(temp_dir, "nixpacks.toml")
        assert os.path.exists(nixpacks_file)
    
    def test_validate_valid_config(self, web_service, temp_dir):
        """Test validating a valid Railway configuration"""
        provider = RailwayDeploymentProvider()
        output_file = provider.generate_config([web_service], temp_dir)
        
        assert provider.validate_config(output_file) is True


class TestFlyioProvider:
    """Test Fly.io deployment provider"""
    
    def test_provider_name(self):
        """Test provider name"""
        provider = FlyioDeploymentProvider()
        assert provider.provider_name == "flyio"
    
    def test_generate_config(self, web_service, temp_dir):
        """Test generating Fly.io configuration"""
        provider = FlyioDeploymentProvider()
        output_file = provider.generate_config([web_service], temp_dir)
        
        assert os.path.exists(output_file)
        
        with open(output_file, 'r') as f:
            config = toml.load(f)
        
        assert "app" in config
        assert config["app"] == "test-backend"
        assert "http_service" in config
    
    def test_health_check_configuration(self, web_service, temp_dir):
        """Test health check in Fly.io config"""
        provider = FlyioDeploymentProvider()
        output_file = provider.generate_config([web_service], temp_dir)
        
        with open(output_file, 'r') as f:
            config = toml.load(f)
        
        assert "checks" in config["http_service"]
        check = config["http_service"]["checks"][0]
        assert check["path"] == "/health"
    
    def test_validate_valid_config(self, web_service, temp_dir):
        """Test validating a valid Fly.io configuration"""
        provider = FlyioDeploymentProvider()
        output_file = provider.generate_config([web_service], temp_dir)
        
        assert provider.validate_config(output_file) is True


class TestVercelProvider:
    """Test Vercel deployment provider"""
    
    def test_provider_name(self):
        """Test provider name"""
        provider = VercelDeploymentProvider()
        assert provider.provider_name == "vercel"
    
    def test_generate_config(self, temp_dir):
        """Test generating Vercel configuration"""
        static_service = ServiceDefinition(
            name="test-frontend",
            type=ServiceType.STATIC,
            runtime="node",
            version="20",
            build_command="npm run build",
            env_vars={"NEXT_PUBLIC_API_URL": "https://api.test.com"},
            custom_config={"framework": "nextjs"}
        )
        
        provider = VercelDeploymentProvider()
        output_file = provider.generate_config([static_service], temp_dir)
        
        assert os.path.exists(output_file)
        
        with open(output_file, 'r') as f:
            config = json.load(f)
        
        assert config["version"] == 2
        assert "routes" in config
    
    def test_supports_static_type(self):
        """Test Vercel supports static sites"""
        provider = VercelDeploymentProvider()
        
        assert provider.supports_service_type(ServiceType.STATIC) is True
        assert provider.supports_service_type(ServiceType.WEB) is True

