#!/usr/bin/env python3
"""
Helper script to mark a Supabase user as email-confirmed using the service role key.

Usage:
    ./scripts/verify_supabase_user.py user@example.com
    ./scripts/verify_supabase_user.py user@example.com --user-id=<uuid>

Environment variables required:
    SUPABASE_URL
    SUPABASE_SERVICE_KEY
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Dict

import requests
def _load_env_if_available() -> None:
    """Load environment variables from a local .env file if present."""

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


API_TIMEOUT = 10  # seconds


class SupabaseVerificationError(Exception):
    """Custom error for verification failures."""


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SupabaseVerificationError(f"Environment variable {name} is required.")
    return value


def _request(
    method: str,
    url: str,
    service_key: str,
    *,
    params: Dict[str, Any] | None = None,
    json: Dict[str, Any] | None = None,
) -> requests.Response:
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
    }
    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        params=params,
        json=json,
        timeout=API_TIMEOUT,
    )
    if not response.ok:
        raise SupabaseVerificationError(
            f"{method} {url} failed with status {response.status_code}: {response.text}"
        )
    return response


def _format_user_summary(user: Dict[str, Any]) -> str:
    confirmed_at = user.get("confirmed_at") or user.get("email_confirmed_at")
    return (
        f"- id={user.get('id')} created_at={user.get('created_at')} "
        f"confirmed_at={confirmed_at}"
    )


def find_user_id_by_email(
    project_url: str,
    service_key: str,
    email: str,
    preferred_user_id: str | None = None,
) -> str:
    endpoint = f"{project_url.rstrip('/')}/auth/v1/admin/users"
    response = _request("GET", endpoint, service_key, params={"email": email})
    payload = response.json()

    users = payload.get("users") or []
    if not users:
        raise SupabaseVerificationError(f"No Supabase user found for email {email!r}.")

    if preferred_user_id:
        for user in users:
            if user.get("id") == preferred_user_id:
                return preferred_user_id
        raise SupabaseVerificationError(
            f"User id {preferred_user_id!r} not found for email {email!r}.\n"
            + "\n".join(_format_user_summary(user) for user in users)
        )

    if len(users) > 1:
        summaries = "\n".join(_format_user_summary(user) for user in users)
        raise SupabaseVerificationError(
            f"Multiple users found for email {email!r}; "
            f"re-run with --user-id=<uuid> to disambiguate.\n{summaries}"
        )

    user = users[0]
    return user["id"]


def confirm_user_email(project_url: str, service_key: str, user_id: str) -> None:
    endpoint = f"{project_url.rstrip('/')}/auth/v1/admin/users/{user_id}"
    try:
        _request("PATCH", endpoint, service_key, json={"email_confirm": True})
    except SupabaseVerificationError as exc:
        message = str(exc)
        if "status 405" not in message:
            raise
        _request("PUT", endpoint, service_key, json={"email_confirm": True})


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Mark a Supabase user as email confirmed.")
    parser.add_argument("email", help="Email address of the Supabase user to verify")
    parser.add_argument(
        "--user-id",
        help="Specific Supabase user id to confirm when multiple accounts share the email",
    )
    args = parser.parse_args(argv)

    try:
        _load_env_if_available()
        supabase_url = _get_required_env("SUPABASE_URL")
        service_key = _get_required_env("SUPABASE_SERVICE_KEY")

        user_id = find_user_id_by_email(
            supabase_url,
            service_key,
            args.email,
            preferred_user_id=args.user_id,
        )
        confirm_user_email(supabase_url, service_key, user_id)
        print(f"Successfully confirmed email for user {args.email} (id={user_id}).")
        return 0
    except SupabaseVerificationError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))


