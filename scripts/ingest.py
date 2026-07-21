# scripts/ingest.py

import requests   # library for making HTTP calls to the API
import os          # lets us read environment variables (like our API key)
import json        # used to serialise the API response for storage
import duckdb       # our warehouse — a single local database file
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

# Anchor .env loading off this script's own file location (not the current
# working directory) — this makes it reliable regardless of which folder
# you happen to run the script from.
# __file__ = this script's own path; .parent twice = step up to project root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
BASE_URL = "https://api.football-data.org/v4"

# Path to the DuckDB warehouse file, also anchored to the project root
DB_PATH = Path(__file__).resolve().parent.parent / "warehouse.duckdb"


def fetch_matches() -> dict:
    """
    Call the football-data.org API and return the raw JSON response.

    Arguments: none — API_KEY and BASE_URL are read from the module-level
    constants defined above, rather than being passed in, since this script
    only ever calls one endpoint.

    Returns:
        dict — the full parsed JSON response from the API, exactly as
        received (a dictionary containing a "matches" key, among others).

    Raises:
        requests.HTTPError — if the API call fails (e.g. bad key, rate
        limited, endpoint down). This comes from resp.raise_for_status()
        below; we deliberately don't catch it here, so a failure stops the
        script loudly rather than silently continuing with no data.
    """
    headers = {"X-Auth-Token": API_KEY}
    resp = requests.get(f"{BASE_URL}/competitions/WC/matches", headers=headers)
    resp.raise_for_status()  # raises an exception here if the request failed
    return resp.json()       # parses the response body from JSON text to a dict


def land_raw_json(payload: dict) -> None:
    """
    Store the raw, unflattened JSON payload in DuckDB, stamped with the
    time it was loaded.

    Arguments:
        payload (dict) — the full API response dict, as returned by
        fetch_matches(). This function doesn't inspect or flatten it at
        all — it just serialises the whole thing back to a JSON string
        and stores it as-is.

    Returns:
        None — this function's job is a side effect (writing to the
        database), not producing a value to use afterwards.

    Why store it unflattened:
        Keeping the raw JSON exactly as the API returned it means we have
        an auditable, replayable copy. If we later find a bug in how we
        flatten it in dbt, we can fix the SQL and reprocess — without
        needing to call the API again.
    """
    con = duckdb.connect(str(DB_PATH))  # opens (or creates) the warehouse file

    # Keep raw data in its own schema, separate from anything dbt builds later
    con.execute("CREATE SCHEMA IF NOT EXISTS raw;")

    # Table has just two columns: when it was loaded, and the payload itself.
    # IF NOT EXISTS means this only creates the table the very first time —
    # subsequent runs just insert another row into the existing table.
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw.matches_raw (
            loaded_at TIMESTAMP,
            payload JSON
        );
    """)

    # Insert one row: current UTC timestamp, plus the payload serialised
    # back into a JSON string (DuckDB's JSON column type expects text).
    # The ? placeholders are parameterised — this avoids ever building SQL
    # by string-concatenating values directly into the query.
    con.execute(
        "INSERT INTO raw.matches_raw VALUES (?, ?)",
        [datetime.now(timezone.utc), json.dumps(payload)],
    )
    con.close()  # always close the connection when done


# This block only runs when the script is executed directly
# (e.g. `python scripts/ingest.py`), not if it were ever imported
# as a module from somewhere else — a standard Python convention.
if __name__ == "__main__":
    payload = fetch_matches()
    land_raw_json(payload)

    # .get(..., []) avoids an error if "matches" happens to be missing —
    # defaults to an empty list instead of raising a KeyError
    match_count = len(payload.get("matches", []))
    print(f"Landed {match_count} matches at {datetime.now(timezone.utc)}")