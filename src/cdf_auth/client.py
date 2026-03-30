"""Build a :class:`~cognite.client.CogniteClient` from environment variables."""

from __future__ import annotations

import os
from pathlib import Path

from cognite.client import CogniteClient
from cognite.client.config import ClientConfig
from cognite.client.credentials import OAuthClientCredentials
from dotenv import load_dotenv

_REQUIRED = (
    "COGNITE_PROJECT",
    "COGNITE_TOKEN_URL",
    "COGNITE_CLIENT_ID",
    "COGNITE_CLIENT_SECRET",
)


def _parse_scopes(raw: str | None) -> list[str] | None:
    if raw is None or not raw.strip():
        return None
    parts: list[str] = []
    for token in raw.replace(",", " ").split():
        if token:
            parts.append(token)
    return parts or None


def _require(name: str) -> str:
    value = os.environ.get(name)
    if value is None or not str(value).strip():
        raise ValueError(f"Missing or empty environment variable: {name}")
    return value.strip()


def _find_dotenv_file() -> Path | None:
    """Locate a ``.env`` in the cwd or any parent (helps notebooks run from ``scripts/``)."""
    cwd = Path.cwd().resolve()
    for directory in (cwd, *cwd.parents):
        candidate = directory / ".env"
        if candidate.is_file():
            return candidate
    return None


def get_cognite_client(*, dotenv_path: str | Path | None = None) -> CogniteClient:
    """Load ``.env`` (if present), then return a sync Cognite client using OAuth2 client credentials.

    Required environment variables:
        ``COGNITE_PROJECT``, ``COGNITE_TOKEN_URL``, ``COGNITE_CLIENT_ID``,
        ``COGNITE_CLIENT_SECRET``.

    Host (one required):
        ``COGNITE_BASE_URL`` **or** ``COGNITE_CLUSTER`` (expands to
        ``https://<cluster>.cognitedata.com``).

    Optional:
        ``COGNITE_SCOPES`` (space- or comma-separated; passed to the token request),
        ``COGNITE_CLIENT_NAME`` (defaults to ``cdf-auth``).

    See the Cognite Python SDK docs for credential configuration:
    https://cognite-sdk-python.readthedocs-hosted.com/en/latest/
    """
    if dotenv_path is not None:
        load_dotenv(dotenv_path)
    else:
        env_file = _find_dotenv_file()
        if env_file is not None:
            load_dotenv(env_file)
        else:
            load_dotenv()

    missing = [k for k in _REQUIRED if not os.environ.get(k, "").strip()]
    if missing:
        raise ValueError("Missing required environment variables: " + ", ".join(missing))

    base_url = os.environ.get("COGNITE_BASE_URL", "").strip() or None
    cluster = os.environ.get("COGNITE_CLUSTER", "").strip() or None
    if not base_url and not cluster:
        raise ValueError("Set either COGNITE_BASE_URL or COGNITE_CLUSTER")

    credentials = OAuthClientCredentials(
        token_url=_require("COGNITE_TOKEN_URL"),
        client_id=_require("COGNITE_CLIENT_ID"),
        client_secret=_require("COGNITE_CLIENT_SECRET"),
        scopes=_parse_scopes(os.environ.get("COGNITE_SCOPES")),
    )

    client_name = os.environ.get("COGNITE_CLIENT_NAME", "").strip() or "cdf-auth"

    config = ClientConfig(
        client_name=client_name,
        project=_require("COGNITE_PROJECT"),
        credentials=credentials,
        base_url=base_url,
        cluster=cluster if not base_url else None,
    )
    return CogniteClient(config)
