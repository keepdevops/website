# Quick Start Guide

Get your SaaS platform running in 10 minutes!

## 1. Backend Setup (5 minutes)

```bash
cd backend

# Check what's needed
python3 check_setup.py

# Create environment file
cp env.example .env

# Edit .env with your credentials (minimum for local dev):
# - SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY
# - STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY (use test keys)
# - REDIS_URL=redis://localhost:6379 (or use free Redis cloud)

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn main:app --reload
```

Backend will run on http://localhost:8000

## 2. Database Setup (2 minutes)

```bash
# Go to supabase.com and create free project
# Copy URL and keys to backend/.env

# In Supabase SQL Editor, paste and run:
backend/subscriptions/schema.sql

# This creates all tables with RLS policies
```

## 3. Frontend Setup (3 minutes)

```bash
cd ..  # back to root

# Install dependencies
npm install

# Create environment file
cp env.local.example .env.local

# Edit .env.local:
# NEXT_PUBLIC_SUPABASE_URL=your_url
# NEXT_PUBLIC_SUPABASE_ANON_KEY=your_key  
# NEXT_PUBLIC_API_URL=http://localhost:8000
# NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...

# Start frontend
npm run dev
```

Frontend will run on http://localhost:3000

## 4. Redis (Optional for local)

**Option A - Docker:**
```bash
docker run -d -p 6379:6379 redis:alpine
```

**Option B - Cloud (Recommended):**
- Get free Redis from Upstash.com or Redis Cloud
- Update REDIS_URL in backend/.env

## 5. First User & Admin

1. Go to http://localhost:3000/register
2. Create account
3. Go to Supabase > Table Editor > profiles
4. Find your user, set `is_admin = true`
5. Refresh page - you now have admin access!

## 6. Test Stripe (Optional)

```bash
# Use Stripe test mode keys in .env
# Test card: 4242 4242 4242 4242
# Any future expiry, any CVC

# For webhooks locally, use Stripe CLI:
stripe listen --forward-to localhost:8000/api/webhooks/stripe
# Copy webhook secret to STRIPE_WEBHOOK_SECRET
```

## URLs

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Test the Platform

1. **Register**: http://localhost:3000/register
2. **Login**: http://localhost:3000/login  
3. **Dashboard**: http://localhost:3000/dashboard
4. **Admin Panel**: http://localhost:3000/admin (if admin)

## Common Issues

**Backend won't start:**
- Check .env file exists
- Verify Python 3.11+
- Install requirements.txt

**Frontend build errors:**
- Run `npm install` again
- Check Node.js 18+
- Verify .env.local exists

**Database errors:**
- Run schema.sql in Supabase
- Check Supabase credentials
- Verify RLS policies enabled

**Redis connection:**
- Use cloud Redis for easiest setup
- Or run local Docker container

## What's Next?

✅ Platform is running!

Now:
1. Customize branding in frontend
2. Add your Stripe products/prices
3. Configure Docker registry for software distribution
4. Setup email service (SendGrid/Mailgun)
5. Deploy to production (see DEPLOYMENT.md)

## File Structure Reference

Every file ≤200 LOC:

```
backend/
  core/          - Plugin system, event bus, DB, cache
  auth/          - Login, register, JWT
  subscriptions/ - Stripe checkout & management  
  webhooks/      - Secure Stripe webhook handlers
  customers/     - Customer management (admin)
  docker_registry/ - Software download tokens
  campaigns/     - Email marketing
  analytics/     - Usage metrics

app/
  (auth)/        - Login & register pages
  dashboard/     - User dashboard
  admin/         - Admin panel

components/      - Reusable React components
lib/             - API client, types, utilities
```

## Adding Features

Create new backend module:
```bash
mkdir backend/my_feature
touch backend/my_feature/{router,service,models,__init__}.py
# Plugin registry auto-discovers it!
```

## Support

- Check README.md for detailed docs
- See DEPLOYMENT.md for production setup
- All files have meaningful names and minimal comments
- Each module is self-contained and ≤200 LOC

Happy building! 🚀



