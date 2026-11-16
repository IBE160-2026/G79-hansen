"""Explicit, fail-closed authentication configuration. The demo needs none."""

import base64
import json
import os
from dataclasses import dataclass, field
from ipaddress import ip_address
from urllib.parse import urlsplit
from pathlib import Path
import re


@dataclass(frozen=True)
class Settings:
    auth_enabled: bool = False
    app_origin: str = ""
    supabase_url: str = ""
    supabase_key: str = field(default="", repr=False)
    allow_loopback_http: bool = False
    idle_seconds: int = 1800
    absolute_seconds: int = 43200
    model_enabled: bool = False
    openai_api_key: str = field(default="", repr=False)
    model_budget_path: str = ""
    save_enabled: bool = False
    save_backend_key_path: str = ""

    @classmethod
    def from_env(cls):
        def positive(name, default):
            try:
                value = int(os.environ.get(name, default))
                return value if 0 < value <= default else default
            except ValueError:
                return default
        return cls(
            auth_enabled=os.environ.get("AUTH_ENABLED") == "true",
            app_origin=os.environ.get("APP_ORIGIN", ""),
            supabase_url=os.environ.get("SUPABASE_URL", ""),
            supabase_key=os.environ.get("SUPABASE_PUBLISHABLE_KEY", ""),
            allow_loopback_http=os.environ.get("AUTH_ALLOW_LOOPBACK_HTTP") == "true",
            idle_seconds=positive("AUTH_IDLE_SECONDS", 1800),
            absolute_seconds=positive("AUTH_ABSOLUTE_SECONDS", 43200),
            model_enabled=os.environ.get("MODEL_ENABLED") == "true",
            openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
            model_budget_path=os.environ.get("MODEL_BUDGET_PATH", ""),
            save_enabled=os.environ.get("SAVE_ENABLED") == "true",
            save_backend_key_path=os.environ.get("SAVE_BACKEND_KEY_PATH", ""),
        )

    @property
    def available(self):
        if not self.auth_enabled:
            return False
        try:
            origin, provider = urlsplit(self.app_origin), urlsplit(self.supabase_url)
            for value in (origin, provider):
                if (not value.hostname or value.username or value.password or
                        value.path or value.query or value.fragment):
                    return False
                _ = value.port
            if provider.scheme != "https":
                return False
            if origin.scheme != "https":
                try:
                    loopback = ip_address(origin.hostname).is_loopback
                except ValueError:
                    loopback = origin.hostname == "localhost"
                if not (origin.scheme == "http" and self.allow_loopback_http and loopback):
                    return False
            # Publishable keys or legacy anon JWTs only. Never accept a secret/service key.
            key = self.supabase_key
            if key.startswith("sb_publishable_") and len(key) > len("sb_publishable_"):
                return self.idle_seconds > 0 and self.absolute_seconds > 0
            parts = key.split(".")
            if len(parts) != 3:
                return False
            claims = json.loads(base64.urlsafe_b64decode(parts[1] + "=" * (-len(parts[1]) % 4)))
            return isinstance(claims, dict) and claims.get("role") == "anon" and self.idle_seconds > 0 and self.absolute_seconds > 0
        except (ValueError, TypeError, UnicodeError):
            return False

    @property
    def secure_cookies(self):
        return self.app_origin.startswith("https://")

    @property
    def model_available(self):
        return bool(self.model_enabled and self.openai_api_key and self.model_budget_path)

    def save_backend_key(self):
        from app.adapters.documents import DocumentFailure
        try:
            if not self.save_enabled or not self.available:
                raise ValueError()
            path = Path(self.save_backend_key_path)
            if path.stat().st_size != 64:
                raise ValueError()
            value = path.read_text(encoding='ascii')
            if not re.fullmatch('[0-9a-f]{64}', value):
                raise ValueError()
            return value
        except (ValueError, OSError, UnicodeError):
            raise DocumentFailure('save_unavailable') from None
