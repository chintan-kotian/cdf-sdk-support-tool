"""Upload a file to Cognite Data Fusion (CDF) using the Python SDK.

This script demonstrates how to upload a file to CDF. Set the following environment variables:
- COGNITE_PROJECT
- COGNITE_TOKEN_URL
- COGNITE_CLIENT_ID
- COGNITE_CLIENT_SECRET
- Optionally: COGNITE_SCOPES

Usage:
    python scripts/upload_files.py <file_path> [external_id] [name]

Arguments:
- file_path: Path to the file to upload
- external_id: Optional external ID for the file (defaults to filename)
- name: Optional name for the file (defaults to filename)
"""

import sys
import os
from pathlib import Path
from cdf_auth import get_cognite_client
from cognite.client.data_classes.data_modeling.cdm.v1 import CogniteFileApply, CogniteAssetApply
from cognite.client.data_classes.data_modeling import NodeId


def upload_file(file_path: str, external_id: str | None = None, name: str | None = None) -> None:
    """Upload a file to CDF."""
    client = get_cognite_client()

    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Default external_id and name to filename if not provided
    if external_id is None:
        external_id = file_path_obj.stem
    if name is None:
        name = file_path_obj.name

    # Upload the file
    # file_metadata = client.files.upload(
    #     path=file_path,
    #     external_id=external_id,
    #     name=name,
    #     # Add other optional parameters as needed, e.g.:
    #     # metadata={"key": "value"},
    #     # data_set_id=123,
    #     # source="script",
    # )

    client.data_modeling.instances.apply(
    CogniteFileApply(
        space="Shashan",
        name="diagram_parsing_chintan",
        external_id="chintan-diagram-parsing-file-1",
        mime_type="application/pdf"  # Required for diagram parsing
    )
    )


    file_metadata = client.files.upload_content(
        path=file_path,
        instance_id=NodeId("Shashan", "chintan-diagram-parsing-file-1")
    )


    print(f"File uploaded successfully!")
    print(f"ID: {file_metadata.id}")
    print(f"External ID: {file_metadata.external_id}")
    print(f"Name: {file_metadata.name}")
    print(f"Uploaded at: {file_metadata.uploaded_time}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/upload_files.py <file_path> [external_id] [name]")
        sys.exit(1)

    file_path = sys.argv[1]
    external_id = sys.argv[2] if len(sys.argv) > 2 else None
    name = sys.argv[3] if len(sys.argv) > 3 else None

    upload_file(file_path, external_id, name)


if __name__ == "__main__":
    main()
    # client = get_cognite_client()

    # root = CogniteAssetApply(
    # space="Shashan",
    # external_id="chintan-v-1305",
    # name="V-1305",
    # )

    # # child = CogniteAssetApply(
    # # space="your_space",
    # # external_id="ChildAsset",
    # # name="Child Asset",
    # # parent=DirectRelationReference("your_space", "RootAsset"),
    # # )
    # client.data_modeling.instances.apply([root])