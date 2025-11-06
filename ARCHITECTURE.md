# Architecture Documentation

## Design Principles

1. **200 LOC Limit**: Every file ≤200 lines of code
2. **Meaningful Naming**: Self-documenting variable/function names
3. **Minimal Comments**: Code clarity over comments
4. **Single Responsibility**: Each file has one clear purpose
5. **Modular Design**: Features are standalone plugins
6. **Event-Driven**: Loose coupling via event bus
7. **Easy Extension**: Add features by creating directories

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Next.js Frontend                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │   Auth   │  │Dashboard │  │  Admin   │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└────────────┬────────────────────────────────────────────┘
             │ HTTPS/REST
             ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │           Plugin Registry (Auto-Discovery)       │  │
│  └────┬─────────────────────────────────────────────┘  │
│       │                                                  │
│  ┌────▼────┐ ┌──────┐ ┌────────┐ ┌─────────┐          │
│  │  Auth   │ │Stripe│ │ Docker │ │Campaigns│ ...      │
│  │ Plugin  │ │Plugin│ │ Plugin │ │ Plugin  │          │
│  └─────────┘ └──────┘ └────────┘ └─────────┘          │
│                    │                                     │
│              ┌─────▼─────┐                              │
│              │ Event Bus │ (Redis Pub/Sub)             │
│              └─────┬─────┘                              │
└────────────────────┼──────────────────────────────────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
    ┌────▼────┐ ┌───▼────┐ ┌───▼────┐
    │Supabase │ │ Redis  │ │ Stripe │
    │   DB    │ │ Cache  │ │  API   │
    └─────────┘ └────────┘ └────────┘
```

## Backend Plugin System

### How Plugins Work

1. **Auto-Discovery**: Plugin registry scans backend/* directories
2. **Convention**: Each plugin has router.py, service.py, models.py
3. **Loading**: Automatically includes router in FastAPI app
4. **Events**: Plugins subscribe to/emit events via event bus
5. **Dependencies**: Injected via FastAPI Depends()

### Adding a New Plugin

```python
# backend/my_feature/router.py
from fastapi import APIRouter
router = APIRouter(prefix="/api/my-feature", tags=["My Feature"])

@router.get("/")
async def my_endpoint():
    return {"hello": "world"}

# That's it! Plugin registry auto-loads it.
```

### Event-Driven Communication

```python
# Plugin A - Emit event
await event_bus.publish("user.registered", {
    "user_id": user_id,
    "email": email
})

# Plugin B - Listen to event  
event_bus.subscribe("user.registered", self.send_welcome_email)
```

## Data Flow Examples

### 1. User Registration

```
User → Frontend → POST /api/auth/register → Auth Service
                                               ↓
                                    Create user in Supabase
                                               ↓
                                    Emit "user.registered" event
                                               ↓
                        ┌────────────────┬────┴────┬────────────┐
                        ▼                ▼         ▼            ▼
                  Email Service   Analytics  Campaign   Docker Access
```

### 2. Stripe Webhook

```
Stripe → POST /api/webhooks/stripe → Validator (verify signature)
                                          ↓
                                    Check idempotency (Redis)
                                          ↓
                                    Processor → Route to handler
                                          ↓
                            ┌─────────────┴─────────────┐
                            ▼                           ▼
                   Subscription Handler         Invoice Handler
                            ↓                           ↓
                   Update DB + Emit events     Update DB + Send email
```

### 3. Docker Download

```
User → Frontend → POST /api/docker/download-token
                            ↓
                   Check subscription (DB)
                            ↓
                   Verify access control
                            ↓
                   Generate token (Redis, 24h TTL)
                            ↓
                   Log download (DB)
                            ↓
                   Return token to user
```

## Database Schema

### Tables

- **profiles**: User accounts (extends Supabase auth.users)
- **subscriptions**: Stripe subscription sync
- **products**: Software offerings
- **campaigns**: Email campaigns
- **webhook_events**: Idempotency tracking
- **download_logs**: Audit trail
- **usage_events**: Analytics

### Row Level Security

All tables have RLS policies:
- Users see only their own data
- Admins see everything
- Service role bypasses RLS

## Security Layers

1. **Authentication**: Supabase Auth → JWT tokens
2. **Authorization**: RLS policies + admin checks
3. **Webhook Security**: Stripe signature verification
4. **Idempotency**: Redis tracking prevents duplicate processing
5. **Rate Limiting**: Auth endpoints limited (10 req/min)
6. **CORS**: Configured for frontend domains only
7. **Input Validation**: Pydantic models on all endpoints

## Caching Strategy

**Redis Usage:**
- Session data (user tokens)
- Rate limit counters
- Webhook idempotency keys
- Download tokens (24h TTL)
- Analytics aggregations (5min TTL)

## File Organization

### Backend Modules (All ≤200 LOC)

```
core/
  - plugin_registry.py    # Auto-discovers plugins
  - plugin_interface.py   # Base class for plugins
  - event_bus.py          # Redis pub/sub
  - database.py           # Supabase wrapper
  - cache.py              # Redis wrapper
  - dependencies.py       # FastAPI deps

auth/
  - router.py             # Endpoints
  - service.py            # Business logic
  - models.py             # Pydantic schemas
  
webhooks/
  - router.py             # Main webhook endpoint
  - validator.py          # Security checks
  - processor.py          # Event dispatcher
  - handlers/
    - subscription.py     # Subscription events
    - payment.py          # Payment events
    - invoice.py          # Invoice events
```

### Frontend Structure

```
app/
  (auth)/                 # Auth route group
    login/page.tsx
    register/page.tsx
  dashboard/              # User dashboard
    page.tsx
    billing/page.tsx
    downloads/page.tsx
  admin/                  # Admin panel
    page.tsx
    customers/page.tsx
    campaigns/page.tsx

components/
  auth/                   # Auth components
  dashboard/              # Dashboard components
  admin/                  # Admin components
  shared/                 # Reusable components

lib/
  supabase-client.ts      # Supabase client
  api-client.ts           # Axios with interceptors
  types.ts                # TypeScript interfaces
```

## Deployment Architecture

```
Production Setup:

Frontend (Vercel)
  ├── Static hosting
  ├── Edge functions
  └── Auto SSL

Backend (Render)
  ├── Web Service (FastAPI)
  ├── Redis Instance
  └── Auto-deploy from Git

Database (Supabase)
  ├── PostgreSQL
  ├── Auth service
  ├── Realtime (optional)
  └── Edge functions

External Services
  ├── Stripe (Payments)
  ├── Docker Hub (Images)
  └── SendGrid (Email)
```

## Performance Considerations

1. **Redis Caching**: Frequently accessed data cached
2. **Database Indexes**: All foreign keys indexed
3. **Async Operations**: FastAPI async/await throughout
4. **Background Tasks**: Webhook processing async
5. **Connection Pooling**: Database connections pooled
6. **Event Bus**: Non-blocking pub/sub

## Scalability

**Horizontal Scaling:**
- FastAPI workers can scale horizontally
- Redis supports clustering
- Supabase read replicas
- Frontend CDN distribution

**Vertical Scaling:**
- Upgrade Render instance
- Increase Redis memory
- Supabase compute units

## Monitoring Points

1. **Health Check**: `/health` endpoint
2. **Webhook Events**: Track in database
3. **Stripe Dashboard**: Payment events
4. **Supabase Logs**: Database queries
5. **Redis Metrics**: Cache hit rates
6. **Render Logs**: Application logs

## Extension Points

### Add New Product

```sql
INSERT INTO products (name, docker_image, stripe_product_id)
VALUES ('New App', 'registry.io/new-app', 'prod_xxx');
```

### Add New Feature Module

```bash
mkdir backend/new_feature
# Add router.py, service.py, models.py
# Plugin system auto-loads!
```

### Add Event Listener

```python
def __init__(self):
    event_bus.subscribe("subscription.created", 
                       self.handle_new_subscription)
```

## Code Quality Rules

1. **No file** exceeds 200 LOC
2. **Meaningful names** - no `temp`, `data`, `func`
3. **Minimal comments** - code explains itself
4. **Type hints** - all Python functions
5. **Pydantic models** - all API schemas
6. **Error handling** - try/except with logging
7. **Dependency injection** - no globals

This architecture supports infinite growth while maintaining code quality and modularity!



