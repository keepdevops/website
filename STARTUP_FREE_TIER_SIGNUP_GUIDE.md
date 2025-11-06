# 🚀 Startup Free Tier - Service Signup Guide

Complete this guide to get all your free API keys! Estimated time: **30-40 minutes**

---

## 📋 Checklist

- [ ] **Service 1:** Supabase (Database, Auth, Storage) - 10 min
- [ ] **Service 2:** Resend (Email) - 5 min
- [ ] **Service 3:** Stripe (Payments) - 10 min
- [ ] **Service 4:** OneSignal (Push Notifications) - 10 min
- [ ] **Final Step:** Configure .env file - 5 min

---

## 1️⃣ Supabase Setup (10 minutes)

**What you get:** Database, Authentication, File Storage, Real-time subscriptions

### Step 1: Create Account
1. Go to **https://supabase.com**
2. Click **"Start your project"**
3. Sign up with GitHub (recommended) or email
4. Verify your email if needed

### Step 2: Create a Project
1. Click **"New Project"**
2. Fill in:
   - **Organization:** Create new or select existing
   - **Project Name:** `my-startup-app` (or your app name)
   - **Database Password:** Generate a strong password (save it!)
   - **Region:** Choose closest to your users
   - **Pricing Plan:** Free (already selected)
3. Click **"Create new project"**
4. Wait 2-3 minutes for provisioning ☕

### Step 3: Get Your API Keys
1. Once project is ready, go to **Settings** (gear icon in sidebar)
2. Click **API** in the left menu
3. Copy these values:

```bash
# You'll need these:
Project URL          → SUPABASE_URL
anon public key      → SUPABASE_ANON_KEY
service_role secret  → SUPABASE_SERVICE_KEY
```

**⚠️ Important:**
- `anon public` key is SAFE to use in frontend
- `service_role` key is SECRET - never expose in frontend!

### Step 4: Create Storage Bucket
1. In Supabase dashboard, click **Storage** in sidebar
2. Click **"New bucket"**
3. Bucket name: `uploads`
4. Public bucket: **Yes** (or No if you want private files)
5. Click **"Create bucket"**

**✅ Done!** Save these values:
```
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_STORAGE_BUCKET=uploads
```

---

## 2️⃣ Resend Setup (5 minutes)

**What you get:** 3,000 emails/month, 100 emails/day - FREE forever

### Step 1: Create Account
1. Go to **https://resend.com**
2. Click **"Start Building"** or **"Sign Up"**
3. Sign up with email or GitHub
4. Verify your email

### Step 2: Add Your Domain (Optional but Recommended)
1. Go to **Domains** in sidebar
2. Click **"Add Domain"**
3. Enter your domain (e.g., `yourdomain.com`)
4. Add DNS records to your domain provider:
   - Copy the TXT, MX, and CNAME records
   - Add them to your DNS (Cloudflare, Namecheap, etc.)
   - Wait for verification (5-30 minutes)

**OR use Resend's shared domain for testing:**
- Skip domain verification
- Use `onboarding@resend.dev` as sender
- Limited to verified recipients only

### Step 3: Get API Key
1. Go to **API Keys** in sidebar
2. Click **"Create API Key"**
3. Name: `Production` or `My Startup App`
4. Permission: **Sending access** (default)
5. Click **"Create"**
6. **COPY THE KEY NOW** - you can't see it again!

**✅ Done!** Save this:
```
RESEND_API_KEY=re_123456789_AbCdEfGhIjKlMnOpQrStUvWxYz
```

### Sending Your First Email (Test)
```python
import resend

resend.api_key = "re_your_key"

resend.Emails.send({
    "from": "onboarding@resend.dev",  # or your@domain.com
    "to": "your-email@example.com",
    "subject": "Test from Resend",
    "html": "<p>It works!</p>"
})
```

---

## 3️⃣ Stripe Setup (10 minutes)

**What you get:** Payment processing, subscriptions, billing portal (pay per transaction only)

### Step 1: Create Account
1. Go to **https://stripe.com**
2. Click **"Start now"** or **"Sign up"**
3. Enter your email and create password
4. Fill in business information:
   - **Business name:** Your startup name
   - **Country:** Your country
   - **Business type:** Individual or Company
5. Verify your email

### Step 2: Activate Your Account
1. Complete business details:
   - Industry
   - Website (optional for now)
   - What you're selling
2. Add representative information
3. Add bank account (for payouts) - can skip for testing

**📝 Note:** You can test without full activation, just stay in Test Mode

### Step 3: Get API Keys
1. Go to **Developers** → **API keys**
2. Make sure you're in **Test mode** (toggle in top right)
3. Copy these keys:

```bash
# Test mode keys (for development):
Publishable key → STRIPE_PUBLISHABLE_KEY (starts with pk_test_)
Secret key      → STRIPE_SECRET_KEY (starts with sk_test_)
```

**⚠️ Important:**
- `Publishable key` is SAFE for frontend
- `Secret key` is SECRET - backend only!

### Step 4: Get Webhook Secret
1. Go to **Developers** → **Webhooks**
2. Click **"Add endpoint"**
3. Endpoint URL: `https://your-domain.com/api/payment/webhook/stripe`
   - For local testing: `https://your-ngrok-url.ngrok.io/api/payment/webhook/stripe`
4. Description: `Production Webhooks`
5. Events to send: Click **"Select events"**
   - Choose: `checkout.session.completed`
   - Choose: `customer.subscription.created`
   - Choose: `customer.subscription.updated`
   - Choose: `customer.subscription.deleted`
   - Choose: `invoice.payment_succeeded`
   - Choose: `invoice.payment_failed`
6. Click **"Add endpoint"**
7. Click on the webhook you just created
8. Reveal the **Signing secret** → Copy it

**✅ Done!** Save these:
```
STRIPE_SECRET_KEY=sk_test_51xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
STRIPE_PUBLISHABLE_KEY=pk_test_51xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Testing Stripe Locally (Optional)
```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Forward webhooks to localhost
stripe listen --forward-to localhost:8000/api/payment/webhook/stripe

# This gives you a webhook secret: whsec_xxxxx
```

**Test card numbers:**
- Success: `4242 4242 4242 4242`
- Decline: `4000 0000 0000 0002`
- Require authentication: `4000 0025 0000 3155`
- Any future expiry, any CVC, any postal code

---

## 4️⃣ OneSignal Setup (10 minutes)

**What you get:** Unlimited push notifications - FREE forever!

### Step 1: Create Account
1. Go to **https://onesignal.com**
2. Click **"Get Started Free"**
3. Sign up with email or Google
4. Verify email if needed

### Step 2: Create an App
1. Click **"New App/Website"**
2. App Name: `My Startup App`
3. Choose your platform:
   - **Web Push:** For website notifications
   - **Mobile:** For iOS/Android apps
   - **Email:** For email notifications (optional)

### For Web Push Setup:
1. Select **"Web Push"**
2. Select **"Typical Site"** (or choose your framework)
3. Site URL: `https://yourdomain.com` (or `http://localhost:3000` for testing)
4. Auto Resubscribe: **Enabled** (recommended)
5. Default Notification Icon: Upload icon (optional)
6. Click **"Save"**

### Step 3: Get API Keys
1. Go to **Settings** → **Keys & IDs**
2. Copy these:

```bash
OneSignal App ID  → ONESIGNAL_APP_ID
REST API Key      → ONESIGNAL_API_KEY
```

### Step 4: Install Web SDK (Frontend)
1. Go to **Settings** → **Platforms** → **Web Push**
2. Choose setup option:
   - **Typical Site:** Copy the `<script>` tag
   - **React/Vue/Angular:** Use npm package

**For React (Next.js):**
```bash
npm install react-onesignal
```

**OneSignal init code:**
```javascript
import OneSignal from 'react-onesignal';

OneSignal.init({
  appId: "your-app-id-here",
  allowLocalhostAsSecureOrigin: true, // for local testing
});
```

**✅ Done!** Save these:
```
ONESIGNAL_APP_ID=12345678-1234-1234-1234-123456789012
ONESIGNAL_API_KEY=AbCdEfGhIjKlMnOpQrStUvWxYz123456789
```

### Testing OneSignal
1. Open your website
2. You should see notification permission prompt
3. Click **"Allow"**
4. Send test notification:
   - Go to OneSignal dashboard → **Messages** → **New Push**
   - Write message → **Send to Test Device**

---

## 5️⃣ Configure Your .env File (5 minutes)

### Step 1: Copy the Template
```bash
cd /Users/caribou/WebSite/backend
cp .env.startup-free .env
```

### Step 2: Edit .env with Your Keys
```bash
# Open in your editor
code .env
# or
nano .env
# or
vim .env
```

### Step 3: Replace All Placeholders
```bash
# ============================================
# Configuration Preset: startup-free-tier
# ============================================

ENVIRONMENT=production

# Plugin Provider Selections
CACHE_PROVIDER=memory
STORAGE_PROVIDER=supabase
EMAIL_PROVIDER=resend
SMS_PROVIDER=console
PAYMENT_PROVIDER=stripe
PUSH_NOTIFICATION_PROVIDER=onesignal
LOGGING_PROVIDER=console
MONITORING_PROVIDERS=console
ANALYTICS_PROVIDERS=internal
RATE_LIMIT_PROVIDER=memory

# ============================================
# 1️⃣ SUPABASE - Replace with your values
# ============================================
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_STORAGE_BUCKET=uploads

# ============================================
# 2️⃣ RESEND - Replace with your API key
# ============================================
RESEND_API_KEY=re_123456789_AbCdEfGhIjKlMnOpQrStUvWxYz

# ============================================
# 3️⃣ STRIPE - Replace with your keys
# ============================================
STRIPE_SECRET_KEY=sk_test_51xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
STRIPE_PUBLISHABLE_KEY=pk_test_51xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ============================================
# 4️⃣ ONESIGNAL - Replace with your keys
# ============================================
ONESIGNAL_APP_ID=12345678-1234-1234-1234-123456789012
ONESIGNAL_API_KEY=AbCdEfGhIjKlMnOpQrStUvWxYz123456789

# ============================================
# Optional: Add your other settings
# ============================================
JWT_SECRET=your-super-secret-jwt-key-change-this
DATABASE_URL=postgresql://user:password@localhost/dbname
```

### Step 4: Verify Configuration
```bash
# Check your .env file
cat .env | grep -v "^#" | grep "="

# Make sure no placeholder values remain
cat .env | grep "your_" && echo "❌ Still has placeholders!" || echo "✅ Looks good!"
```

---

## 🚀 Launch Your App!

### Step 1: Install Dependencies
```bash
cd /Users/caribou/WebSite/backend
pip install -r requirements.txt
```

### Step 2: Run Backend
```bash
uvicorn main:app --reload
```

**Your API is now running at:** http://localhost:8000

### Step 3: Test Each Service

**Test Supabase:**
```bash
curl http://localhost:8000/api/health
```

**Test Email (Resend):**
```bash
curl -X POST http://localhost:8000/api/email/send \
  -H "Content-Type: application/json" \
  -d '{
    "to": "your-email@example.com",
    "subject": "Test Email",
    "body": "Hello from your startup!"
  }'
```

**Test Payment (Stripe):**
```bash
curl -X POST http://localhost:8000/api/payment/create-checkout \
  -H "Content-Type: application/json" \
  -d '{
    "price_id": "price_xxxxx",
    "success_url": "http://localhost:3000/success",
    "cancel_url": "http://localhost:3000/cancel"
  }'
```

**Test Push Notification (OneSignal):**
```bash
curl -X POST http://localhost:8000/api/notifications/send \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Notification",
    "message": "Hello from your app!",
    "user_ids": ["user-123"]
  }'
```

---

## 📊 Your Free Tier Limits

| Service | What You Get FREE | Monthly Value |
|---------|------------------|---------------|
| **Supabase** | 500 MB DB + 1 GB storage + Auth | ~$25 |
| **Resend** | 3,000 emails/month | ~$10 |
| **Stripe** | Unlimited (pay per transaction) | $0 |
| **OneSignal** | Unlimited notifications | ~$150 |
| **Total** | Full production stack | **~$185/mo value** |

---

## 🆘 Troubleshooting

### "Supabase connection failed"
- Check `SUPABASE_URL` is correct (should be https://xxx.supabase.co)
- Verify `SUPABASE_ANON_KEY` and `SERVICE_KEY` are different
- Make sure you created the `uploads` bucket

### "Resend authentication failed"
- API key should start with `re_`
- Make sure you copied the full key
- Check if domain is verified (or use `onboarding@resend.dev`)

### "Stripe webhook signature verification failed"
- Make sure webhook secret starts with `whsec_`
- For local testing, use Stripe CLI
- Endpoint URL must match exactly

### "OneSignal push not received"
- Check browser permissions (allow notifications)
- Verify App ID is correct
- Make sure you're subscribed (check browser console)
- Use HTTPS or localhost (HTTP won't work except localhost)

---

## 📚 Next Steps

Once everything is working:

1. **Deploy your backend:**
   - Render.com (free tier)
   - Railway.app (free trial)
   - Fly.io (free tier)

2. **Deploy your frontend:**
   - Vercel (free for personal)
   - Netlify (free tier)
   - Cloudflare Pages (free)

3. **Monitor usage:**
   - Watch your free tier limits
   - Set up alerts in each dashboard
   - Upgrade when needed

4. **When you outgrow free tier:**
   ```bash
   # Switch to cost-optimized ($97.50/month)
   python generate_env.py cost-optimized
   ```

---

## 🎯 Quick Reference Card

Save this for later:

```bash
# SERVICE          | DASHBOARD URL
# ================|================================
# Supabase        | https://app.supabase.com
# Resend          | https://resend.com/dashboard
# Stripe          | https://dashboard.stripe.com
# OneSignal       | https://app.onesignal.com

# DOCUMENTATION
# Supabase        | https://supabase.com/docs
# Resend          | https://resend.com/docs
# Stripe          | https://stripe.com/docs
# OneSignal       | https://documentation.onesignal.com
```

---

## ✅ Final Checklist

Before you start development:

- [ ] All 4 services signed up
- [ ] All API keys saved in `.env`
- [ ] No placeholder values in `.env`
- [ ] Backend runs without errors
- [ ] Test email sent successfully
- [ ] Stripe test payment works
- [ ] Push notification received
- [ ] Ready to build! 🚀

---

**Need help?** Check the troubleshooting section or refer to each service's documentation.

**Good luck with your startup!** 🎉

