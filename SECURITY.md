# Security Guidelines

## 🔐 Critical: Never Commit These Files

### Environment Files (Contains ALL secrets)
- ❌ `.env`
- ❌ `.env.local`
- ❌ `.env.production`
- ❌ `backend/.env`
- ✅ `env.example` (template only)
- ✅ `env.local.example` (template only)

### API Keys & Secrets
These should ONLY be in `.env` files (which are gitignored):
- Supabase URL and keys
- Stripe secret keys
- Redis URLs with passwords
- Docker registry tokens
- Email provider API keys
- JWT secret keys
- Webhook secrets
- Database passwords

### Other Sensitive Files
- ❌ `secrets.json`
- ❌ `credentials.json`
- ❌ `*.pem` (private keys)
- ❌ `*.key` (SSL/TLS keys)
- ❌ `*.cert` (certificates)
- ❌ `dump.rdb` (Redis dump - may contain session data)
- ❌ `*.sqlite` (local databases)

## ✅ Safe to Commit

- ✅ `env.example` - Template with placeholder values
- ✅ `requirements.txt` - Python dependencies (no secrets)
- ✅ `package.json` - Node dependencies (no secrets)
- ✅ `*.md` - Documentation
- ✅ Source code files
- ✅ `schema.sql` - Database structure (no data)
- ✅ `.gitignore` itself

## 🛡️ Security Checklist

### Before First Commit

- [ ] `.gitignore` files are in place
- [ ] `.env` files are NOT tracked
- [ ] No hardcoded API keys in source code
- [ ] All secrets use environment variables
- [ ] Example env files have placeholder values

### Before Every Commit

```bash
# Check what's being committed
git status

# Look for sensitive files
git diff

# Check for accidentally staged secrets
git diff --cached

# Search for potential secrets
grep -r "sk_live_" .
grep -r "api_key" .
grep -r "password" .
```

### If You Accidentally Commit Secrets

**IMMEDIATELY:**

1. **Rotate ALL exposed credentials**
   ```bash
   # Change in respective services:
   # - Stripe: Generate new API keys
   # - Supabase: Rotate keys
   # - Redis: Change password
   # - Email: Generate new API key
   ```

2. **Remove from Git history**
   ```bash
   # Use git-filter-repo or BFG Repo-Cleaner
   # DO NOT just delete the file - it's still in history!
   
   # Option 1: BFG Repo-Cleaner (recommended)
   bfg --delete-files .env
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   
   # Option 2: git filter-repo
   git filter-repo --invert-paths --path .env
   ```

3. **Force push (if already pushed)**
   ```bash
   git push --force
   # WARNING: Coordinate with team first!
   ```

## 🔍 Scanning for Secrets

### Install git-secrets (Recommended)

```bash
# Install
brew install git-secrets  # macOS
# or download from: https://github.com/awslabs/git-secrets

# Setup in repo
cd /path/to/repo
git secrets --install
git secrets --register-aws

# Add custom patterns
git secrets --add 'sk_live_[a-zA-Z0-9]{24}'  # Stripe live keys
git secrets --add 'sk_test_[a-zA-Z0-9]{24}'  # Stripe test keys
git secrets --add 'eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*'  # JWT tokens
git secrets --add 'supabase_[a-zA-Z0-9]{40}'  # Supabase keys
```

### Use gitleaks

```bash
# Install
brew install gitleaks

# Scan repository
gitleaks detect --source . --verbose

# Scan before commit
gitleaks protect --staged --verbose
```

## 🔑 Environment Variable Management

### Development

```bash
# Backend
cp backend/env.example backend/.env
# Edit backend/.env with your development credentials

# Frontend
cp env.local.example .env.local
# Edit .env.local with your development credentials
```

### Production

**Never store production secrets in code!**

Use environment variable management:

- **Vercel**: Dashboard → Project Settings → Environment Variables
- **Render**: Dashboard → Environment → Add Environment Variable
- **GitHub Actions**: Repository Settings → Secrets and Variables
- **Docker**: Use secrets or env files (not in image)

## 🚨 What Each Secret Does

### Critical Secrets (Highest Risk)

| Secret | Used For | Risk if Exposed |
|--------|----------|-----------------|
| `STRIPE_SECRET_KEY` | Process payments | Financial fraud |
| `SUPABASE_SERVICE_KEY` | Bypass RLS, admin access | Full database access |
| `JWT_SECRET_KEY` | Sign auth tokens | Account takeover |
| `STRIPE_WEBHOOK_SECRET` | Verify webhooks | Fake payment events |

### Important Secrets (High Risk)

| Secret | Used For | Risk if Exposed |
|--------|----------|-----------------|
| `DOCKER_REGISTRY_TOKEN` | Push/pull images | Unauthorized downloads |
| `EMAIL_PROVIDER_API_KEY` | Send emails | Spam from your account |
| `REDIS_URL` (with password) | Cache access | Session hijacking |

### Moderate Secrets

| Secret | Used For | Risk if Exposed |
|--------|----------|-----------------|
| `SUPABASE_ANON_KEY` | Client-side auth | Limited (RLS protected) |
| `STRIPE_PUBLISHABLE_KEY` | Client-side Stripe | Read-only, low risk |

## 🛠️ Safe Development Practices

### 1. Use Environment Variables

```python
# ❌ NEVER DO THIS
stripe.api_key = "sk_live_abc123..."

# ✅ DO THIS
from config import settings
stripe.api_key = settings.stripe_secret_key
```

```typescript
// ❌ NEVER DO THIS
const apiKey = "pk_live_abc123..."

// ✅ DO THIS
const apiKey = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY
```

### 2. Validate .gitignore

```bash
# Check if .env is ignored
git check-ignore backend/.env
# Should output: backend/.env

# If not ignored, check .gitignore
cat .gitignore | grep ".env"
```

### 3. Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash

# Check for .env files
if git diff --cached --name-only | grep -E "\.env$|\.env\.local$"; then
    echo "❌ ERROR: Attempting to commit .env file!"
    echo "Please remove it from staging:"
    echo "  git reset HEAD .env"
    exit 1
fi

# Check for hardcoded secrets
if git diff --cached | grep -E "sk_live_|sk_test_|eyJ[a-zA-Z0-9]"; then
    echo "⚠️  WARNING: Potential secret detected in commit!"
    echo "Please review your changes carefully."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

exit 0
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

## 📋 Emergency Response Plan

### If Secrets Are Leaked

1. **STOP** - Don't commit/push anymore
2. **ASSESS** - What was exposed?
3. **ROTATE** - Change ALL exposed credentials
4. **REMOVE** - Clean Git history
5. **AUDIT** - Check for unauthorized access
6. **MONITOR** - Watch for suspicious activity
7. **NOTIFY** - Inform team/users if needed

### Rotation Procedures

**Stripe:**
1. Dashboard → Developers → API keys
2. Click "Reveal test/live key"
3. Roll keys
4. Update `.env` files
5. Redeploy

**Supabase:**
1. Project Settings → API
2. Click "Generate new anon key"
3. Click "Generate new service key"
4. Update `.env` files
5. Redeploy

**Redis:**
1. Update password in Redis provider
2. Update `REDIS_URL` in `.env`
3. Restart services

## ✅ Verification Commands

```bash
# Check gitignore is working
git status --ignored

# Verify .env is not tracked
git ls-files | grep ".env"
# Should return nothing

# Check for secrets in code
grep -r "sk_live_" . --exclude-dir=node_modules --exclude-dir=.git
grep -r "sk_test_" . --exclude-dir=node_modules --exclude-dir=.git

# Verify example files only
ls -la | grep env
# Should show: env.example, env.local.example
# Should NOT show: .env, .env.local
```

## 🎓 Training

**Everyone on the team should:**
- [ ] Read this document
- [ ] Understand which files contain secrets
- [ ] Know how to use `.env` files
- [ ] Install `git-secrets` or `gitleaks`
- [ ] Review commits before pushing
- [ ] Know the emergency response plan

---

## 🔒 Remember

**The three rules of secrets:**

1. **Never commit secrets to Git** (use .env files)
2. **Never hardcode secrets in code** (use environment variables)
3. **Never share secrets in chat/email** (use secure secret management)

Stay secure! 🛡️



