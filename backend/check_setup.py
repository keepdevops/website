#!/usr/bin/env python3
import os
from pathlib import Path

print("🔍 Checking SaaS Platform Setup...\n")

required_env_vars = [
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "SUPABASE_SERVICE_KEY",
    "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET",
    "REDIS_URL",
    "DOCKER_REGISTRY_URL"
]

modules = [
    "core", "auth", "subscriptions", "webhooks",
    "customers", "docker_registry", "campaigns", "analytics"
]

print("📦 Checking modules...")
for module in modules:
    path = Path(module)
    if path.exists():
        files = list(path.glob("*.py"))
        print(f"  ✅ {module}: {len(files)} files")
    else:
        print(f"  ❌ {module}: Missing!")

print("\n🔑 Checking environment (from .env file)...")
env_file = Path(".env")
if env_file.exists():
    with open(env_file) as f:
        env_content = f.read()
    
    for var in required_env_vars:
        if var in env_content and not env_content.split(var)[1].split('\n')[0].strip().startswith('=your_'):
            print(f"  ✅ {var}")
        else:
            print(f"  ⚠️  {var}: Not configured")
else:
    print("  ⚠️  .env file not found. Copy from env.example")

print("\n📄 Checking key files...")
key_files = [
    "main.py", "config.py", "requirements.txt",
    "render.yaml", "Dockerfile", "README.md"
]

for file in key_files:
    if Path(file).exists():
        print(f"  ✅ {file}")
    else:
        print(f"  ❌ {file}: Missing!")

print("\n✨ Setup check complete!")
print("\nNext steps:")
print("1. Copy env.example to .env and fill in values")
print("2. Install: pip install -r requirements.txt")
print("3. Run database schema in Supabase")
print("4. Start: uvicorn main:app --reload")



