# Deployment Guide

## Prerequisites

- Supabase account
- Stripe account  
- Render account (for backend + Redis)
- Vercel account (for frontend) or use Render
- Docker Hub account (for software distribution)
- Email service API key (SendGrid/Mailgun/Resend)

## Step 1: Supabase Setup

1. Create new project at supabase.com
2. Go to SQL Editor
3. Paste and run contents of `backend/subscriptions/schema.sql`
4. Go to Settings > API
5. Copy Project URL and anon/service keys
6. Enable Email Auth in Authentication settings

## Step 2: Stripe Setup

1. Create Stripe account
2. Create products and prices in Products section
3. Copy Secret Key and Publishable Key
4. Note: Webhook secret will be set after backend deployment

## Step 3: Deploy Backend to Render

1. Push code to GitHub/GitLab
2. Go to render.com > New > Web Service
3. Connect your repository
4. Render auto-detects `render.yaml`
5. Set environment variables:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_KEY`
   - `STRIPE_SECRET_KEY`
   - `STRIPE_PUBLISHABLE_KEY`
   - `DOCKER_REGISTRY_URL`
   - `DOCKER_REGISTRY_TOKEN`
   - `EMAIL_PROVIDER_API_KEY`
   - `FRONTEND_URL` (will update after frontend deploy)
6. Click "Create Web Service"
7. Wait for deployment (5-10 minutes)
8. Copy your backend URL (e.g., https://saas-backend.onrender.com)

## Step 4: Configure Stripe Webhooks

1. Go to Stripe Dashboard > Developers > Webhooks
2. Click "Add endpoint"
3. Endpoint URL: `https://your-backend.onrender.com/api/webhooks/stripe`
4. Select events:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `invoice.paid`
   - `invoice.payment_failed`
5. Copy webhook signing secret
6. Add to Render env vars as `STRIPE_WEBHOOK_SECRET`
7. Redeploy backend on Render

## Step 5: Deploy Frontend to Vercel

1. Go to vercel.com > New Project
2. Import your Git repository
3. Framework Preset: Next.js (auto-detected)
4. Add environment variables:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `NEXT_PUBLIC_API_URL` (your Render backend URL)
   - `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`
5. Click "Deploy"
6. Copy your frontend URL

## Step 6: Update CORS & Frontend URL

1. Go back to Render backend
2. Update environment variable:
   - `FRONTEND_URL` = your Vercel URL
3. Update `config.py` cors_origins if needed
4. Redeploy

## Step 7: Create First Admin User

1. Register a user at your frontend `/register`
2. Go to Supabase > Table Editor > profiles
3. Find your user and set `is_admin = true`
4. Refresh frontend - you now have admin access!

## Step 8: Docker Registry Setup

Option A - Docker Hub:
1. Create Docker Hub account
2. Create repository
3. Get access token
4. Add to Render:
   - `DOCKER_REGISTRY_URL` = `docker.io/your-username`
   - `DOCKER_REGISTRY_TOKEN` = your token

Option B - GitHub Container Registry:
1. Create personal access token
2. Add to environment variables

## Step 9: Test Everything

1. Register new user
2. Create Stripe checkout session
3. Complete test payment
4. Verify webhook received
5. Check subscription in dashboard
6. Generate download token
7. Test admin panel

## Local Development

Backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp env.example .env
# Edit .env
uvicorn main:app --reload
```

Frontend:
```bash
npm install
cp env.local.example .env.local
# Edit .env.local
npm run dev
```

Redis (local):
```bash
docker run -p 6379:6379 redis:alpine
```

## Production Checklist

- [ ] All environment variables set
- [ ] Supabase RLS policies enabled
- [ ] Stripe webhooks configured
- [ ] Redis connected
- [ ] CORS configured correctly
- [ ] Admin user created
- [ ] Test subscription flow
- [ ] Test webhooks with Stripe CLI
- [ ] Docker registry authenticated
- [ ] Email service configured
- [ ] SSL/HTTPS enabled (automatic on Render/Vercel)

## Monitoring

- Backend logs: Render dashboard
- Frontend logs: Vercel dashboard
- Database: Supabase dashboard
- Stripe events: Stripe dashboard > Developers > Events
- Redis: Render Redis dashboard

## Scaling

- Upgrade Render plan for more resources
- Enable Redis persistence
- Add database read replicas
- Implement caching strategy
- Use CDN for static assets

