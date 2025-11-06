"""
Interface for configuration presets.
Defines the structure of preset configurations.
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class PresetConfig:
    """Configuration preset definition"""
    
    name: str
    description: str
    estimated_monthly_cost: float
    
    # All plugin provider selections
    cache_provider: str
    storage_provider: str
    email_provider: str
    sms_provider: str
    payment_provider: str
    push_notification_provider: str
    logging_provider: str
    monitoring_providers: str
    analytics_providers: str
    rate_limit_provider: str
    
    # Provider-specific settings
    provider_settings: Dict[str, Any] = field(default_factory=dict)
    
    # Environment variables to set
    environment_vars: Dict[str, str] = field(default_factory=dict)
    
    def to_env_dict(self) -> Dict[str, str]:
        """Convert preset to environment variable dictionary"""
        env_vars = {
            "CACHE_PROVIDER": self.cache_provider,
            "STORAGE_PROVIDER": self.storage_provider,
            "EMAIL_PROVIDER": self.email_provider,
            "SMS_PROVIDER": self.sms_provider,
            "PAYMENT_PROVIDER": self.payment_provider,
            "PUSH_NOTIFICATION_PROVIDER": self.push_notification_provider,
            "LOGGING_PROVIDER": self.logging_provider,
            "MONITORING_PROVIDERS": self.monitoring_providers,
            "ANALYTICS_PROVIDERS": self.analytics_providers,
            "RATE_LIMIT_PROVIDER": self.rate_limit_provider,
        }
        
        # Add provider-specific settings
        env_vars.update(self.environment_vars)
        
        return env_vars
    
    def get_cost_breakdown(self) -> Dict[str, float]:
        """Get cost breakdown by service"""
        return self.provider_settings.get("cost_breakdown", {})

