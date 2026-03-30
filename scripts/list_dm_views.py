"""List data modeling views in a space so you can fix ``DM_SYNC_VIEW_*`` for ``sync_nodes``.

If sync fails with ``One or more views do not exist`` on a ``hasData`` filter, the
``space`` / ``external_id`` / ``version`` triple does not match this CDF project.

Usage (repo root, venv, ``pip install -e .``):

    python scripts/list_dm_views.py cdf_apm

Or set ``DM_LIST_VIEWS_SPACE`` (or reuse ``DM_SYNC_VIEW_SPACE``) and run with no args.

SDK: https://cognite-sdk-python.readthedocs-hosted.com/en/latest/
"""

from __future__ import annotations

import argparse
import os
import sys

from cdf_auth import get_cognite_client


def main() -> None:
    parser = argparse.ArgumentParser(description="List views in a data modeling space.")
    parser.add_argument(
        "space",
        nargs="?",
        default=(
            os.environ.get("DM_LIST_VIEWS_SPACE", "").strip()
            or os.environ.get("DM_SYNC_VIEW_SPACE", "").strip()
            or None
        ),
        help="Space external id (e.g. cdf_apm). Defaults to DM_LIST_VIEWS_SPACE or DM_SYNC_VIEW_SPACE.",
    )
    parser.add_argument(
        "--contains",
        metavar="SUBSTR",
        default="",
        help="Only print views whose external_id contains this substring (case-sensitive).",
    )
    args = parser.parse_args()
    if not args.space:
        sys.exit("Pass SPACE as an argument or set DM_LIST_VIEWS_SPACE / DM_SYNC_VIEW_SPACE in .env")

    client = get_cognite_client()
    views = client.data_modeling.views.list(
        space=args.space,
        limit=None,
        all_versions=True,
    )

    rows: list[tuple[str, str, str, str]] = []
    for v in views:
        if args.contains and args.contains not in v.external_id:
            continue
        name = (v.name or "").replace("\t", " ")
        rows.append((v.space, v.external_id, v.version, name))

    rows.sort(key=lambda r: (r[1], r[2]))
    print(f"space={args.space!r}  count={len(rows)}  (all_versions=True)\n")
    print("view_ref (for docs)\texternal_id\tversion\tname")
    for space, xid, ver, name in rows:
        print(f"{space}:{xid}/{ver}\t{xid}\t{ver}\t{name}")


if __name__ == "__main__":
    main()
