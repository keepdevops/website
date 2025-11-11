#!/usr/bin/env python3
"""
Shared helpers and demo content for Supabase seeding scripts.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple
from uuid import NAMESPACE_URL, uuid5

import requests


API_TIMEOUT = 10  # seconds
DEMO_PASSWORD = "DemoPass123!"


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
            f"Admin API {method} {endpoint} failed with status "
            f"{response.status_code}: {response.text}"
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
    response = requests.get(
        endpoint, headers=headers, params={"select": "id", "limit": 1}, timeout=API_TIMEOUT
    )

    if response.ok:
        return True

    if response.status_code == 404 and "PGRST205" in response.text:
        return False

    raise SeedError(
        f"Unable to determine if table '{table}' exists: {response.status_code} {response.text}"
    )


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


def ensure_auth_user(
    project_url: str,
    service_key: str,
    email: str,
    password: str = DEMO_PASSWORD,
) -> Tuple[str, bool]:
    """Return auth user id for email, creating if necessary."""
    existing = admin_request("GET", project_url, service_key, params={"per_page": 200})
    for user in existing.json().get("users") or []:
        if user.get("email") == email:
            return user["id"], False

    payload = {"email": email, "password": password, "email_confirm": True}
    response = requests.post(
        f"{project_url.rstrip('/')}/auth/v1/admin/users",
        headers=supabase_headers(service_key),
        json=payload,
        timeout=API_TIMEOUT,
    )

    if response.ok:
        data = response.json()
        user = data.get("user", data)
        if not user or not user.get("id"):
            raise SeedError(f"Failed to parse created user response for {email}: {data}")
        return user["id"], True

    if response.status_code in (400, 422):
        retry = admin_request("GET", project_url, service_key, params={"per_page": 200})
        for user in retry.json().get("users") or []:
            if user.get("email") == email:
                return user["id"], False

    raise SeedError(
        f"Failed to create or find auth user for {email}: "
        f"{response.status_code} {response.text}"
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


def deterministic_uuid(name: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"demo:{name}"))


DEMO_PRODUCTS = [
    {
        "id": deterministic_uuid("product:redline"),
        "name": "Redline Container Acceleration Suite",
        "description": (
            "Bundle of CI/CD automations, security scans, and live dashboards "
            "for container delivery."
        ),
        "docker_image": "registry.example.com/redline/app:latest",
        "stripe_product_id": "prod_redline_demo",
        "active": True,
    },
    {
        "id": deterministic_uuid("product:bytecode"),
        "name": "Bytecode Analyzer",
        "description": (
            "Static analysis toolkit that surfaces dependency drift, CVEs, and "
            "upgrade insights."
        ),
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


