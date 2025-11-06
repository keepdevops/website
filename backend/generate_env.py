#!/usr/bin/env python3
"""
Environment file generator from configuration presets.
Generates .env files optimized for different deployment scenarios.
"""
import sys
from config_presets.loader import get_preset, list_presets


def generate_env_file(preset_name: str, output_file: str = ".env"):
    """Generate .env file from preset"""
    try:
        preset = get_preset(preset_name)
        
        with open(output_file, 'w') as f:
            f.write(f"# ============================================\n")
            f.write(f"# Configuration Preset: {preset.name}\n")
            f.write(f"# {preset.description}\n")
            f.write(f"# Estimated Monthly Cost: ${preset.estimated_monthly_cost:.2f}\n")
            f.write(f"# ============================================\n\n")
            
            f.write("# Environment\n")
            f.write("ENVIRONMENT=production\n\n")
            
            f.write("# Plugin Provider Selections\n")
            env_dict = preset.to_env_dict()
            for key, value in env_dict.items():
                f.write(f"{key}={value}\n")
            
            f.write("\n# Provider-Specific Settings\n")
            f.write("# NOTE: Replace placeholders below with your actual credentials\n\n")
            
            for key, value in preset.environment_vars.items():
                f.write(f"{key}={value}\n")
            
            if "cost_breakdown" in preset.provider_settings:
                f.write("\n# Cost Breakdown (Monthly)\n")
                for service, cost in preset.provider_settings["cost_breakdown"].items():
                    f.write(f"# {service}: ${cost:.2f}\n")
        
        print(f"✅ Generated {output_file}")
        print(f"📝 Preset: {preset.name}")
        print(f"💰 Estimated Cost: ${preset.estimated_monthly_cost:.2f}/month")
        print(f"\n⚠️  Remember to replace placeholder values with your actual API keys!")
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\nAvailable presets:")
        for name in list_presets().keys():
            print(f"  - {name}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_env.py <preset_name> [output_file]")
        print("\nAvailable presets:")
        for name, info in list_presets().items():
            print(f"  {name:20} - ${info['monthly_cost']:.2f}/month")
        sys.exit(1)
    
    preset_name = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else ".env"
    
    generate_env_file(preset_name, output_file)

