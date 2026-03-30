"""Minimal script: obtain a client via cdf_auth and run a read-only SDK call."""

from cdf_auth import get_cognite_client


def main() -> None:
    client = get_cognite_client()
    result = client.time_series.list(limit=1)
    print(f"Retrieved {len(result)} time series (limit=1).")


if __name__ == "__main__":
    main()
