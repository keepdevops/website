"""
Cost calculator for plugin provider configurations.
Estimates monthly costs based on usage patterns.
"""
from typing import Dict, Any


class CostCalculator:
    """Calculate estimated costs for provider configurations"""
    
    # Base pricing for each provider (monthly)
    PROVIDER_COSTS = {
        # Cache
        "redis": 50.00,  # Dedicated instance
        "upstash": 10.00,  # Serverless tier
        "memory": 0.00,
        
        # Storage (base + egress for 100GB + 500GB)
        "aws_s3": 47.30,
        "cloudflare_r2": 1.50,  # Zero egress!
        "digitalocean_spaces": 5.00,
        "backblaze_b2": 5.50,
        "supabase": 0.00,  # Free tier
        "gcs": 62.00,
        
        # Email (per 10k emails/month)
        "sendgrid": 20.00,
        "mailgun": 15.00,
        "postmark": 15.00,
        "aws_ses": 1.00,
        "resend": 20.00,
        
        # SMS (pay-as-go, estimated 1k msgs)
        "twilio": 7.50,
        "vonage": 5.00,
        "aws_sns": 6.45,
        "messagebird": 6.00,
        "console": 0.00,
        
        # Payment (transaction fees only, no monthly)
        "stripe": 0.00,  # 2.9% + $0.30 per transaction
        "paypal": 0.00,  # 2.9% + $0.30 per transaction
        "square": 0.00,  # 2.6% + $0.10 per transaction
        "braintree": 0.00,  # 2.9% + $0.30 per transaction
        "adyen": 0.00,  # Custom enterprise pricing
        
        # Push Notifications
        "onesignal": 0.00,  # Free up to 30k users
        "firebase": 0.00,  # Free unlimited
        "aws_sns_push": 10.00,
        "pusher": 20.00,
        "webpush": 0.00,
        
        # Logging
        "console": 0.00,
        "file": 0.00,
        "json": 0.00,
        "datadog": 150.00,  # APM + Logs
        "betterstack": 20.00,
        "cloudwatch": 10.00,
        
        # Monitoring
        "sentry": 26.00,
        
        # Analytics
        "google_analytics": 0.00,
        "posthog": 20.00,
        "internal": 0.00,
    }
    
    def calculate_preset_cost(self, preset_config: Dict[str, str]) -> Dict[str, Any]:
        """Calculate total cost for a preset configuration"""
        total_cost = 0.00
        breakdown = {}
        
        for service, provider in preset_config.items():
            cost = self.PROVIDER_COSTS.get(provider, 0.00)
            breakdown[service] = {
                "provider": provider,
                "cost": cost
            }
            total_cost += cost
        
        return {
            "total_monthly_cost": round(total_cost, 2),
            "breakdown": breakdown
        }
    
    def compare_providers(self, service: str) -> Dict[str, float]:
        """Compare costs for all providers of a specific service"""
        service_providers = {
            k: v for k, v in self.PROVIDER_COSTS.items()
            if self._matches_service(k, service)
        }
        
        sorted_providers = sorted(
            service_providers.items(),
            key=lambda x: x[1]
        )
        
        return dict(sorted_providers)
    
    def _matches_service(self, provider: str, service: str) -> bool:
        """Check if provider belongs to service category"""
        service_mapping = {
            "cache": ["redis", "upstash", "memory"],
            "storage": ["aws_s3", "cloudflare_r2", "digitalocean_spaces", "backblaze_b2", "supabase", "gcs"],
            "email": ["sendgrid", "mailgun", "postmark", "aws_ses", "resend"],
            "sms": ["twilio", "vonage", "aws_sns", "messagebird", "console"],
            "logging": ["console", "file", "json", "datadog", "betterstack", "cloudwatch"],
        }
        
        return provider in service_mapping.get(service, [])
    
    def get_savings_report(
        self,
        current_config: Dict[str, str],
        optimized_config: Dict[str, str]
    ) -> Dict[str, Any]:
        """Compare current vs optimized configuration"""
        current = self.calculate_preset_cost(current_config)
        optimized = self.calculate_preset_cost(optimized_config)
        
        savings = current["total_monthly_cost"] - optimized["total_monthly_cost"]
        savings_percent = (savings / current["total_monthly_cost"] * 100) if current["total_monthly_cost"] > 0 else 0
        
        return {
            "current_cost": current["total_monthly_cost"],
            "optimized_cost": optimized["total_monthly_cost"],
            "monthly_savings": round(savings, 2),
            "savings_percent": round(savings_percent, 1),
            "annual_savings": round(savings * 12, 2)
        }

