"""Read (sync) data modeling nodes via Instances Sync API.

Uses ``client.data_modeling.instances.sync`` with a :class:`~cognite.client.data_classes.data_modeling.query.QuerySync`.
See: https://cognite-sdk-python.readthedocs-hosted.com/en/latest/ (Data Modeling > Instances > Sync instances).

Set in ``.env`` (in addition to Cognite auth vars):

- ``DM_SYNC_VIEW_SPACE`` — space of the view
- ``DM_SYNC_VIEW_EXTERNAL_ID`` — view external id
- ``DM_SYNC_VIEW_VERSION`` — view version (e.g. ``v1``)

Optional:

- ``DM_SYNC_LIMIT`` (default ``100``) — max nodes per sync chunk
- ``DM_SYNC_PROPERTIES`` — comma-separated property names to return; if unset, ``["*"]`` (all properties). The API rejects null ``properties`` on ``SourceSelector``.

If you get **``One or more views do not exist``** on the ``hasData`` filter, the view triple
is wrong for this project (wrong space, external id, or version — e.g. ``v12`` vs ``v13``).
Run ``python scripts/list_dm_views.py <space>`` to list views and copy a valid triple into ``.env``.
"""

from __future__ import annotations

import os
import json
from cdf_auth import get_cognite_client
from cognite.client.data_classes.data_modeling.ids import ViewId
from cognite.client.data_classes.data_modeling.query import (
    NodeResultSetExpressionSync,
    QuerySync,
    SelectSync,
    SourceSelector,
)
from cognite.client.data_classes.filters import HasData

from cognite.client.data_classes.data_modeling.debug import DebugParameters

def _require_sync_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ValueError(f"Set {name} in .env for node sync (see scripts/sync_nodes.py docstring).")
    return value


def build_node_sync_query(
    view_id: ViewId,
    *,
    limit: int = 100,
    properties: list[str] | None = None,
) -> QuerySync:
    """Build a minimal sync query: nodes that have data in ``view_id``.

    The Instances API requires ``SourceSelector.properties`` to be a non-null list.
    Use ``["*"]`` to request all properties (see SDK docs on ``SourceSelector``).
    """
    # Treat None and [] as "all properties" (empty env / comma-only DM_SYNC_PROPERTIES).
    props = list(properties) if properties else ["*"]
    return QuerySync(
        with_={
            "nodes": NodeResultSetExpressionSync(
                filter=HasData(views=[view_id]),
                limit=limit,
            ),
        },
        select={
            "nodes": SelectSync(sources=[SourceSelector(view_id, props)]),
        },
    )


def main() -> None:
    client = get_cognite_client()

    view_id = ViewId(
    space= "shashanDataModel",
    external_id="Movie" ,
    version="1",
    )
    limit = int(os.environ.get("DM_SYNC_LIMIT", "100") or "100")
    props_raw = os.environ.get("DM_SYNC_PROPERTIES", "").strip()
    sync_properties = (
        [p.strip() for p in props_raw.split(",") if p.strip()] if props_raw else None
    )

    query = build_node_sync_query(view_id, limit=limit, properties=sync_properties)
    result = client.data_modeling.instances.sync(query)

    nodes = result["nodes"]
    print(f"First sync: {len(nodes)} node(s), cursor={nodes.cursor!r}")

    # Incremental: merge cursors (omit None) so the next sync returns changes since last cursor.
    merged = dict(query.cursors)
    for key, cur in result.cursors.items():
        if cur is not None:
            merged[key] = cur
    query.cursors = merged
    result_next = client.data_modeling.instances.sync(query, debug=DebugParameters(emit_results=False, include_translated_query=True, include_plan=True, profile=True))
    print(type(result_next.debug))
    with open("query_result.json", "w") as f:    
        json.dump(result_next.debug.dump() , f)
    # nodes_next = result_next["nodes"]
    # print(f"Second sync: {len(nodes_next)} node(s), cursor={nodes_next.cursor!r}")


if __name__ == "__main__":
    main()
