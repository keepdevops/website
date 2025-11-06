"""
CLI tool for managing configuration presets.
Use: python -m config_presets.cli [command]
"""
import sys
import argparse
from config_presets.loader import get_preset, list_presets, apply_preset_to_env_file, get_preset_comparison
from config_presets.cost_calculator import CostCalculator


def cmd_list_presets():
    """List all available presets"""
    presets = list_presets()
    
    print("\n" + "="*70)
    print("AVAILABLE CONFIGURATION PRESETS")
    print("="*70 + "\n")
    
    for name, info in presets.items():
        print(f"📦 {name}")
        print(f"   {info['description']}")
        print(f"   💰 Monthly Cost: ${info['monthly_cost']:.2f}")
        print(f"   Providers: {', '.join(f'{k}={v}' for k, v in list(info['providers'].items())[:3])}")
        print()


def cmd_show_preset(preset_name: str):
    """Show detailed preset configuration"""
    preset = get_preset(preset_name)
    
    print("\n" + "="*70)
    print(f"PRESET: {preset.name.upper()}")
    print("="*70)
    print(f"\n{preset.description}")
    print(f"\n💰 Estimated Monthly Cost: ${preset.estimated_monthly_cost:.2f}\n")
    
    print("Provider Configuration:")
    print(f"  Cache:           {preset.cache_provider}")
    print(f"  Storage:         {preset.storage_provider}")
    print(f"  Email:           {preset.email_provider}")
    print(f"  SMS:             {preset.sms_provider}")
    print(f"  Payment:         {preset.payment_provider}")
    print(f"  Push:            {preset.push_notification_provider}")
    print(f"  Logging:         {preset.logging_provider}")
    print(f"  Monitoring:      {preset.monitoring_providers}")
    print(f"  Analytics:       {preset.analytics_providers}")
    print(f"  Rate Limiting:   {preset.rate_limit_provider}")
    
    if "cost_breakdown" in preset.provider_settings:
        print("\n💵 Cost Breakdown:")
        for service, cost in preset.provider_settings["cost_breakdown"].items():
            if cost > 0:
                print(f"  {service:20} ${cost:.2f}")
    
    print()


def cmd_generate_env(preset_name: str, output_file: str = ".env.preset"):
    """Generate .env file from preset"""
    file_path = apply_preset_to_env_file(preset_name, output_file)
    print(f"\n✅ Generated {file_path} from preset: {preset_name}")
    print(f"   Review and update with your actual API keys, then rename to .env\n")


def cmd_compare_presets():
    """Compare all presets"""
    comparison = get_preset_comparison()
    
    print("\n" + "="*70)
    print("PRESET COMPARISON")
    print("="*70 + "\n")
    
    print(f"{'Preset':<25} {'Cost':<12} {'Storage':<15} {'Payment':<10}")
    print("-" * 70)
    
    for name, data in comparison.items():
        print(f"{name:<25} ${data['cost']:<11.2f} {data['storage']:<15} {data['payment']:<10}")
    
    print()


def cmd_calculate_savings():
    """Show savings of cost-optimized vs expensive"""
    calc = CostCalculator()
    
    expensive_config = {
        "storage": "aws_s3",
        "email": "sendgrid",
        "sms": "twilio",
        "logging": "datadog"
    }
    
    optimized_config = {
        "storage": "cloudflare_r2",
        "email": "resend",
        "sms": "vonage",
        "logging": "betterstack"
    }
    
    report = calc.get_savings_report(expensive_config, optimized_config)
    
    print("\n" + "="*70)
    print("COST OPTIMIZATION REPORT")
    print("="*70 + "\n")
    print(f"Current (Expensive):     ${report['current_cost']:.2f}/month")
    print(f"Optimized:               ${report['optimized_cost']:.2f}/month")
    print(f"Monthly Savings:         ${report['monthly_savings']:.2f}")
    print(f"Annual Savings:          ${report['annual_savings']:.2f}")
    print(f"Savings Percentage:      {report['savings_percent']:.1f}%")
    print()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Manage configuration presets for cost-optimized plugin selection"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # List command
    subparsers.add_parser("list", help="List all available presets")
    
    # Show command
    show_parser = subparsers.add_parser("show", help="Show preset details")
    show_parser.add_argument("preset", help="Preset name")
    
    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate .env file")
    gen_parser.add_argument("preset", help="Preset name")
    gen_parser.add_argument("-o", "--output", default=".env.preset", help="Output file")
    
    # Compare command
    subparsers.add_parser("compare", help="Compare all presets")
    
    # Savings command
    subparsers.add_parser("savings", help="Show cost savings report")
    
    args = parser.parse_args()
    
    if args.command == "list":
        cmd_list_presets()
    elif args.command == "show":
        cmd_show_preset(args.preset)
    elif args.command == "generate":
        cmd_generate_env(args.preset, args.output)
    elif args.command == "compare":
        cmd_compare_presets()
    elif args.command == "savings":
        cmd_calculate_savings()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

