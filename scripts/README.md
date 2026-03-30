# Scripts

These examples import the **`cdf_auth`** package. Install it once from the **repository root** (not from `scripts/`):

```bash
cd /path/to/base_sdk
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
# optional: pandas for notebook HTML tables (`cdf_auth` extras)
pip install -e ".[pandas]"
```

Copy `.env.example` to `.env` in the repo root and set:

- `COGNITE_PROJECT`, `COGNITE_TOKEN_URL`, `COGNITE_CLIENT_ID`, `COGNITE_CLIENT_SECRET`
- Either `COGNITE_BASE_URL` or `COGNITE_CLUSTER`
- `COGNITE_SCOPES` as required by your identity provider (often `https://<cluster>.cognitedata.com/.default` for Azure AD)

Run a sample script (from repo root with venv active):

```bash
python scripts/example_sdk_call.py
```

### Data modeling: sync (read) nodes

[`sync_nodes.py`](sync_nodes.py) and [`sync_nodes.ipynb`](sync_nodes.ipynb) call `client.data_modeling.instances.sync` with a `QuerySync` over a view you choose. Add to `.env`:

- `DM_SYNC_VIEW_SPACE`, `DM_SYNC_VIEW_EXTERNAL_ID`, `DM_SYNC_VIEW_VERSION`
- Optional: `DM_SYNC_LIMIT` (default `100`)
- Optional: `DM_SYNC_PROPERTIES` — comma-separated view properties; if omitted, the script uses `["*"]` (all). The API requires non-null `properties` on each `SourceSelector`.

```bash
python scripts/sync_nodes.py
```

If the API returns **`One or more views do not exist`** (e.g. `space:ViewExternalId/v13` in the `hasData` filter), the `HasData` filter is using a view that is not in **this** CDF project. List views in the space and pick a real `external_id` + `version`:

```bash
python scripts/list_dm_views.py cdf_apm
python scripts/list_dm_views.py cdf_apm --contains ApmAppData
```

Then set `DM_SYNC_VIEW_SPACE`, `DM_SYNC_VIEW_EXTERNAL_ID`, and `DM_SYNC_VIEW_VERSION` to match a printed row.

In Jupyter, use `print(...)` for diagnostics instead of leaving `len(nodes), nodes.cursor` as the last expression; some environments raise `TypeError: cannot create weak reference to 'NoneType' object` when displaying tuples that include `None`. Prefer `pip install -e ".[pandas]"` for stable table rendering.

Add more scripts the same way: `from cdf_auth import get_cognite_client`, then use the [Cognite Python SDK](https://cognite-sdk-python.readthedocs-hosted.com/en/latest/) APIs on the returned client.
