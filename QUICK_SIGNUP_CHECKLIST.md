# ✅ Quick Signup Checklist - Print This!

Use this as you sign up for each service. Check off each step.

---

## 📋 Master Checklist

- [ ] **Supabase** (10 min)
- [ ] **Resend** (5 min)  
- [ ] **Stripe** (10 min)
- [ ] **OneSignal** (10 min)
- [ ] **Configure .env** (5 min)
- [ ] **Test & Launch** (5 min)

**Total Time: ~45 minutes** ⏱️

---

## 1️⃣ Supabase Checklist

**URL:** https://supabase.com

- [ ] Create account (GitHub signup recommended)
- [ ] Create new project
  - [ ] Choose name
  - [ ] Save database password
  - [ ] Select free plan
  - [ ] Wait for provisioning (2-3 min)
- [ ] Get API keys (Settings → API)
  - [ ] Copy `SUPABASE_URL`
  - [ ] Copy `anon public` key → `SUPABASE_ANON_KEY`
  - [ ] Copy `service_role` key → `SUPABASE_SERVICE_KEY`
- [ ] Create storage bucket (Storage → New bucket)
  - [ ] Name: `uploads`
  - [ ] Public: Yes

**✍️ Write down:**
```
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_KEY=
SUPABASE_STORAGE_BUCKET=uploads
```

---

## 2️⃣ Resend Checklist

**URL:** https://resend.com

- [ ] Create account
- [ ] Verify email
- [ ] (Optional) Add domain OR use `onboarding@resend.dev`
- [ ] Create API key (API Keys → Create)
  - [ ] Name: `Production`
  - [ ] **COPY KEY NOW** (can't see it again!)

**✍️ Write down:**
```
RESEND_API_KEY=re_
```

---

## 3️⃣ Stripe Checklist

**URL:** https://stripe.com

- [ ] Create account
- [ ] Verify email
- [ ] Fill business info (can skip some for testing)
- [ ] Get API keys (Developers → API keys)
  - [ ] Make sure in **Test mode**
  - [ ] Copy `Publishable key` → `STRIPE_PUBLISHABLE_KEY`
  - [ ] Copy `Secret key` → `STRIPE_SECRET_KEY`
- [ ] Create webhook (Developers → Webhooks)
  - [ ] Endpoint URL: `https://yourdomain.com/api/payment/webhook/stripe`
  - [ ] Select events: checkout.session.completed, customer.subscription.*
  - [ ] Copy `Signing secret` → `STRIPE_WEBHOOK_SECRET`

**✍️ Write down:**
```
STRIPE_SECRET_KEY=sk_test_
STRIPE_PUBLISHABLE_KEY=pk_test_
STRIPE_WEBHOOK_SECRET=whsec_
```

---

## 4️⃣ OneSignal Checklist

**URL:** https://onesignal.com

- [ ] Create account
- [ ] Create new app
  - [ ] Name: Your app name
  - [ ] Platform: Web Push
  - [ ] Site URL: `https://yourdomain.com`
- [ ] Get keys (Settings → Keys & IDs)
  - [ ] Copy `OneSignal App ID` → `ONESIGNAL_APP_ID`
  - [ ] Copy `REST API Key` → `ONESIGNAL_API_KEY`

**✍️ Write down:**
```
ONESIGNAL_APP_ID=
ONESIGNAL_API_KEY=
```

---

## 5️⃣ Configure .env

- [ ] Copy template: `cp .env.startup-free .env`
- [ ] Open `.env` in editor
- [ ] Paste all your API keys
- [ ] Verify no placeholders remain
- [ ] Save file

---

## 6️⃣ Test Everything

- [ ] Install: `pip install -r requirements.txt`
- [ ] Run: `uvicorn main:app --reload`
- [ ] Visit: http://localhost:8000/docs
- [ ] Test each endpoint
- [ ] Send test email
- [ ] Create test payment
- [ ] Send test notification

---

## 🎯 API Keys Quick Copy

Copy this template and fill it in as you go:

```bash
# SUPABASE
SUPABASE_URL=https://________________.supabase.co
SUPABASE_ANON_KEY=eyJ_____________________________
SUPABASE_SERVICE_KEY=eyJ_____________________________
SUPABASE_STORAGE_BUCKET=uploads

# RESEND  
RESEND_API_KEY=re_________________________________

# STRIPE (Test Mode)
STRIPE_SECRET_KEY=sk_test__________________________
STRIPE_PUBLISHABLE_KEY=pk_test__________________________
STRIPE_WEBHOOK_SECRET=whsec________________________________

# ONESIGNAL
ONESIGNAL_APP_ID=_____________________________________
ONESIGNAL_API_KEY=_____________________________________
```

---

## 🆘 Got Stuck?

| Issue | Quick Fix |
|-------|-----------|
| Supabase project won't create | Wait 5 min, try different region |
| Resend email not sending | Verify domain OR use `onboarding@resend.dev` |
| Stripe webhook failing | Use Stripe CLI for local testing |
| OneSignal not receiving | Check browser permissions, use HTTPS |

**Full troubleshooting:** See `STARTUP_FREE_TIER_SIGNUP_GUIDE.md`

---

## 💰 What You Get FREE

- **Supabase:** 500 MB DB + 1 GB storage + Auth
- **Resend:** 3,000 emails/month
- **Stripe:** Unlimited (pay 2.9% + 30¢ per transaction)
- **OneSignal:** Unlimited push notifications

**Value:** ~$185/month **Cost:** $0/month 🎉

---

## ⏱️ Time Estimates

- ⚡ **Express mode:** 20 min (skip optional steps)
- 🎯 **Standard mode:** 40 min (recommended)
- 🔬 **Thorough mode:** 60 min (test everything)

---

**Print this page and check off items as you complete them!**

Good luck! 🚀

