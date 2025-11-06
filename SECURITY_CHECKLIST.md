# Security Checklist - Quick Reference

## ✅ Before Your First Git Commit

```bash
# 1. Verify .gitignore files exist
ls -la .gitignore
ls -la backend/.gitignore

# 2. Create your .env files from examples
cp env.local.example .env.local
cp backend/env.example backend/.env

# 3. Add your actual secrets to .env files
# Edit .env.local and backend/.env with real credentials

# 4. Verify .env files are ignored
git status
# Should NOT show .env or .env.local files

# 5. Check what will be committed
git add .
git status
# Review carefully - no .env files should appear!

# 6. Safe to commit
git commit -m "Initial commit"
```

## 🚫 NEVER Commit These Files

```
❌ .env
❌ .env.local
❌ .env.production
❌ backend/.env
❌ secrets.json
❌ credentials.json
❌ *.pem
❌ *.key
❌ dump.rdb
```

## ✅ Safe to Commit

```
✅ env.example
✅ env.local.example
✅ backend/env.example
✅ .gitignore
✅ *.md files
✅ Source code
✅ requirements.txt
✅ package.json
```

## 🔍 Quick Security Scan

```bash
# Before committing
git diff --cached | grep -i "api_key\|secret\|password\|sk_live\|sk_test"

# If anything found, remove it!
```

## 🆘 Emergency: I Committed Secrets!

```bash
# 1. IMMEDIATELY rotate all exposed credentials in:
# - Stripe dashboard
# - Supabase dashboard  
# - Redis provider
# - Email provider

# 2. Remove from last commit (if not pushed yet)
git reset HEAD~1
git add .gitignore
git commit -m "Add gitignore"

# 3. If already pushed - contact team ASAP!
# You'll need to:
# - Rotate credentials
# - Clean Git history with BFG or git-filter-repo
# - Force push
```

## 📝 Correct Pattern

### ❌ Wrong (Hardcoded)
```python
stripe.api_key = "sk_live_abc123..."
```

### ✅ Correct (Environment Variable)
```python
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
```

## 🎯 Pre-Commit Commands

```bash
# Always run before git add
echo "Checking for secrets..."
grep -r "sk_live_" . --exclude-dir=node_modules --exclude-dir=.git
grep -r "sk_test_" . --exclude-dir=node_modules --exclude-dir=.git

# If found, use environment variables instead!
```

## 📊 File Status Legend

| Symbol | Meaning |
|--------|---------|
| ❌ | NEVER commit |
| ✅ | Safe to commit |
| ⚠️  | Review carefully |

## 🔐 Quick Test

```bash
# This should output nothing (all ignored)
git ls-files | grep "\.env"

# This should show example files only
ls -la | grep env
# Expected: env.example, env.local.example
# NOT: .env, .env.local
```

## 💡 Remember

1. **Example files** = Templates (safe) ✅
2. **Actual .env files** = Secrets (never commit) ❌
3. **When in doubt** = Don't commit! 🛑

---

**Read full guide:** `SECURITY.md`



