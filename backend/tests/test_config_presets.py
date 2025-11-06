"""
Tests for configuration preset system.
"""
import pytest
from config_presets.interface import PresetConfig
from config_presets.loader import get_preset, list_presets, PRESETS
from config_presets.cost_calculator import CostCalculator


class TestPresetInterface:
    """Test preset interface"""
    
    def test_preset_to_env_dict(self):
        """Test converting preset to environment variables"""
        preset = PresetConfig(
            name="test",
            description="Test preset",
            estimated_monthly_cost=50.00,
            cache_provider="redis",
            storage_provider="aws_s3",
            email_provider="sendgrid",
            sms_provider="twilio",
            payment_provider="stripe",
            push_notification_provider="onesignal",
            logging_provider="console",
            monitoring_providers="sentry",
            analytics_providers="posthog",
            rate_limit_provider="redis"
        )
        
        env_dict = preset.to_env_dict()
        
        assert env_dict["CACHE_PROVIDER"] == "redis"
        assert env_dict["STORAGE_PROVIDER"] == "aws_s3"
        assert env_dict["PAYMENT_PROVIDER"] == "stripe"


class TestPresetLoader:
    """Test preset loader"""
    
    def test_get_preset_cost_optimized(self):
        """Test loading cost-optimized preset"""
        preset = get_preset("cost-optimized")
        
        assert preset.name == "cost-optimized-production"
        assert preset.storage_provider == "cloudflare_r2"
        assert preset.payment_provider == "square"
        assert preset.estimated_monthly_cost == 97.50
    
    def test_get_preset_startup_free(self):
        """Test loading startup free preset"""
        preset = get_preset("startup-free")
        
        assert preset.name == "startup-free-tier"
        assert preset.estimated_monthly_cost == 0.00
        assert preset.sms_provider == "console"
    
    def test_get_preset_enterprise(self):
        """Test loading enterprise preset"""
        preset = get_preset("enterprise")
        
        assert preset.name == "enterprise-production"
        assert preset.logging_provider == "datadog"
        assert preset.estimated_monthly_cost == 500.00
    
    def test_invalid_preset(self):
        """Test error on invalid preset"""
        with pytest.raises(ValueError, match="Unknown preset"):
            get_preset("nonexistent")
    
    def test_list_presets(self):
        """Test listing all presets"""
        presets = list_presets()
        
        assert "cost-optimized" in presets
        assert "startup-free" in presets
        assert "enterprise" in presets
        assert len(presets) == 3


class TestCostCalculator:
    """Test cost calculator"""
    
    def test_calculate_preset_cost(self):
        """Test cost calculation"""
        calc = CostCalculator()
        
        config = {
            "cache": "upstash",
            "storage": "cloudflare_r2",
            "email": "resend"
        }
        
        result = calc.calculate_preset_cost(config)
        
        assert "total_monthly_cost" in result
        assert "breakdown" in result
        assert result["total_monthly_cost"] > 0
    
    def test_compare_providers(self):
        """Test provider comparison"""
        calc = CostCalculator()
        
        storage_costs = calc.compare_providers("storage")
        
        assert "cloudflare_r2" in storage_costs
        assert "aws_s3" in storage_costs
        # R2 should be cheaper than S3
        assert storage_costs["cloudflare_r2"] < storage_costs["aws_s3"]
    
    def test_savings_report(self):
        """Test savings calculation"""
        calc = CostCalculator()
        
        expensive = {"storage": "aws_s3", "email": "sendgrid"}
        cheap = {"storage": "cloudflare_r2", "email": "resend"}
        
        report = calc.get_savings_report(expensive, cheap)
        
        assert report["monthly_savings"] > 0
        assert report["savings_percent"] > 0
        assert report["annual_savings"] == report["monthly_savings"] * 12


def test_all_presets_have_required_providers():
    """Verify all presets configure all required providers"""
    required_providers = [
        "cache_provider", "storage_provider", "email_provider", 
        "sms_provider", "payment_provider", "push_notification_provider",
        "logging_provider", "monitoring_providers", "analytics_providers",
        "rate_limit_provider"
    ]
    
    for preset_name, preset in PRESETS.items():
        for provider_attr in required_providers:
            assert hasattr(preset, provider_attr), f"{preset_name} missing {provider_attr}"
            assert getattr(preset, provider_attr), f"{preset_name} has empty {provider_attr}"

