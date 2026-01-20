#!/usr/bin/env python3
"""
Google Calendar Read-Only Fetch Utility

Fetches calendar events via OAuth 2.0 and saves raw JSON to raw/calendars/gcal/.

Usage:
    python gcal_fetch.py auth              # Run OAuth flow, save token
    python gcal_fetch.py fetch             # Fetch upcoming events (default 7 days)
    python gcal_fetch.py fetch --days 30   # Fetch next 30 days
    python gcal_fetch.py fetch --from 2026-01-01 --to 2026-01-31
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent / ".env")

# Read-only scope for calendar events
SCOPES = ["https://www.googleapis.com/auth/calendar.events.readonly"]

# Paths relative to repo root
REPO_ROOT = Path(__file__).parent.parent.parent
TOKEN_PATH = Path(__file__).parent / "token.json"
RAW_OUTPUT_DIR = REPO_ROOT / "raw" / "calendars" / "gcal"
CHECKPOINT_DIR = REPO_ROOT / "state" / "checkpoints"
CHECKPOINT_FILE = CHECKPOINT_DIR / "gcal_last_sync.json"


def get_client_config() -> dict:
    """Build OAuth client config from environment variables."""
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("Error: GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in .env")
        print("See scripts/.env.example for details.")
        sys.exit(1)

    return {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }


def authenticate() -> Credentials:
    """
    Run OAuth 2.0 authentication flow.

    If a valid token exists, load it. If expired, refresh it.
    Otherwise, run the full OAuth consent flow.
    """
    creds = None

    # Load existing token if present
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("Starting OAuth consent flow...")
            print("A browser window will open for authentication.")
            client_config = get_client_config()
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for next run
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())
        print(f"Token saved to {TOKEN_PATH}")

    return creds


def cmd_auth(args: argparse.Namespace) -> None:
    """Handle the 'auth' command - run OAuth flow and save token."""
    creds = authenticate()
    print("Authentication successful!")
    print(f"Token stored at: {TOKEN_PATH}")


def fetch_events(
    creds: Credentials,
    calendar_id: str = "primary",
    time_min: datetime = None,
    time_max: datetime = None,
) -> list:
    """
    Fetch calendar events within the specified time range.

    Args:
        creds: OAuth credentials
        calendar_id: Calendar ID (default: primary)
        time_min: Start of time range (default: now)
        time_max: End of time range (default: 7 days from now)

    Returns:
        List of event dictionaries
    """
    if time_min is None:
        time_min = datetime.now(timezone.utc)
    if time_max is None:
        time_max = time_min + timedelta(days=7)

    # Ensure timezone-aware datetimes in ISO format
    time_min_str = time_min.isoformat()
    time_max_str = time_max.isoformat()

    service = build("calendar", "v3", credentials=creds)

    all_events = []
    page_token = None

    while True:
        events_result = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=time_min_str,
                timeMax=time_max_str,
                singleEvents=True,
                orderBy="startTime",
                pageToken=page_token,
            )
            .execute()
        )

        events = events_result.get("items", [])
        all_events.extend(events)

        page_token = events_result.get("nextPageToken")
        if not page_token:
            break

    return all_events


def save_events(events: list, calendar_id: str) -> Path:
    """
    Save events to raw JSON file.

    Args:
        events: List of event dictionaries
        calendar_id: Calendar ID used for fetch

    Returns:
        Path to saved file
    """
    RAW_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc)
    date_str = timestamp.strftime("%Y-%m-%d")
    filename = f"{date_str}__gcal_events.json"
    output_path = RAW_OUTPUT_DIR / filename

    output_data = {
        "fetched_at": timestamp.isoformat(),
        "calendar_id": calendar_id,
        "event_count": len(events),
        "events": events,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    return output_path


def update_checkpoint(time_min: datetime, time_max: datetime, event_count: int) -> None:
    """Update the last sync checkpoint."""
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

    checkpoint_data = {
        "last_sync": datetime.now(timezone.utc).isoformat(),
        "time_range": {
            "from": time_min.isoformat(),
            "to": time_max.isoformat(),
        },
        "event_count": event_count,
    }

    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(checkpoint_data, f, indent=2)


def parse_date(date_str: str) -> datetime:
    """Parse a date string (YYYY-MM-DD) into a timezone-aware datetime."""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.replace(tzinfo=timezone.utc)


def cmd_fetch(args: argparse.Namespace) -> None:
    """Handle the 'fetch' command - fetch and save calendar events."""
    # Determine time range
    now = datetime.now(timezone.utc)

    if args.from_date and args.to_date:
        time_min = parse_date(args.from_date)
        time_max = parse_date(args.to_date) + timedelta(days=1)  # Include end date
    elif args.days:
        time_min = now
        time_max = now + timedelta(days=args.days)
    else:
        time_min = now
        time_max = now + timedelta(days=7)

    calendar_id = args.calendar or "primary"

    print(f"Fetching events from {time_min.date()} to {time_max.date()}...")
    print(f"Calendar: {calendar_id}")

    # Authenticate and fetch
    creds = authenticate()

    try:
        events = fetch_events(creds, calendar_id, time_min, time_max)
    except HttpError as e:
        print(f"Error fetching events: {e}")
        sys.exit(1)

    if not events:
        print("No events found in the specified time range.")
        return

    # Save to file
    output_path = save_events(events, calendar_id)
    print(f"Saved {len(events)} events to {output_path}")

    # Update checkpoint
    update_checkpoint(time_min, time_max, len(events))
    print(f"Checkpoint updated: {CHECKPOINT_FILE}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Google Calendar read-only fetch utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # auth command
    auth_parser = subparsers.add_parser("auth", help="Run OAuth flow and save token")
    auth_parser.set_defaults(func=cmd_auth)

    # fetch command
    fetch_parser = subparsers.add_parser("fetch", help="Fetch calendar events")
    fetch_parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to fetch (default: 7)",
    )
    fetch_parser.add_argument(
        "--from",
        dest="from_date",
        type=str,
        help="Start date (YYYY-MM-DD)",
    )
    fetch_parser.add_argument(
        "--to",
        dest="to_date",
        type=str,
        help="End date (YYYY-MM-DD)",
    )
    fetch_parser.add_argument(
        "--calendar",
        type=str,
        default="primary",
        help="Calendar ID (default: primary)",
    )
    fetch_parser.set_defaults(func=cmd_fetch)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
