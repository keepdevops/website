#!/bin/bash

echo "🔧 Supabase Configuration Setup"
echo "================================"
echo ""
echo "Please have your Supabase dashboard open:"
echo "Settings → API"
echo ""

# Check if .env already exists
if [ -f "backend/.env" ]; then
    echo "⚠️  backend/.env already exists!"
    read -p "Overwrite? (y/n): " overwrite
    if [ "$overwrite" != "y" ]; then
        echo "Cancelled."
        exit 0
    fi
fi

echo ""
echo "Enter your Supabase credentials:"
echo "================================"
echo ""

read -p "📍 Project URL (https://xxx.supabase.co): " SUPABASE_URL
read -p "🔑 Anon/Public Key (eyJ...): " SUPABASE_ANON_KEY
read -p "🔐 Service Role Key (eyJ...): " SUPABASE_SERVICE_KEY

echo ""
echo "Optional - Stripe (can add later):"
read -p "Stripe Secret Key (sk_test_... or press Enter to skip): " STRIPE_SECRET_KEY
read -p "Stripe Publishable Key (pk_test_... or press Enter to skip): " STRIPE_PUBLISHABLE_KEY

# Set defaults for optional fields
STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY:-"sk_test_dummy"}
STRIPE_PUBLISHABLE_KEY=${STRIPE_PUBLISHABLE_KEY:-"pk_test_dummy"}
STRIPE_WEBHOOK_SECRET="whsec_dummy"
REDIS_URL="redis://localhost:6379"
DOCKER_REGISTRY_URL="docker.io"
DOCKER_REGISTRY_TOKEN="dummy_token"
EMAIL_PROVIDER_API_KEY="dummy_email_key"

# Create backend .env
cat > backend/.env << EOF
# Supabase Configuration
SUPABASE_URL=$SUPABASE_URL
SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY
SUPABASE_SERVICE_KEY=$SUPABASE_SERVICE_KEY

# Stripe Configuration
STRIPE_SECRET_KEY=$STRIPE_SECRET_KEY
STRIPE_WEBHOOK_SECRET=$STRIPE_WEBHOOK_SECRET
STRIPE_PUBLISHABLE_KEY=$STRIPE_PUBLISHABLE_KEY

# Redis Configuration
REDIS_URL=$REDIS_URL

# Docker Registry
DOCKER_REGISTRY_URL=$DOCKER_REGISTRY_URL
DOCKER_REGISTRY_TOKEN=$DOCKER_REGISTRY_TOKEN

# Email Provider
EMAIL_PROVIDER_API_KEY=$EMAIL_PROVIDER_API_KEY

# Application URLs
API_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000

# Environment
ENVIRONMENT=development
EOF

# Create frontend .env.local
cat > .env.local << EOF
NEXT_PUBLIC_SUPABASE_URL=$SUPABASE_URL
NEXT_PUBLIC_SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=$STRIPE_PUBLISHABLE_KEY
EOF

echo ""
echo "✅ Configuration files created!"
echo ""
echo "Created:"
echo "  ✓ backend/.env"
echo "  ✓ .env.local"
echo ""
echo "⚠️  These files are gitignored - your secrets are safe!"
echo ""
echo "Next steps:"
echo "1. Run database migrations in Supabase"
echo "2. Restart your backend server"
echo ""
echo "Would you like to see the migration instructions? (y/n)"



