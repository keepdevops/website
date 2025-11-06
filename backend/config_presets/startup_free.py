"""
Startup/Free Tier Configuration Preset.
Total cost: ~$0/month using all free tiers - perfect for MVP.
"""
from config_presets.interface import PresetConfig


startup_free_preset = PresetConfig(
    name="startup-free-tier",
    description="Free tier maximization for startups and MVPs - $0/month",
    estimated_monthly_cost=0.00,
    
    # Provider selections (all free tiers)
    cache_provider="memory",              # FREE (not for multi-instance)
    storage_provider="supabase",          # FREE 1GB storage + 2GB bandwidth
    email_provider="resend",              # FREE 3,000 emails/month
    sms_provider="console",               # FREE (console logging only)
    payment_provider="stripe",            # FREE (pay transaction fees only)
    push_notification_provider="onesignal", # FREE up to 30,000 users
    logging_provider="console",           # FREE (stdout/stderr)
    monitoring_providers="console",       # FREE (console logging)
    analytics_providers="internal",       # FREE (database-based)
    rate_limit_provider="memory",         # FREE (in-memory)
    
    # Cost breakdown
    provider_settings={
        "cost_breakdown": {
            "cache": 0.00,
            "storage": 0.00,  # Within free tier
            "email": 0.00,  # Under 3,000/month
            "sms": 0.00,  # Console only
            "payment": 0.00,  # Transaction fees only
            "push_notifications": 0.00,
            "logging": 0.00,
            "monitoring": 0.00,
            "analytics": 0.00,
            "rate_limiting": 0.00
        },
        "limitations": {
            "cache": "Single instance only (not distributed)",
            "storage": "1GB storage limit",
            "email": "3,000 emails/month limit",
            "sms": "Development only, no real SMS",
            "push": "30,000 users limit",
            "rate_limiting": "Single instance only"
        },
        "assumptions": {
            "storage": "Under 1GB",
            "email": "Under 3,000/month",
            "users": "Under 30,000",
            "traffic": "Low to medium"
        }
    },
    
    # Environment variables (mostly using defaults)
    environment_vars={
        # Supabase (free tier)
        "SUPABASE_URL": "https://your-project.supabase.co",
        "SUPABASE_ANON_KEY": "your_anon_key",
        "SUPABASE_SERVICE_KEY": "your_service_key",
        "SUPABASE_STORAGE_BUCKET": "uploads",
        
        # Resend Email (free 3k/month)
        "RESEND_API_KEY": "re_your_key",
        
        # Stripe (free, pay-as-go)
        "STRIPE_SECRET_KEY": "sk_test_your_key",
        "STRIPE_PUBLISHABLE_KEY": "pk_test_your_key",
        "STRIPE_WEBHOOK_SECRET": "whsec_your_secret",
        
        # OneSignal (free up to 30k users)
        "ONESIGNAL_APP_ID": "your_app_id",
        "ONESIGNAL_API_KEY": "your_api_key",
    }
)

