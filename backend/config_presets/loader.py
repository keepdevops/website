"""
Configuration preset loader and applier.
Load and apply preset configurations to the application.
"""
from typing import Optional, Dict, Any
from config_presets.interface import PresetConfig
from config_presets.cost_optimized import cost_optimized_preset
from config_presets.startup_free import startup_free_preset
from config_presets.enterprise import enterprise_preset


# Registry of available presets
PRESETS: Dict[str, PresetConfig] = {
    "cost-optimized": cost_optimized_preset,
    "startup-free": startup_free_preset,
    "enterprise": enterprise_preset,
}


def get_preset(name: str) -> PresetConfig:
    """
    Get preset configuration by name.
    
    Args:
        name: Preset name
        
    Returns:
        PresetConfig instance
        
    Raises:
        ValueError: If preset not found
    """
    if name not in PRESETS:
        available = ", ".join(PRESETS.keys())
        raise ValueError(
            f"Unknown preset: {name}. Available presets: {available}"
        )
    
    return PRESETS[name]


def list_presets() -> Dict[str, Dict[str, Any]]:
    """
    List all available presets with summary info.
    
    Returns:
        Dictionary of preset summaries
    """
    return {
        name: {
            "description": preset.description,
            "monthly_cost": preset.estimated_monthly_cost,
            "providers": {
                "cache": preset.cache_provider,
                "storage": preset.storage_provider,
                "email": preset.email_provider,
                "sms": preset.sms_provider,
                "payment": preset.payment_provider,
                "push": preset.push_notification_provider,
                "logging": preset.logging_provider,
                "monitoring": preset.monitoring_providers,
                "analytics": preset.analytics_providers,
                "rate_limit": preset.rate_limit_provider,
            }
        }
        for name, preset in PRESETS.items()
    }


def get_preset_comparison() -> Dict[str, Any]:
    """
    Compare all presets side-by-side.
    
    Returns:
        Comparison dictionary with costs and providers
    """
    comparison = {}
    
    for name, preset in PRESETS.items():
        comparison[name] = {
            "cost": preset.estimated_monthly_cost,
            "cache": preset.cache_provider,
            "storage": preset.storage_provider,
            "email": preset.email_provider,
            "payment": preset.payment_provider,
            "logging": preset.logging_provider,
        }
    
    return comparison


def apply_preset_to_env_file(
    preset_name: str,
    output_file: str = ".env.preset",
    include_placeholders: bool = True
) -> str:
    """
    Generate .env file from preset configuration.
    
    Args:
        preset_name: Name of preset to apply
        output_file: Output file path
        include_placeholders: Include placeholder values for secrets
        
    Returns:
        Path to generated .env file
    """
    preset = get_preset(preset_name)
    env_dict = preset.to_env_dict()
    
    with open(output_file, 'w') as f:
        f.write(f"# Generated from preset: {preset.name}\n")
        f.write(f"# {preset.description}\n")
        f.write(f"# Estimated monthly cost: ${preset.estimated_monthly_cost}\n\n")
        
        for key, value in env_dict.items():
            f.write(f"{key}={value}\n")
        
        if include_placeholders and preset.environment_vars:
            f.write("\n# Provider-specific settings (replace with actual values)\n")
            for key, value in preset.environment_vars.items():
                f.write(f"{key}={value}\n")
    
    return output_file

