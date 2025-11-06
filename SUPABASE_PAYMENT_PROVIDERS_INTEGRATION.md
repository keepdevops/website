# 💳 Supabase + Payment Providers Integration Guide

**How to use Supabase with multiple payment provider plugins**

**Architecture:** Supabase stores ALL payment data, while payment providers handle transactions  
**Flexibility:** Switch payment providers without losing customer data  
**Multi-Provider:** Support multiple payment methods simultaneously

---

## 🏗️ Architecture Overview

### **The Perfect Combination**

```
┌─────────────────────────────────────────────────────────┐
│                    YOUR APPLICATION                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────┐          │
│  │         SUPABASE (Data Layer)            │          │
│  │                                          │          │
│  │  ✓ User profiles                        │          │
│  │  ✓ Subscription records                 │          │
│  │  ✓ Payment history                      │          │
│  │  ✓ Customer metadata                    │          │
│  │  ✓ Product/pricing data                 │          │
│  │  ✓ Webhook event logs                   │          │
│  └──────────────────────────────────────────┘          │
│                      ▲                                   │
│                      │                                   │
│                      │ (Stores all data)                │
│                      │                                   │
│  ┌──────────────────▼───────────────────────┐          │
│  │    PAYMENT PROVIDER (Transaction Layer)  │          │
│  │                                          │          │
│  │    Choose ONE at a time via .env:       │          │
│  │    ┌──────────────────────────┐         │          │
│  │    │ ☐ Stripe                 │         │          │
│  │    │ ☐ PayPal                 │         │          │
│  │    │ ☐ Square                 │         │          │
│  │    │ ☐ Braintree              │         │          │
│  │    │ ☐ Adyen                  │         │          │
│  │    └──────────────────────────┘         │          │
│  │                                          │          │
│  │  Handles:                               │          │
│  │  ✓ Payment processing                   │          │
│  │  ✓ Subscription billing                 │          │
│  │  ✓ Webhooks                             │          │
│  │  ✓ PCI compliance                       │          │
│  └──────────────────────────────────────────┘          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 How It Works

### **1. Supabase = Your Source of Truth**

**ALL customer data lives in Supabase:**
- User accounts
- Subscription status
- Payment history
- Customer preferences
- Usage data

**Benefits:**
- ✅ Own your data (not locked into a payment provider)
- ✅ Switch payment providers anytime
- ✅ Query data directly with SQL
- ✅ Sync data across multiple payment providers
- ✅ Keep historical data when migrating

### **2. Payment Provider = Transaction Processor**

**Payment provider handles:**
- Credit card processing
- Subscription billing cycles
- Webhooks for status changes
- PCI compliance
- Fraud detection

**Benefits:**
- ✅ Let experts handle payments
- ✅ Choose best rates
- ✅ Switch based on geography
- ✅ A/B test different providers

---

## 🔧 Configuration: Choose Your Payment Provider

### **Option 1: Single Provider (Most Common)**

**Configure in `.env`:**
```bash
# Choose ONE payment provider
PAYMENT_PROVIDER=stripe  # or paypal, square, braintree, adyen

# Add that provider's credentials
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
```

**That's it!** Your app now uses Stripe for all payments, storing data in Supabase.

### **Option 2: Support Multiple Providers Simultaneously** 🚀

**For advanced use cases, you can support MULTIPLE payment providers:**

**Use Cases:**
- Let customers choose their preferred payment method
- Use different providers per region (Stripe for US, Adyen for EU)
- A/B test conversion rates
- Gradual migration from one provider to another

**Implementation:**

```python
# backend/subscriptions/service.py

class SubscriptionService:
    def __init__(self, db: Database, payment_provider: PaymentProviderInterface):
        self.db = db
        self.provider = payment_provider
    
    async def create_checkout_session(
        self,
        user_id: str,
        session_data: CheckoutSessionCreate,
        provider_choice: str = None  # NEW: Let user choose!
    ):
        # Use user's choice OR default from config
        provider_name = provider_choice or settings.payment_provider
        
        # Get the specific provider
        from core.payment_provider_factory import get_payment_provider_by_name
        provider = get_payment_provider_by_name(provider_name, self.db)
        
        # Create checkout with chosen provider
        result = await provider.create_checkout_session(
            user_id=user_id,
            price_id=session_data.price_id,
            success_url=session_data.success_url,
            cancel_url=session_data.cancel_url
        )
        
        # Store which provider was used in Supabase
        await self.db.insert("subscriptions", {
            "user_id": user_id,
            "payment_provider": provider_name,  # Track which provider!
            "provider_subscription_id": result["subscription_id"],
            "status": "pending"
        })
        
        return result
```

---

## 📊 Database Schema: Storing Payment Data in Supabase

### **Subscriptions Table**

```sql
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Track which payment provider is used
    payment_provider VARCHAR(50) NOT NULL,  -- 'stripe', 'paypal', etc.
    
    -- Provider-specific IDs (flexible column naming)
    provider_customer_id VARCHAR(255),      -- Stripe: cus_xxx, PayPal: CUST-xxx
    provider_subscription_id VARCHAR(255),  -- Stripe: sub_xxx, PayPal: I-xxx
    
    -- Universal subscription data (same across all providers)
    plan_id VARCHAR(100),
    status VARCHAR(50),                     -- active, canceled, past_due, etc.
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    
    -- Pricing
    amount DECIMAL(10, 2),
    currency VARCHAR(3) DEFAULT 'USD',
    interval VARCHAR(20),                   -- month, year
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast lookups
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_provider_sub_id ON subscriptions(provider_subscription_id);
CREATE INDEX idx_subscriptions_provider ON subscriptions(payment_provider);
```

### **Payment History Table**

```sql
CREATE TABLE payment_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id),
    subscription_id UUID REFERENCES subscriptions(id),
    
    -- Track which provider processed this payment
    payment_provider VARCHAR(50) NOT NULL,
    
    -- Event details
    event_type VARCHAR(100),                -- payment_succeeded, subscription_created, etc.
    provider_event_id VARCHAR(255),         -- Provider's event ID
    
    -- Payment details
    amount DECIMAL(10, 2),
    currency VARCHAR(3),
    status VARCHAR(50),                     -- succeeded, failed, pending
    
    -- Raw data from provider (JSONB for flexibility)
    provider_data JSONB,                    -- Full webhook payload
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_payment_events_user_id ON payment_events(user_id);
CREATE INDEX idx_payment_events_provider ON payment_events(payment_provider);
```

### **Customer Profiles Table**

```sql
CREATE TABLE customer_profiles (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id),
    
    -- Store customer IDs for ALL providers
    stripe_customer_id VARCHAR(255),
    paypal_customer_id VARCHAR(255),
    square_customer_id VARCHAR(255),
    braintree_customer_id VARCHAR(255),
    adyen_customer_id VARCHAR(255),
    
    -- Customer metadata
    default_payment_provider VARCHAR(50),   -- User's preferred provider
    email VARCHAR(255),
    name VARCHAR(255),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 🎨 Frontend: Let Users Choose Payment Provider

### **Option A: Admin Chooses (Simple)**

**You configure one provider, all users use it.**

```typescript
// frontend/lib/payment/use-payment.ts

export function useCheckout() {
  const createCheckout = async (priceId: string) => {
    // Uses whatever provider is configured in backend .env
    const response = await fetch('/api/subscriptions/checkout', {
      method: 'POST',
      body: JSON.stringify({ price_id: priceId })
    });
    
    const { url } = await response.json();
    window.location.href = url;  // Redirect to Stripe/PayPal/etc.
  };
  
  return { createCheckout };
}
```

### **Option B: Users Choose (Advanced)** 🌟

**Let customers select their preferred payment method.**

```typescript
// frontend/components/PaymentProviderSelector.tsx

import { useState } from 'react';

const PROVIDERS = [
  { id: 'stripe', name: 'Credit Card (Stripe)', icon: '💳' },
  { id: 'paypal', name: 'PayPal', icon: '🅿️' },
  { id: 'square', name: 'Square', icon: '⬜' },
];

export function PaymentProviderSelector({ onCheckout }) {
  const [selectedProvider, setSelectedProvider] = useState('stripe');
  
  const handleCheckout = async (priceId: string) => {
    const response = await fetch('/api/subscriptions/checkout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        price_id: priceId,
        provider: selectedProvider  // User's choice!
      })
    });
    
    const { url } = await response.json();
    window.location.href = url;
  };
  
  return (
    <div>
      <h3>Choose Payment Method</h3>
      
      {PROVIDERS.map(provider => (
        <button
          key={provider.id}
          onClick={() => setSelectedProvider(provider.id)}
          className={selectedProvider === provider.id ? 'selected' : ''}
        >
          <span>{provider.icon}</span>
          <span>{provider.name}</span>
        </button>
      ))}
      
      <button onClick={() => handleCheckout('price_monthly')}>
        Subscribe with {selectedProvider}
      </button>
    </div>
  );
}
```

---

## 🔄 Backend: Handle Multiple Providers

### **Router with Provider Selection**

```python
# backend/subscriptions/router.py

from fastapi import APIRouter, Depends, HTTPException
from core.payment_provider_factory import get_payment_provider_by_name
from subscriptions.models import CheckoutSessionCreate

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

@router.post("/checkout")
async def create_checkout_session(
    session_data: CheckoutSessionCreate,
    provider: str = None,  # Optional: let frontend choose
    user_id: str = Depends(get_current_user_id),
    user_email: str = Depends(get_current_user_email),
    db: Database = Depends(get_database)
):
    """
    Create checkout session.
    Supports multiple payment providers!
    """
    # Use provider from request OR default from config
    provider_name = provider or settings.payment_provider
    
    # Validate provider
    allowed_providers = ['stripe', 'paypal', 'square', 'braintree', 'adyen']
    if provider_name not in allowed_providers:
        raise HTTPException(400, f"Invalid provider: {provider_name}")
    
    # Get the specific provider
    payment_provider = get_payment_provider_by_name(provider_name, db)
    
    # Create checkout
    result = await payment_provider.create_checkout_session(
        user_id=user_id,
        price_id=session_data.price_id,
        success_url=session_data.success_url,
        cancel_url=session_data.cancel_url
    )
    
    # Store in Supabase (regardless of provider!)
    await db.insert("subscriptions", {
        "user_id": user_id,
        "payment_provider": provider_name,  # Track which provider
        "provider_subscription_id": result.get("subscription_id"),
        "status": "pending",
        "plan_id": session_data.price_id
    })
    
    return {
        "session_id": result["session_id"],
        "url": result["url"],
        "provider": provider_name
    }
```

### **Webhooks for Multiple Providers**

```python
# backend/webhooks/router.py

@router.post("/webhook/{provider}")
async def handle_webhook(
    provider: str,
    request: Request,
    db: Database = Depends(get_database)
):
    """
    Unified webhook endpoint for ALL payment providers.
    Route: /webhook/stripe, /webhook/paypal, etc.
    """
    # Get the specific provider
    payment_provider = get_payment_provider_by_name(provider, db)
    
    # Verify webhook signature (provider-specific)
    body = await request.body()
    signature = request.headers.get("stripe-signature") or \
                request.headers.get("paypal-transmission-sig")
    
    event = await payment_provider.verify_webhook(body, signature)
    
    # Store event in Supabase (unified format)
    await db.insert("payment_events", {
        "payment_provider": provider,
        "event_type": event["type"],
        "provider_event_id": event["id"],
        "provider_data": event,
        "created_at": datetime.utcnow()
    })
    
    # Update subscription in Supabase based on event
    if event["type"] == "subscription.created":
        await db.update("subscriptions", {
            "status": "active",
            "provider_subscription_id": event["data"]["subscription_id"]
        }, {"user_id": event["data"]["user_id"]})
    
    return {"success": True}
```

---

## 🌍 Real-World Use Cases

### **Use Case 1: Geographic Routing**

**Problem:** Different payment providers work better in different regions.

**Solution:**
```python
def get_provider_for_region(country_code: str) -> str:
    """Route to best provider based on customer location"""
    regional_providers = {
        'US': 'stripe',      # Best rates in US
        'CA': 'stripe',
        'GB': 'stripe',
        'EU': 'adyen',       # Best for Europe
        'AU': 'square',      # Popular in Australia
        'JP': 'stripe',
        'default': 'paypal'  # PayPal works everywhere
    }
    
    return regional_providers.get(country_code, 'paypal')

@router.post("/smart-checkout")
async def smart_checkout(
    session_data: CheckoutSessionCreate,
    user: User = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    # Auto-select best provider for user's region
    provider = get_provider_for_region(user.country_code)
    
    payment_provider = get_payment_provider_by_name(provider, db)
    # ... create checkout
```

### **Use Case 2: Cost Optimization**

**Problem:** Different providers have different fees.

**Solution:**
```python
# Choose cheapest provider based on transaction amount
def get_cheapest_provider(amount: float, currency: str) -> str:
    """
    Stripe: 2.9% + $0.30
    PayPal: 3.49% + $0.49
    Square: 2.9% + $0.30
    """
    fees = {
        'stripe': amount * 0.029 + 0.30,
        'paypal': amount * 0.0349 + 0.49,
        'square': amount * 0.029 + 0.30,
    }
    
    return min(fees, key=fees.get)
```

### **Use Case 3: Gradual Migration**

**Problem:** You want to switch from Stripe to PayPal without disrupting existing customers.

**Solution:**
```python
@router.post("/checkout")
async def create_checkout(
    session_data: CheckoutSessionCreate,
    user: User = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    # Check if user has existing subscription
    existing_sub = await db.get("subscriptions", {"user_id": user.id})
    
    if existing_sub:
        # Keep existing customers on their current provider
        provider = existing_sub["payment_provider"]
    else:
        # New customers use new provider
        provider = "paypal"  # Migrating to PayPal
    
    payment_provider = get_payment_provider_by_name(provider, db)
    # ... create checkout
```

---

## 📦 Configuration Presets with Payment Providers

### **Startup Free Tier**

```bash
# .env (generated from startup-free preset)

# Supabase (free)
STORAGE_PROVIDER=supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...

# Payment Provider (free account, pay per transaction)
PAYMENT_PROVIDER=stripe
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
```

**Cost:** $0/month base + 2.9% per transaction

### **Cost Optimized**

```bash
# Switch to Square for better rates
PAYMENT_PROVIDER=square
SQUARE_ACCESS_TOKEN=xxx
SQUARE_ENVIRONMENT=production

# Data still in Supabase!
STORAGE_PROVIDER=cloudflare_r2
```

**Cost:** $97.50/month + 2.6% per transaction (save 0.3%!)

### **Multi-Provider Setup**

```bash
# Enable ALL providers, choose at runtime
PAYMENT_PROVIDER=stripe  # Default

# Stripe
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxx

# PayPal (backup)
PAYPAL_CLIENT_ID=xxx
PAYPAL_CLIENT_SECRET=xxx
PAYPAL_MODE=live

# Square (for in-person)
SQUARE_ACCESS_TOKEN=xxx
SQUARE_ENVIRONMENT=production
```

---

## 🔐 Security Best Practices

### **1. Validate Provider Choice**

```python
# Never trust user input
ALLOWED_PROVIDERS = ['stripe', 'paypal', 'square', 'braintree', 'adyen']

def validate_provider(provider: str) -> str:
    if provider not in ALLOWED_PROVIDERS:
        raise ValueError(f"Invalid provider: {provider}")
    return provider
```

### **2. Store Provider Info in Supabase**

```python
# Always track which provider was used
await db.insert("subscriptions", {
    "payment_provider": provider_name,  # Critical!
    "provider_customer_id": customer_id,
    "provider_subscription_id": subscription_id
})
```

### **3. Separate Webhook Endpoints**

```python
# Don't mix webhook payloads
@router.post("/webhook/stripe")
async def stripe_webhook(...): pass

@router.post("/webhook/paypal")
async def paypal_webhook(...): pass
```

---

## 🚀 Quick Start: Add Multi-Provider Support

### **Step 1: Update Database Schema**

```sql
-- Add provider tracking to subscriptions table
ALTER TABLE subscriptions 
ADD COLUMN IF NOT EXISTS payment_provider VARCHAR(50) DEFAULT 'stripe';

-- Add index
CREATE INDEX IF NOT EXISTS idx_subscriptions_provider 
ON subscriptions(payment_provider);
```

### **Step 2: Update Environment**

```bash
# Enable multiple providers
PAYMENT_PROVIDER=stripe  # Default

# Add credentials for all providers you want to support
STRIPE_SECRET_KEY=sk_xxx
PAYPAL_CLIENT_ID=xxx
PAYPAL_CLIENT_SECRET=xxx
SQUARE_ACCESS_TOKEN=xxx
```

### **Step 3: Update Frontend**

```typescript
// Let users choose
const response = await fetch('/api/subscriptions/checkout', {
  method: 'POST',
  body: JSON.stringify({
    price_id: 'price_xxx',
    provider: 'paypal'  // User's choice!
  })
});
```

### **Step 4: Test**

```bash
# Test each provider
curl -X POST http://localhost:8000/api/subscriptions/checkout \
  -H "Content-Type: application/json" \
  -d '{"price_id": "price_123", "provider": "stripe"}'

curl -X POST http://localhost:8000/api/subscriptions/checkout \
  -H "Content-Type: application/json" \
  -d '{"price_id": "price_123", "provider": "paypal"}'
```

---

## ✅ Summary

### **The Perfect Setup:**

```
Supabase (Data) + Payment Provider Plugins (Transactions) = 🎯 Perfect!
```

**What Supabase Stores:**
✅ All user data
✅ All subscription records
✅ All payment history
✅ Which provider each customer uses

**What Payment Providers Handle:**
✅ Credit card processing
✅ Subscription billing
✅ Webhooks
✅ PCI compliance

**Benefits:**
✅ Own your data
✅ Switch providers anytime
✅ Support multiple providers
✅ Route by geography/cost
✅ A/B test providers
✅ Gradual migrations

---

## 📚 Files to Reference

```
Backend:
  • backend/core/payment_provider_factory.py  - Provider selection
  • backend/subscriptions/service.py          - Business logic
  • backend/subscriptions/schema.sql          - Database schema
  • backend/webhooks/router.py                - Webhook handling

Frontend:
  • lib/payment/provider-context.tsx          - Payment context
  • lib/payment/use-payment.ts                - Payment hooks
  • components/PaymentProviderSelector.tsx    - UI (create this!)

Config:
  • backend/config.py                         - Environment variables
  • backend/config_presets/startup_free.py    - Free tier setup
  • backend/config_presets/cost_optimized.py  - Optimized setup
```

---

**Ready to implement multi-provider support? Just ask!** 🚀

