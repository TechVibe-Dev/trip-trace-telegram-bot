"""Runtime configuration, read from the environment and validated at startup."""

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")
DEFAULT_API_URL = "https://trip-trace-api.onrender.com"


class ConfigError(ValueError):
    """Raised when a required variable is missing or has an invalid value."""


@dataclass(frozen=True)
class Config:
    telegram_bot_token: str
    # Only these Telegram users get answers; everyone else is ignored.
    allowed_user_ids: frozenset[int]
    api_url: str
    api_username: str
    api_password: str
    api_timeout_seconds: float
    log_level: str


def load_env_file(env: Mapping[str, str] = os.environ) -> None:
    """Loads `.env`, or `.env.prod` when APP_ENV=prod. Variables already set win."""
    name = ".env.prod" if env.get("APP_ENV", "").lower() == "prod" else ".env"
    if Path(name).exists():
        load_dotenv(name, override=False)


def _required(env: Mapping[str, str], name: str) -> str:
    value = env.get(name, "").strip()
    if not value:
        raise ConfigError(f"{name} is not set. Copy .env.default to .env and fill it in.")
    return value


def _user_ids(raw: str) -> frozenset[int]:
    ids = set()
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        if not item.lstrip("-").isdigit():
            raise ConfigError(f"ALLOWED_TELEGRAM_USER_IDS must be numeric ids, got {item!r}")
        ids.add(int(item))
    if not ids:
        raise ConfigError("ALLOWED_TELEGRAM_USER_IDS needs at least one Telegram user id.")
    return frozenset(ids)


def load_config(env: Mapping[str, str] = os.environ) -> Config:
    log_level = env.get("LOG_LEVEL", "").strip().upper() or "INFO"
    if log_level not in LOG_LEVELS:
        raise ConfigError(f"LOG_LEVEL must be one of {', '.join(LOG_LEVELS)}, got {log_level!r}")

    raw_timeout = env.get("API_TIMEOUT_SECONDS", "").strip() or "30"
    try:
        timeout = float(raw_timeout)
    except ValueError:
        timeout = 0.0
    if timeout <= 0:
        raise ConfigError(f"API_TIMEOUT_SECONDS must be a positive number, got {raw_timeout!r}")

    return Config(
        telegram_bot_token=_required(env, "TELEGRAM_BOT_TOKEN"),
        allowed_user_ids=_user_ids(_required(env, "ALLOWED_TELEGRAM_USER_IDS")),
        api_url=(env.get("API_URL", "").strip() or DEFAULT_API_URL).rstrip("/"),
        api_username=_required(env, "API_USERNAME"),
        api_password=_required(env, "API_PASSWORD"),
        api_timeout_seconds=timeout,
        log_level=log_level,
    )
