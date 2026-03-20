# base_sdk

Small utilities for working with the [Cognite Python SDK](https://cognite-sdk-python.readthedocs-hosted.com/en/latest/).

## cdf_auth package

Install in editable mode from the repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Configure environment variables (see `.env.example`), then use `from cdf_auth import get_cognite_client` in your scripts. See [`scripts/README.md`](scripts/README.md) for examples.
# cdf-sdk-support-tool
