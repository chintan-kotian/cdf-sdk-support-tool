"""Upload ~500 MB of dummy data into CDF RAW using the Python SDK.

Generates exactly MAX_ROWS rows, each sized large enough that the total
payload reaches TARGET_MB. With defaults: 3 000 rows × ~174 KB each ≈ 500 MB.

Set the following environment variables (same as other scripts in this repo):
- COGNITE_PROJECT
- COGNITE_TOKEN_URL
- COGNITE_CLIENT_ID
- COGNITE_CLIENT_SECRET
- COGNITE_BASE_URL  or  COGNITE_CLUSTER
- Optionally: COGNITE_SCOPES, COGNITE_CLIENT_NAME

Configuration (override via env vars):
- RAW_DATABASE   — target RAW database name      (default: chintan_dummy_db)
- RAW_TABLE      — target RAW table name         (default: dummy_table)
- TARGET_MB      — total payload in MB           (default: 500)
- MAX_ROWS       — exact number of rows to write (default: 3000)
- BATCH_SIZE     — rows per upsert call          (default: 100)

Usage:
    python scripts/upload_dummy.py
"""

from __future__ import annotations

import math
import os
import random
import string
import time
from typing import Any

from cdf_auth import get_cognite_client
from cognite.client.data_classes import Row

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
RAW_DATABASE = os.environ.get("RAW_DATABASE", "chintan_dummy_db")
RAW_TABLE    = os.environ.get("RAW_TABLE",    "dummy_table")
TARGET_MB    = float(os.environ.get("TARGET_MB",  "500"))
MAX_ROWS     = int(os.environ.get("MAX_ROWS",   "3000"))
BATCH_SIZE   = int(os.environ.get("BATCH_SIZE", "100"))

TARGET_BYTES    = int(TARGET_MB * 1024 * 1024)
BYTES_PER_ROW   = math.ceil(TARGET_BYTES / MAX_ROWS)

# Fixed overhead per row (key + numeric columns + JSON punctuation) ≈ 120 bytes.
# The two large string columns absorb the rest.
_FIXED_OVERHEAD  = 120
_STRING_BUDGET   = max(BYTES_PER_ROW - _FIXED_OVERHEAD, 1)

# Split the string budget: 40 % col_description, 60 % col_notes.
_DESC_LEN  = int(_STRING_BUDGET * 0.40)
_NOTES_LEN = _STRING_BUDGET - _DESC_LEN

_STATUSES   = ["active", "inactive", "pending", "archived", "unknown"]
_CATEGORIES = ["alpha", "beta", "gamma", "delta", "epsilon"]
_TAGS       = ["tag_" + c for c in string.ascii_lowercase[:10]]

_ALPHABET = string.ascii_letters + string.digits + " "


def _random_str(length: int) -> str:
    return "".join(random.choices(_ALPHABET, k=length))


def _make_row(index: int) -> tuple[str, dict[str, Any]]:
    """Return (key, columns) for a single large dummy row (10 columns)."""
    key = f"row_{index:010d}"
    columns: dict[str, Any] = {
        "col_id":          index,
        "col_name":        _random_str(50),
        "col_description": _random_str(_DESC_LEN),
        "col_category":    random.choice(_CATEGORIES),
        "col_value_a":     round(random.uniform(-1e6, 1e6), 6),
        "col_value_b":     round(random.uniform(0, 1), 8),
        "col_count":       random.randint(0, 1_000_000),
        "col_tag":         random.choice(_TAGS),
        "col_status":      random.choice(_STATUSES),
        "col_notes":       _random_str(_NOTES_LEN),
    }
    return key, columns


def main() -> None:
    client = get_cognite_client()

    try:
        client.raw.databases.create(RAW_DATABASE)
        print(f"Created database: {RAW_DATABASE}")
    except Exception:
        print(f"Database already exists (or creation skipped): {RAW_DATABASE}")

    try:
        client.raw.tables.create(RAW_DATABASE, RAW_TABLE)
        print(f"Created table: {RAW_TABLE}")
    except Exception:
        print(f"Table already exists (or creation skipped): {RAW_TABLE}")

    approx_mb = (BYTES_PER_ROW * MAX_ROWS) / (1024 * 1024)
    print(f"\nTarget : {TARGET_MB:.0f} MB over {MAX_ROWS:,} rows "
          f"(~{BYTES_PER_ROW / 1024:.1f} KB / row → ~{approx_mb:.0f} MB total)")
    print(f"Batch  : {BATCH_SIZE} rows/call")
    print(f"Writing: {RAW_DATABASE}.{RAW_TABLE}\n")

    total_rows  = 0
    batch_count = 0
    start_time  = time.time()

    while total_rows < MAX_ROWS:
        rows_left = MAX_ROWS - total_rows
        this_batch_size = min(BATCH_SIZE, rows_left)

        batch: list[Row] = [
            Row(key=k, columns=c, last_updated_time=0)
            for k, c in (_make_row(total_rows + i) for i in range(this_batch_size))
        ]

        client.raw.rows.insert(RAW_DATABASE, RAW_TABLE, batch, ensure_parent=False)

        total_rows  += this_batch_size
        batch_count += 1
        elapsed      = time.time() - start_time
        mb_done      = (BYTES_PER_ROW * total_rows) / (1024 * 1024)
        print(
            f"  Batch {batch_count:>4d} | rows: {total_rows:>6,} / {MAX_ROWS:,} | "
            f"~{mb_done:>7.1f} / {TARGET_MB:.0f} MB | {elapsed:.1f}s",
            flush=True,
        )

    elapsed = time.time() - start_time
    print(f"\nDone. {total_rows:,} rows in {batch_count} batches "
          f"(~{approx_mb:.0f} MB estimated, {elapsed:.1f}s).")


if __name__ == "__main__":
    main()
