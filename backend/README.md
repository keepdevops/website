# SaaS Subscription Platform - Backend

Modular FastAPI backend with plugin architecture. All files are constrained to ≤200 LOC.

## Architecture

- **Plugin System**: Auto-discovery and loading of modular services
- **Event Bus**: Redis pub/sub for decoupled communication
- **Database**: Supabase (PostgreSQL) with RLS policies
- **Cache**: Redis for sessions and idempotency
- **Payments**: Stripe webhooks with secure verification
- **Distribution**: Docker registry integration with access control

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy environment file:
```bash
cp env.example .env
```

3. Configure environment variables in `.env`

4. Run database migrations (execute schema.sql in Supabase SQL editor)

5. Start the server:
```bash
uvicorn main:app --reload
```

## Deployment to Render

1. Push code to Git repository
2. Create new Web Service on Render
3. Connect repository
4. Render will detect `render.yaml` and configure automatically
5. Set environment variables in Render dashboard
6. Deploy!

## Stripe Webhook Setup

1. Create webhook endpoint in Stripe Dashboard
2. Point to: `https://your-domain.onrender.com/api/webhooks/stripe`
3. Select events: `customer.subscription.*`, `payment_intent.*`, `invoice.*`
4. Copy webhook secret to `STRIPE_WEBHOOK_SECRET` env var

## Module Structure

Each module is self-contained:
- `router.py` - API endpoints
- `service.py` - Business logic
- `models.py` - Pydantic schemas
- `__init__.py` - Exports

## Adding New Modules

1. Create directory in backend/
2. Add router.py, service.py, models.py
3. Plugin registry auto-discovers and loads
4. Register event listeners in service.py

## Security

- JWT authentication via Supabase
- Stripe webhook signature verification
- Rate limiting on auth endpoints
- RLS policies on database tables
- Redis-based idempotency for webhooks



