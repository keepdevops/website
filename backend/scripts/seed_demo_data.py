#!/usr/bin/env python3
"""
Seed Supabase with demo data for products, campaigns, customers, and subscriptions.

Usage:
    ./scripts/seed_demo_data.py
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from typing import Dict, List

from seed_utils import (
    API_TIMEOUT,
    DEMO_CAMPAIGNS,
    DEMO_PASSWORD,
    DEMO_PRODUCTS,
    DEMO_SUBSCRIPTIONS,
    DEMO_USERS,
    SeedError,
    column_exists,
    ensure_users,
    get_env_var,
    load_env,
    rest_upsert,
    table_exists,
)


def upsert_profiles(
    project_url: str,
    service_key: str,
    demo_users: List[Dict[str, str]],
    email_to_id: Dict[str, str],
) -> None:
    supports_full_name = column_exists(project_url, service_key, "profiles", "full_name")
    timestamp = datetime.now(timezone.utc).isoformat()
    rows: List[Dict[str, str]] = []
    for user in demo_users:
        row: Dict[str, str] = {
            "id": email_to_id[user["email"]],
            "email": user["email"],
            "is_admin": user["is_admin"],
            "stripe_customer_id": user["stripe_customer_id"],
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        if supports_full_name:
            row["full_name"] = user["full_name"]
        rows.append(row)
    rest_upsert(project_url, service_key, "profiles", rows)
    print(f"✔ Upserted {len(rows)} profiles.")


def upsert_products(project_url: str, service_key: str) -> None:
    if not table_exists(project_url, service_key, "products"):
        print("⚠ Skipping products seed: table 'products' not found. Run Supabase migrations.")
        return
    timestamp = datetime.now(timezone.utc).isoformat()
    rows = [{**product, "created_at": timestamp} for product in DEMO_PRODUCTS]
    rest_upsert(project_url, service_key, "products", rows)
    print(f"✔ Upserted {len(rows)} products.")


def upsert_campaigns(project_url: str, service_key: str) -> None:
    if not table_exists(project_url, service_key, "campaigns"):
        print("⚠ Skipping campaigns seed: table 'campaigns' not found. Run Supabase migrations.")
        return

    rows: List[Dict[str, str]] = []
    timestamp = datetime.now(timezone.utc).isoformat()
    for campaign in DEMO_CAMPAIGNS:
        data = {**campaign}
        sent_at = data.get("sent_at")
        scheduled_at = data.get("scheduled_at")
        if isinstance(sent_at, datetime):
            data["sent_at"] = sent_at.isoformat()
        if isinstance(scheduled_at, datetime):
            data["scheduled_at"] = scheduled_at.isoformat()
        data.setdefault("created_at", timestamp)
        data.setdefault("total_recipients", 0)
        data.setdefault("opened_count", 0)
        data.setdefault("clicked_count", 0)
        rows.append(data)
    rest_upsert(project_url, service_key, "campaigns", rows)
    print(f"✔ Upserted {len(rows)} campaigns.")


def upsert_subscriptions(
    project_url: str,
    service_key: str,
    email_to_id: Dict[str, str],
) -> None:
    if not table_exists(project_url, service_key, "subscriptions"):
        print("⚠ Skipping subscriptions seed: table 'subscriptions' not found. Run Supabase migrations.")
        return

    required = {
        "user_id": column_exists(project_url, service_key, "subscriptions", "user_id"),
        "status": column_exists(project_url, service_key, "subscriptions", "status"),
    }
    if not all(required.values()):
        print("⚠ Skipping subscriptions seed: required columns missing on 'subscriptions'.")
        return

    optional = {
        "stripe_customer_id": column_exists(project_url, service_key, "subscriptions", "stripe_customer_id"),
        "stripe_subscription_id": column_exists(project_url, service_key, "subscriptions", "stripe_subscription_id"),
        "current_period_start": column_exists(project_url, service_key, "subscriptions", "current_period_start"),
        "current_period_end": column_exists(project_url, service_key, "subscriptions", "current_period_end"),
        "cancel_at_period_end": column_exists(project_url, service_key, "subscriptions", "cancel_at_period_end"),
        "created_at": column_exists(project_url, service_key, "subscriptions", "created_at"),
        "updated_at": column_exists(project_url, service_key, "subscriptions", "updated_at"),
        "tier": column_exists(project_url, service_key, "subscriptions", "tier"),
    }

    rows: List[Dict[str, str]] = []
    for subscription in DEMO_SUBSCRIPTIONS:
        user_id = email_to_id.get(subscription["user_email"])
        if not user_id:
            print(f"⚠ Skipping subscription for {subscription['user_email']}: user id not found.")
            continue

        row: Dict[str, str] = {"id": subscription["id"], "user_id": user_id, "status": subscription["status"]}
        if optional["stripe_customer_id"]:
            row["stripe_customer_id"] = subscription["stripe_customer_id"]
        if optional["stripe_subscription_id"]:
            row["stripe_subscription_id"] = subscription["stripe_subscription_id"]
        if optional["current_period_start"]:
            row["current_period_start"] = subscription["current_period_start"].isoformat()
        if optional["current_period_end"]:
            row["current_period_end"] = subscription["current_period_end"].isoformat()
        if optional["cancel_at_period_end"]:
            row["cancel_at_period_end"] = subscription["cancel_at_period_end"]
        if optional["tier"]:
            row["tier"] = subscription.get("tier", "standard")
        timestamp = datetime.now(timezone.utc).isoformat()
        if optional["created_at"]:
            row["created_at"] = timestamp
        if optional["updated_at"]:
            row["updated_at"] = timestamp
        rows.append(row)

    if rows:
        rest_upsert(project_url, service_key, "subscriptions", rows)
        print(f"✔ Upserted {len(rows)} subscriptions.")
    else:
        print("⚠ No subscriptions to upsert.")


def main() -> int:
    try:
        load_env()
        supabase_url = get_env_var("SUPABASE_URL")
        service_key = get_env_var("SUPABASE_SERVICE_KEY")

        email_to_id = ensure_users(supabase_url, service_key, DEMO_USERS)
        upsert_profiles(supabase_url, service_key, DEMO_USERS, email_to_id)
        upsert_products(supabase_url, service_key)
        upsert_campaigns(supabase_url, service_key)
        upsert_subscriptions(supabase_url, service_key, email_to_id)

        print("✅ Demo data seeded successfully.")
        return 0
    except SeedError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Seed Supabase with demo data for products, campaigns, customers, and subscriptions.

This script:
1. Ensures demo users exist (creates via Supabase Admin API if missing).
2. Upserts profiles with admin/customer metadata.
3. Populates products, campaigns, and subscriptions tables with showcase content.

Usage:
    ./scripts/seed_demo_data.py

Environment:
    Reads SUPABASE_URL and SUPABASE_SERVICE_KEY from environment or ../.env.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple
from uuid import UUID, uuid5, NAMESPACE_URL

import requests


API_TIMEOUT = 10  # seconds
DEMO_PASSWORD = "DemoPass123!"

# Deterministic UUIDs for seeded content
def deterministic_uuid(name: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"demo:{name}"))


DEMO_PRODUCTS = [
    {
        "id": deterministic_uuid("product:redline"),
        "name": "Redline Container Acceleration Suite",
        "description": "Bundle of CI/CD automations, security scans, and live dashboards for container delivery.",
        "docker_image": "registry.example.com/redline/app:latest",
        "stripe_product_id": "prod_redline_demo",
        "active": True,
    },
    {
        "id": deterministic_uuid("product:bytecode"),
        "name": "Bytecode Analyzer",
        "description": "Static analysis toolkit that surfaces dependency drift, CVEs, and upgrade insights.",
        "docker_image": "registry.example.com/bytecode/analyzer:stable",
        "stripe_product_id": "prod_bytecode_demo",
        "active": True,
    },
]

DEMO_CAMPAIGNS = [
    {
        "id": deterministic_uuid("campaign:redline-launch"),
        "name": "Redline Launch",
        "subject": "Launch Week: Accelerate Kubernetes deliveries 🚀",
        "content": "<h1>Redline Launch</h1><p>See how Redline accelerates your workflow.</p>",
        "segment": "all",
        "status": "sent",
        "sent_at": datetime.now(timezone.utc) - timedelta(days=14),
        "total_recipients": 128,
        "opened_count": 92,
        "clicked_count": 41,
    },
    {
        "id": deterministic_uuid("campaign:redline-upgrade"),
        "name": "Upgrade Invite",
        "subject": "Unlock Redline Pro in 2 clicks",
        "content": "<p>Upgrade to Redline Pro for advanced governance features.</p>",
        "segment": "active_subscribers",
        "status": "scheduled",
        "scheduled_at": datetime.now(timezone.utc) + timedelta(days=3),
    },
]

DEMO_USERS = [
    {
        "email": "redischeck@gmail.com",
        "full_name": "Redline Admin",
        "is_admin": True,
        "stripe_customer_id": "cus_redline_admin",
    },
    {
        "email": "alex.ops@example.com",
        "full_name": "Alex Ops",
        "is_admin": False,
        "stripe_customer_id": "cus_demo_ops",
    },
    {
        "email": "taylor.finance@example.com",
        "full_name": "Taylor Finance",
        "is_admin": False,
        "stripe_customer_id": "cus_demo_finance",
    },
]

DEMO_SUBSCRIPTIONS = [
    {
        "id": deterministic_uuid("subscription:alex"),
        "user_email": "alex.ops@example.com",
        "stripe_customer_id": "cus_demo_ops",
        "stripe_subscription_id": "sub_demo_ops",
        "status": "active",
        "tier": "pro",
        "current_period_start": datetime.now(timezone.utc) - timedelta(days=10),
        "current_period_end": datetime.now(timezone.utc) + timedelta(days=20),
        "cancel_at_period_end": False,
    },
    {
        "id": deterministic_uuid("subscription:taylor"),
        "user_email": "taylor.finance@example.com",
        "stripe_customer_id": "cus_demo_finance",
        "stripe_subscription_id": "sub_demo_finance",
        "status": "trialing",
        "tier": "starter",
        "current_period_start": datetime.now(timezone.utc) - timedelta(days=3),
        "current_period_end": datetime.now(timezone.utc) + timedelta(days=11),
        "cancel_at_period_end": False,
    },
]


class SeedError(Exception):
    """Custom error for seeding failures."""


def load_env() -> None:
    """Populate environment variables from local .env if not already set."""
    candidates = [
        Path(__file__).resolve().parent.parent / ".env",
        Path(__file__).resolve().parents[2] / ".env",
    ]
    for candidate in candidates:
        if not candidate.exists():
            continue
        for line in candidate.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)
        break


def get_env_var(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SeedError(f"Environment variable {name} is required.")
    return value


def supabase_headers(service_key: str) -> Dict[str, str]:
    return {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
    }


def admin_request(
    method: str,
    project_url: str,
    service_key: str,
    *,
    params: Dict[str, Any] | None = None,
    json: Dict[str, Any] | None = None,
) -> requests.Response:
    endpoint = f"{project_url.rstrip('/')}/auth/v1/admin/users"
    response = requests.request(
        method=method,
        url=endpoint,
        headers=supabase_headers(service_key),
        params=params,
        json=json,
        timeout=API_TIMEOUT,
    )
    if not response.ok:
        raise SeedError(
            f"Admin API {method} {endpoint} failed with status {response.status_code}: {response.text}"
        )
    return response


def column_exists(project_url: str, service_key: str, table: str, column: str) -> bool:
    endpoint = f"{project_url.rstrip('/')}/rest/v1/{table}"
    headers = supabase_headers(service_key)
    params = {"select": column, "limit": 1}
    response = requests.get(endpoint, headers=headers, params=params, timeout=API_TIMEOUT)

    if response.ok:
        return True

    if response.status_code == 400 and (
        "PGRST204" in response.text or "does not exist" in response.text
    ):
        return False

    raise SeedError(
        f"Unable to determine if column '{column}' exists on '{table}': "
        f"{response.status_code} {response.text}"
    )


def table_exists(project_url: str, service_key: str, table: str) -> bool:
    endpoint = f"{project_url.rstrip('/')}/rest/v1/{table}"
    headers = supabase_headers(service_key)
    response = requests.get(endpoint, headers=headers, params={"select": "id", "limit": 1}, timeout=API_TIMEOUT)

    if response.ok:
        return True

    if response.status_code == 404 and "PGRST205" in response.text:
        return False

    raise SeedError(
        f"Unable to determine if table '{table}' exists: {response.status_code} {response.text}"
    )


def ensure_auth_user(
    project_url: str,
    service_key: str,
    email: str,
) -> Tuple[str, bool]:
    """Return user id, creating the auth user if needed."""
    list_response = admin_request("GET", project_url, service_key, params={"per_page": 200})
    for user in list_response.json().get("users") or []:
        if user.get("email") == email:
            return user["id"], False

    payload = {
        "email": email,
        "password": DEMO_PASSWORD,
        "email_confirm": True,
    }
    create_response = requests.post(
        f"{project_url.rstrip('/')}/auth/v1/admin/users",
        headers=supabase_headers(service_key),
        json=payload,
        timeout=API_TIMEOUT,
    )

    if create_response.ok:
        data = create_response.json()
        user = data.get("user", data)
        if not user or not user.get("id"):
            raise SeedError(f"Failed to parse created user response for {email}: {data}")
        return user["id"], True

    if create_response.status_code in (400, 422):
        list_response = admin_request("GET", project_url, service_key, params={"per_page": 200})
        for user in list_response.json().get("users") or []:
            if user.get("email") == email:
                return user["id"], False

    raise SeedError(
        f"Failed to create or find auth user for {email}: "
        f"{create_response.status_code} {create_response.text}"
    )


def ensure_users(
    project_url: str,
    service_key: str,
    demo_users: List[Dict[str, Any]],
) -> Dict[str, str]:
    email_to_id: Dict[str, str] = {}
    created = 0
    for user in demo_users:
        user_id, was_created = ensure_auth_user(project_url, service_key, user["email"])
        email_to_id[user["email"]] = user_id
        if was_created:
            created += 1
    print(f"✔ Ensured {len(demo_users)} auth users ({created} created).")
    return email_to_id


def rest_upsert(
    project_url: str,
    service_key: str,
    table: str,
    rows: List[Dict[str, Any]],
    *,
    on_conflict: str = "id",
) -> None:
    if not rows:
        return
    endpoint = f"{project_url.rstrip('/')}/rest/v1/{table}"
    headers = supabase_headers(service_key)
    headers["Prefer"] = "resolution=merge-duplicates"
    params = {"on_conflict": on_conflict} if on_conflict else None
    for row in rows:
        response = requests.post(
            endpoint,
            headers=headers,
            params=params,
            json=row,
            timeout=API_TIMEOUT,
        )
        if not response.ok:
            raise SeedError(
                f"Failed to upsert into {table}: {response.status_code} {response.text}"
            )


def upsert_profiles(
    project_url: str,
    service_key: str,
    demo_users: List[Dict[str, Any]],
    email_to_id: Dict[str, str],
) -> None:
    supports_full_name = column_exists(project_url, service_key, "profiles", "full_name")
    rows = []
    for user in demo_users:
        user_id = email_to_id[user["email"]]
        row = {
            "id": user_id,
            "email": user["email"],
            "is_admin": user["is_admin"],
            "stripe_customer_id": user["stripe_customer_id"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        if supports_full_name:
            row["full_name"] = user["full_name"]
        rows.append(row)
    rest_upsert(project_url, service_key, "profiles", rows)
    print(f"✔ Upserted {len(rows)} profiles.")


def upsert_products(project_url: str, service_key: str) -> None:
    if not table_exists(project_url, service_key, "products"):
        print("⚠ Skipping products seed: table 'products' not found. Run Supabase migrations.")
        return
    rows = []
    now = datetime.now(timezone.utc).isoformat()
    for product in DEMO_PRODUCTS:
        data = {
            **product,
            "created_at": now,
        }
        rows.append(data)
    rest_upsert(project_url, service_key, "products", rows)
    print(f"✔ Upserted {len(rows)} products.")


def upsert_campaigns(project_url: str, service_key: str) -> None:
    if not table_exists(project_url, service_key, "campaigns"):
        print("⚠ Skipping campaigns seed: table 'campaigns' not found. Run Supabase migrations.")
        return
    rows = []
    now = datetime.now(timezone.utc).isoformat()
    for campaign in DEMO_CAMPAIGNS:
        data = {**campaign}
        if "sent_at" in data and isinstance(data["sent_at"], datetime):
            data["sent_at"] = data["sent_at"].isoformat()
        if "scheduled_at" in data and isinstance(data["scheduled_at"], datetime):
            data["scheduled_at"] = data["scheduled_at"].isoformat()
        data.setdefault("created_at", now)
        data.setdefault("total_recipients", 0)
        data.setdefault("opened_count", 0)
        data.setdefault("clicked_count", 0)
        rows.append(data)
    rest_upsert(project_url, service_key, "campaigns", rows)
    print(f"✔ Upserted {len(rows)} campaigns.")


def upsert_subscriptions(
    project_url: str,
    service_key: str,
    email_to_id: Dict[str, str],
) -> None:
    if not table_exists(project_url, service_key, "subscriptions"):
        print("⚠ Skipping subscriptions seed: table 'subscriptions' not found. Run Supabase migrations.")
        return
    required_columns = {
        "user_id": column_exists(project_url, service_key, "subscriptions", "user_id"),
        "status": column_exists(project_url, service_key, "subscriptions", "status"),
    }
    if not all(required_columns.values()):
        print("⚠ Skipping subscriptions seed: required columns missing on 'subscriptions'.")
        return

    optional_columns = {
        "stripe_customer_id": column_exists(project_url, service_key, "subscriptions", "stripe_customer_id"),
        "stripe_subscription_id": column_exists(project_url, service_key, "subscriptions", "stripe_subscription_id"),
        "current_period_start": column_exists(project_url, service_key, "subscriptions", "current_period_start"),
        "current_period_end": column_exists(project_url, service_key, "subscriptions", "current_period_end"),
        "cancel_at_period_end": column_exists(project_url, service_key, "subscriptions", "cancel_at_period_end"),
        "created_at": column_exists(project_url, service_key, "subscriptions", "created_at"),
        "updated_at": column_exists(project_url, service_key, "subscriptions", "updated_at"),
        "tier": column_exists(project_url, service_key, "subscriptions", "tier"),
    }

    rows = []
    for subscription in DEMO_SUBSCRIPTIONS:
        user_email = subscription["user_email"]
        user_id = email_to_id.get(user_email)
        if not user_id:
            print(f"⚠ Skipping subscription for {user_email}: user id not found.")
            continue
        row = {
            "id": subscription["id"],
            "user_id": user_id,
            "status": subscription["status"],
        }
        if optional_columns["stripe_customer_id"]:
            row["stripe_customer_id"] = subscription["stripe_customer_id"]
        if optional_columns["stripe_subscription_id"]:
            row["stripe_subscription_id"] = subscription["stripe_subscription_id"]
        if optional_columns["current_period_start"]:
            row["current_period_start"] = subscription["current_period_start"].isoformat()
        if optional_columns["current_period_end"]:
            row["current_period_end"] = subscription["current_period_end"].isoformat()
        if optional_columns["cancel_at_period_end"]:
            row["cancel_at_period_end"] = subscription["cancel_at_period_end"]
        if optional_columns["tier"]:
            row["tier"] = subscription.get("tier", "standard")
        timestamp = datetime.now(timezone.utc).isoformat()
        if optional_columns["created_at"]:
            row["created_at"] = timestamp
        if optional_columns["updated_at"]:
            row["updated_at"] = timestamp
        rows.append(row)
    if rows:
        rest_upsert(project_url, service_key, "subscriptions", rows)
        print(f"✔ Upserted {len(rows)} subscriptions.")
    else:
        print("⚠ No subscriptions to upsert.")


def main() -> int:
    try:
        load_env()
        supabase_url = get_env_var("SUPABASE_URL")
        service_key = get_env_var("SUPABASE_SERVICE_KEY")

        email_to_id = ensure_users(supabase_url, service_key, DEMO_USERS)
        upsert_profiles(supabase_url, service_key, DEMO_USERS, email_to_id)
        upsert_products(supabase_url, service_key)
        upsert_campaigns(supabase_url, service_key)
        upsert_subscriptions(supabase_url, service_key, email_to_id)

        print("✅ Demo data seeded successfully.")
        return 0
    except SeedError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())


