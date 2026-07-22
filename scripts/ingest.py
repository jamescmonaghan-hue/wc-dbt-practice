import requests            # library for making HTTP calls to the API
import os                  # lets us read environment variables (like our API key)
import json                # used to serialise API responses for storage
import duckdb               # our warehouse — a single local database file
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

# Anchor .env loading off this script's own location, not the working directory —
# works correctly regardless of where the script is run from
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
BASE_URL = "https://api.football-data.org/v4"
DB_PATH = Path(__file__).resolve().parent.parent / "warehouse.duckdb"


def fetch_matches() -> dict:
    """Call the football-data.org matches endpoint and return the raw JSON."""
    headers = {"X-Auth-Token": API_KEY}
    resp = requests.get(f"{BASE_URL}/competitions/WC/matches", headers=headers)
    resp.raise_for_status()
    return resp.json()


def land_raw_matches(payload: dict) -> None:
    """Store the raw matches JSON in DuckDB, stamped with a load time."""
    con = duckdb.connect(str(DB_PATH))
    con.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw.matches_raw (
            loaded_at TIMESTAMP,
            payload JSON
        );
    """)
    con.execute(
        "INSERT INTO raw.matches_raw VALUES (?, ?)",
        [datetime.now(timezone.utc), json.dumps(payload)],
    )
    con.close()


def fetch_standings() -> dict:
    """Call the football-data.org standings endpoint and return the raw JSON."""
    headers = {"X-Auth-Token": API_KEY}
    resp = requests.get(f"{BASE_URL}/competitions/WC/standings", headers=headers)
    resp.raise_for_status()
    return resp.json()


def land_raw_standings(payload: dict) -> None:
    """Store the raw standings JSON in its own dedicated table."""
    con = duckdb.connect(str(DB_PATH))
    con.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw.standings_raw (
            loaded_at TIMESTAMP,
            payload JSON
        );
    """)
    con.execute(
        "INSERT INTO raw.standings_raw VALUES (?, ?)",
        [datetime.now(timezone.utc), json.dumps(payload)],
    )
    con.close()


if __name__ == "__main__":
    matches_payload = fetch_matches()
    land_raw_matches(matches_payload)
    match_count = len(matches_payload.get("matches", []))
    print(f"Landed {match_count} matches at {datetime.now(timezone.utc)}")

    standings_payload = fetch_standings()
    land_raw_standings(standings_payload)
    group_count = len(standings_payload.get("standings", []))
    print(f"Landed {group_count} standings groups at {datetime.now(timezone.utc)}")