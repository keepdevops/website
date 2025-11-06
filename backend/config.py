from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # Environment
    environment: str = "development"
    
    # Stripe
    stripe_secret_key: str
    stripe_webhook_secret: str
    stripe_publishable_key: str
    
    # Payment Provider Selection
    payment_provider: str = "stripe"  # stripe, paypal, square, braintree, adyen
    
    # PayPal
    paypal_client_id: Optional[str] = None
    paypal_client_secret: Optional[str] = None
    paypal_mode: str = "sandbox"  # sandbox or live
    paypal_webhook_id: Optional[str] = None
    
    # Square
    square_access_token: Optional[str] = None
    square_environment: str = "sandbox"  # sandbox or production
    square_location_id: Optional[str] = None
    square_webhook_signature_key: Optional[str] = None
    
    # Braintree
    braintree_merchant_id: Optional[str] = None
    braintree_public_key: Optional[str] = None
    braintree_private_key: Optional[str] = None
    braintree_environment: str = "sandbox"  # sandbox or production
    
    # Adyen
    adyen_api_key: Optional[str] = None
    adyen_merchant_account: Optional[str] = None
    adyen_environment: str = "test"  # test or live
    adyen_client_key: Optional[str] = None
    
    # Email Provider Selection
    email_provider: str = "sendgrid"
    email_from: str = "noreply@yoursaas.com"
    
    # SendGrid
    sendgrid_api_key: Optional[str] = None
    
    # Mailgun
    mailgun_api_key: Optional[str] = None
    mailgun_domain: Optional[str] = None
    mailgun_eu_region: bool = False
    
    # Postmark
    postmark_api_key: Optional[str] = None
    postmark_message_stream: str = "outbound"
    
    # AWS SES
    aws_ses_region: str = "us-east-1"
    aws_ses_configuration_set: Optional[str] = None
    
    # Resend
    resend_api_key: Optional[str] = None
    
    # Cache Provider
    cache_provider: str = "redis"
    upstash_redis_rest_url: Optional[str] = None
    upstash_redis_rest_token: Optional[str] = None
    
    # Monitoring Providers (comma-separated for multiple)
    monitoring_providers: str = "console"
    sentry_dsn: Optional[str] = None
    sentry_traces_sample_rate: float = 0.1
    
    # Analytics Providers (comma-separated for multiple)
    analytics_providers: str = "internal"
    google_analytics_measurement_id: Optional[str] = None
    google_analytics_api_secret: Optional[str] = None
    posthog_api_key: Optional[str] = None
    posthog_host: str = "https://app.posthog.com"
    
    # Storage Provider
    storage_provider: str = "supabase"  # aws_s3, cloudflare_r2, digitalocean_spaces, backblaze_b2, supabase, gcs
    
    # AWS S3 / Cloudflare R2 / DigitalOcean Spaces (S3-compatible)
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    aws_s3_bucket: Optional[str] = None
    s3_endpoint_url: Optional[str] = None  # For R2/Spaces custom endpoints
    
    # Backblaze B2
    b2_application_key_id: Optional[str] = None
    b2_application_key: Optional[str] = None
    b2_bucket_name: Optional[str] = None
    
    # Supabase Storage
    supabase_storage_bucket: str = "uploads"
    
    # Google Cloud Storage
    gcs_project_id: Optional[str] = None
    gcs_bucket_name: Optional[str] = None
    gcs_credentials_path: Optional[str] = None
    
    # CDN Settings
    cdn_domain: Optional[str] = None  # Custom CDN domain
    storage_public_url: Optional[str] = None  # Override public URL generation
    
    # Rate Limiting Provider
    rate_limit_provider: str = "redis"  # redis, upstash, memory
    rate_limit_default_limit: int = 100  # Requests per window
    rate_limit_default_window: int = 60  # Window in seconds
    
    # SMS Provider
    sms_provider: str = "console"  # twilio, vonage, aws_sns, messagebird, console
    
    # Twilio
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None
    
    # Vonage
    vonage_api_key: Optional[str] = None
    vonage_api_secret: Optional[str] = None
    vonage_phone_number: Optional[str] = None
    
    # MessageBird
    messagebird_api_key: Optional[str] = None
    messagebird_phone_number: Optional[str] = None
    
    # Logging Provider
    logging_provider: str = "console"  # datadog, betterstack, cloudwatch, file, console, json
    logging_level: str = "INFO"
    log_file_path: str = "logs/app.log"
    log_file_max_bytes: int = 10485760  # 10MB
    log_file_backup_count: int = 5
    
    # Datadog
    datadog_api_key: Optional[str] = None
    datadog_app_key: Optional[str] = None
    datadog_site: str = "datadoghq.com"
    
    # Better Stack
    betterstack_source_token: Optional[str] = None
    
    # AWS CloudWatch
    cloudwatch_log_group: str = "/aws/saas-app"
    cloudwatch_log_stream: str = "backend"
    
    # Push Notification Provider
    push_notification_provider: str = "onesignal"  # onesignal, firebase, aws_sns_push, pusher, webpush
    
    # OneSignal
    onesignal_app_id: Optional[str] = None
    onesignal_api_key: Optional[str] = None
    
    # Firebase Cloud Messaging
    firebase_credentials_path: Optional[str] = None
    firebase_project_id: Optional[str] = None
    
    # AWS SNS Push
    aws_sns_platform_application_arn: Optional[str] = None
    
    # Pusher Beams
    pusher_beams_instance_id: Optional[str] = None
    pusher_beams_secret_key: Optional[str] = None
    
    # Web Push (VAPID)
    vapid_public_key: Optional[str] = None
    vapid_private_key: Optional[str] = None
    vapid_subject: str = "mailto:admin@yourapp.com"
    
    # Supabase
    supabase_url: str
    supabase_anon_key: str = ""
    supabase_service_key: str = ""
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # JWT
    jwt_secret_key: str = "default-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60
    
    # Optional fields
    docker_registry_url: Optional[str] = None
    docker_registry_token: Optional[str] = None
    email_provider_api_key: Optional[str] = None
    api_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
