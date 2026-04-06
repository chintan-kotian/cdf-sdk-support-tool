# cdf-sdk-support-tool

Small utilities for working with the [Cognite Python SDK](https://cognite-sdk-python.readthedocs-hosted.com/en/latest/).

## Installation

### Using Poetry

1. Ensure you have Poetry installed: `pip install poetry`
2. Clone the repository and navigate to the project directory.
3. Install dependencies using Poetry:

```bash
poetry install
```

This will create a virtual environment and install all required dependencies.

### Using pip (Alternative)

If you prefer using pip:

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

## Usage

### cdf_auth package

The `cdf_auth` package provides utilities for authenticating with Cognite Data Fusion (CDF) using OAuth2 client credentials.

#### Environment Variables

Configure the following environment variables in a `.env` file or your environment:

- `COGNITE_PROJECT`: Your CDF project name
- `COGNITE_TOKEN_URL`: OAuth2 token URL (e.g., `https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/token`)
- `COGNITE_CLIENT_ID`: OAuth2 client ID
- `COGNITE_CLIENT_SECRET`: OAuth2 client secret
- `COGNITE_SCOPES` (optional): Comma-separated list of scopes

#### Using client.py

Import and use the `get_cognite_client` function to obtain a Cognite client:

```python
from cdf_auth import get_cognite_client

# Load environment variables from .env file if present
client = get_cognite_client()

# Now you can use the client for CDF operations
# Example: List assets
assets = client.assets.list(limit=10)
for asset in assets:
    print(asset.name)
```

The `get_cognite_client` function automatically loads environment variables from a `.env` file if found in the current directory or parent directories.

## Scripts

See [`scripts/README.md`](scripts/README.md) for example scripts using this package.
