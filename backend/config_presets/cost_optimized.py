"""
Cost-Optimized Production Configuration Preset.
Total cost: ~$97.50/month with maximum savings and quality.
"""
from config_presets.interface import PresetConfig


cost_optimized_preset = PresetConfig(
    name="cost-optimized-production",
    description="Production-ready with optimal cost/performance ratio - $97.50/month",
    estimated_monthly_cost=97.50,
    
    # Provider selections (best value for money)
    cache_provider="upstash",              # $10/month, serverless
    storage_provider="cloudflare_r2",      # $1.50/month, zero egress fees (97% savings!)
    email_provider="resend",               # $20/month, modern API
    sms_provider="vonage",                 # Pay-as-go, 33% cheaper than Twilio
    payment_provider="square",             # 2.6% vs 2.9% (18% savings on fees)
    push_notification_provider="onesignal", # FREE for up to 30k users
    logging_provider="betterstack",        # $20/month, modern log management
    monitoring_providers="sentry",         # $26/month, error tracking
    analytics_providers="posthog",         # $20/month, product analytics
    rate_limit_provider="upstash",         # Included with cache (FREE)
    
    # Cost breakdown by service
    provider_settings={
        "cost_breakdown": {
            "cache": 10.00,
            "storage": 1.50,
            "email": 20.00,
            "sms": 0.00,  # Pay-as-go (estimated $5-15/month)
            "payment": 0.00,  # Transaction fees only (2.6%)
            "push_notifications": 0.00,  # FREE tier
            "logging": 20.00,
            "monitoring": 26.00,
            "analytics": 20.00,
            "rate_limiting": 0.00  # Included
        },
        "savings_vs_expensive": {
            "storage_savings": 45.80,  # R2 vs S3
            "payment_fee_savings": 18,  # % lower fees
            "sms_savings": 33,  # % vs Twilio
            "total_monthly_savings": 100.00  # vs expensive stack
        },
        "assumptions": {
            "storage": "100GB + 500GB egress/month",
            "email": "10,000 emails/month",
            "sms": "1,000 messages/month",
            "transactions": "$100,000/month volume",
            "users": "Under 30,000 active"
        }
    },
    
    # Environment variables for this preset
    environment_vars={
        # Upstash Cache + Rate Limiting
        "UPSTASH_REDIS_REST_URL": "https://your-db.upstash.io",
        "UPSTASH_REDIS_REST_TOKEN": "your_token",
        
        # Cloudflare R2 Storage (zero egress!)
        "S3_ENDPOINT_URL": "https://your-account.r2.cloudflarestorage.com",
        "AWS_ACCESS_KEY_ID": "your_r2_access_key",
        "AWS_SECRET_ACCESS_KEY": "your_r2_secret",
        "AWS_S3_BUCKET": "production-uploads",
        "CDN_DOMAIN": "cdn.yourapp.com",
        
        # Resend Email
        "RESEND_API_KEY": "re_your_key",
        
        # Vonage SMS
        "VONAGE_API_KEY": "your_api_key",
        "VONAGE_API_SECRET": "your_secret",
        "VONAGE_PHONE_NUMBER": "+1234567890",
        
        # Square Payments (lower fees)
        "SQUARE_ACCESS_TOKEN": "your_token",
        "SQUARE_ENVIRONMENT": "production",
        "SQUARE_LOCATION_ID": "your_location",
        
        # OneSignal Push (FREE)
        "ONESIGNAL_APP_ID": "your_app_id",
        "ONESIGNAL_API_KEY": "your_api_key",
        
        # Better Stack Logging
        "BETTERSTACK_SOURCE_TOKEN": "your_token",
        
        # Sentry Monitoring
        "SENTRY_DSN": "https://your_key@sentry.io/project",
        "SENTRY_TRACES_SAMPLE_RATE": "0.1",
        
        # PostHog Analytics
        "POSTHOG_API_KEY": "phc_your_key",
        "POSTHOG_HOST": "https://app.posthog.com",
    }
)

