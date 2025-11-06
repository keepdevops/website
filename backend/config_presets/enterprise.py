"""
Enterprise Configuration Preset.
Total cost: ~$500+/month with best-in-class features and SLAs.
"""
from config_presets.interface import PresetConfig


enterprise_preset = PresetConfig(
    name="enterprise-production",
    description="Enterprise-grade with best features and SLAs - $500+/month",
    estimated_monthly_cost=500.00,
    
    # Provider selections (best features, SLAs, support)
    cache_provider="redis",                # Dedicated Redis instance
    storage_provider="aws_s3",             # Enterprise features, compliance
    email_provider="sendgrid",             # Enterprise tier, dedicated IPs
    sms_provider="twilio",                 # Best deliverability, global reach
    payment_provider="adyen",              # Enterprise, 250+ payment methods
    push_notification_provider="firebase", # Google infrastructure, unlimited
    logging_provider="datadog",            # Full observability platform
    monitoring_providers="sentry",         # Production error tracking
    analytics_providers="google_analytics,posthog",  # GA4 + product analytics
    rate_limit_provider="redis",           # Dedicated, distributed
    
    # Cost breakdown
    provider_settings={
        "cost_breakdown": {
            "cache": 50.00,  # Dedicated Redis
            "storage": 50.00,  # AWS S3 with high traffic
            "email": 100.00,  # SendGrid Pro
            "sms": 50.00,  # Twilio usage
            "payment": 0.00,  # Custom Adyen pricing
            "push_notifications": 0.00,  # Firebase free
            "logging": 150.00,  # Datadog APM
            "monitoring": 50.00,  # Sentry Business
            "analytics": 50.00,  # PostHog + GA4
            "rate_limiting": 0.00  # Included with Redis
        },
        "benefits": {
            "uptime_sla": "99.99%",
            "support_tier": "Enterprise 24/7",
            "compliance": "SOC 2, GDPR, HIPAA ready",
            "scalability": "Unlimited",
            "features": "All advanced features enabled"
        },
        "assumptions": {
            "storage": "500GB + high bandwidth",
            "email": "50,000 emails/month",
            "sms": "5,000 messages/month",
            "transactions": "$500k+/month volume",
            "users": "100,000+ active"
        }
    },
    
    # Environment variables
    environment_vars={
        # Dedicated Redis
        "REDIS_URL": "redis://redis-dedicated.yourapp.com:6379",
        
        # AWS S3
        "AWS_ACCESS_KEY_ID": "your_access_key",
        "AWS_SECRET_ACCESS_KEY": "your_secret_key",
        "AWS_REGION": "us-east-1",
        "AWS_S3_BUCKET": "enterprise-production",
        
        # SendGrid Enterprise
        "SENDGRID_API_KEY": "SG.your_enterprise_key",
        
        # Twilio
        "TWILIO_ACCOUNT_SID": "AC_your_sid",
        "TWILIO_AUTH_TOKEN": "your_token",
        "TWILIO_PHONE_NUMBER": "+1234567890",
        
        # Adyen
        "ADYEN_API_KEY": "your_api_key",
        "ADYEN_MERCHANT_ACCOUNT": "YourCompanyECOM",
        "ADYEN_ENVIRONMENT": "live",
        
        # Firebase
        "FIREBASE_CREDENTIALS_PATH": "/app/firebase-adminsdk.json",
        "FIREBASE_PROJECT_ID": "your-project",
        
        # Datadog
        "DATADOG_API_KEY": "your_datadog_key",
        "DATADOG_APP_KEY": "your_app_key",
        "DATADOG_SITE": "datadoghq.com",
        
        # Sentry
        "SENTRY_DSN": "https://key@sentry.io/project",
        "SENTRY_TRACES_SAMPLE_RATE": "1.0",  # Full tracing
        
        # PostHog + GA4
        "POSTHOG_API_KEY": "phc_your_key",
        "GOOGLE_ANALYTICS_MEASUREMENT_ID": "G-XXXXXXXXXX",
        "GOOGLE_ANALYTICS_API_SECRET": "your_secret",
    }
)

