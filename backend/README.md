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

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create your `.env`**
   ```bash
   cp env.example .env
   ```
   Populate Supabase, Stripe, and provider keys. For local development we recommend:
   - `CACHE_PROVIDER=redis`
   - `RATE_LIMIT_PROVIDER=redis`
   - `REDIS_URL=redis://localhost:6379`
   - `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_KEY`
   - `SUPABASE_STORAGE_BUCKET=uploads`

3. **Start Redis locally**
   ```bash
   ./scripts/run_redis_docker.sh start
   ```
   This helper ensures a Redis 7 container is running on port 6379. Use `status`, `stop`, or `logs` as needed.

4. **Apply Supabase migrations**
   Load the schema files into your project database (SQL editor, Supabase CLI, or `psql`):
   - `backend/subscriptions/schema.sql`
   - `backend/supabase_schema.sql`
   - Optional patches such as `supabase_fix_duplicate_user.sql`

   Example with `psql`:
   ```bash
   export SUPABASE_CONN="postgresql://postgres:<password>@<host>:5432/postgres"
   cat backend/subscriptions/schema.sql | psql "$SUPABASE_CONN"
   cat backend/supabase_schema.sql     | psql "$SUPABASE_CONN"
   ```

5. **Seed demo data**
   ```bash
   ./scripts/seed_demo_data.py
   ```
   The script confirms/creates demo users, profiles, products, campaigns, and subscriptions. Rerun any time after migrations.

6. **Enable Attack Protection (recommended)**
   In Supabase Dashboard → **Authentication → Attack protection**, toggle on **HaveIBeenPwned** password checks.

7. **Launch the API**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

8. **Optional helpers**
   - `./scripts/verify_supabase_user.py <email>` to force-confirm a Supabase account.
   - `./scripts/run_redis_docker.sh status` to verify Redis health.

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






