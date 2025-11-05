# SaaS Subscription Platform

Full-stack modular SaaS platform with Next.js frontend and FastAPI backend. Every file constrained to 200 LOC with meaningful naming and minimal comments.

## Features

- **Authentication**: Supabase Auth with JWT
- **Subscriptions**: Stripe integration with webhooks
- **Customer Management**: Admin panel for user management
- **Docker Distribution**: Secure download tokens for software
- **Email Campaigns**: Bulk email with segmentation
- **Analytics**: Real-time metrics and conversion tracking
- **Plugin Architecture**: Easily add new features as standalone modules

## Tech Stack

**Frontend:**
- Next.js 16 (React 19)
- TypeScript
- Tailwind CSS
- Axios for API calls
- Supabase JS client

**Backend:**
- FastAPI (Python)
- Supabase (PostgreSQL + Auth)
- Redis (caching + event bus)
- Stripe (payments)
- Docker Registry integration

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
cp env.example .env
# Edit .env with your credentials
uvicorn main:app --reload
```

### Frontend

```bash
npm install
cp env.local.example .env.local
# Edit .env.local with your credentials
npm run dev
```

### Database Setup

1. Create Supabase project
2. Run SQL from `backend/subscriptions/schema.sql` in Supabase SQL editor
3. Copy Supabase URL and keys to environment files

### Stripe Setup

1. Create Stripe account
2. Get API keys from Stripe dashboard
3. Create products and prices
4. Setup webhook endpoint (see backend README)

## Project Structure

```
/backend/              - FastAPI modular backend
  /core/               - Plugin system, event bus, database
  /auth/               - Authentication module
  /subscriptions/      - Stripe integration
  /webhooks/           - Secure webhook handlers
  /customers/          - Customer management
  /docker_registry/    - Software distribution
  /campaigns/          - Email campaigns
  /analytics/          - Usage tracking
  /utils/              - Shared utilities

/app/                  - Next.js frontend
  /(auth)/             - Login & register pages
  /dashboard/          - Customer dashboard
  /admin/              - Admin panel

/components/           - Reusable React components
  /auth/               - Auth forms
  /dashboard/          - Dashboard components
  /admin/              - Admin components

/lib/                  - Frontend utilities
```

## Modular Design

Each backend module:
- ≤200 LOC per file
- Self-contained with router/service/models
- Auto-discovered by plugin registry
- Communicates via event bus
- No tight coupling

## Adding New Features

1. Create new module directory in `backend/`
2. Add `router.py`, `service.py`, `models.py`
3. Plugin system automatically loads it
4. Subscribe to events in service for integration

## Deployment

### Backend (Render)
- Configured via `backend/render.yaml`
- Includes Redis instance
- Auto-deploys from Git

### Frontend (Vercel)
- Connect GitHub repository
- Auto-detects Next.js
- Set environment variables
- Deploy!

## Environment Variables

See `backend/env.example` and `env.local.example` for required variables.

## Security

- Row Level Security (RLS) on all tables
- Stripe webhook signature verification
- JWT token validation
- Rate limiting on auth
- Redis-based idempotency

## Testing

### Backend Tests

```bash
cd backend
./run_tests.sh
```

Tests include:
- ✅ Authentication (registration, login, validation)
- ✅ Stripe subscriptions (checkout, management)
- ✅ Webhooks (signature verification, idempotency)
- ✅ Docker downloads (access control, tokens)

See `backend/TESTING.md` for detailed testing guide.

### Test Coverage

- All modules have comprehensive mock tests
- Security-critical paths (webhooks) have 95%+ coverage
- Fast execution (< 10 seconds for full suite)
- No external dependencies required

## License

MIT
