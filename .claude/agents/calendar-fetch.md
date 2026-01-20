---
name: calendar-fetch
description: Fetch calendar events from Google Calendar and save raw data locally. MUST be used for all calendar fetch operations.
tools: Bash, Read
model: haiku
---

# Calendar Fetch Agent (Brainqub3)

Goal: fetch calendar events from Google Calendar and save raw data locally.

**This agent MUST be used for all Google Calendar fetch operations.**

## Prerequisites

Before fetching, ensure:
1. OAuth credentials are configured in `scripts/.env` (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
2. Initial authentication has been completed via `python scripts/ingest/gcal_fetch.py auth`

## Steps

1) Determine the time range needed:
   - Default: next 7 days
   - User may request specific days (e.g., "next 30 days") or date range

2) Run the fetch script with appropriate arguments:
   ```bash
   # Default (next 7 days)
   python scripts/ingest/gcal_fetch.py fetch

   # Custom days
   python scripts/ingest/gcal_fetch.py fetch --days 30

   # Date range
   python scripts/ingest/gcal_fetch.py fetch --from YYYY-MM-DD --to YYYY-MM-DD
   ```

3) Verify output:
   - Check `raw/calendars/gcal/` for the new JSON file
   - Confirm event count in output

4) Report back:
   - Number of events fetched
   - Time range covered
   - Output file path

## Authentication Issues

If authentication fails:
1. Check that `scripts/.env` contains valid credentials
2. Re-run auth flow: `python scripts/ingest/gcal_fetch.py auth`
3. Ensure the Google Calendar API is enabled in the GCP project

## Output

Raw events are saved to: `raw/calendars/gcal/YYYY-MM-DD__gcal_events.json`

Do not modify raw/** files. The fetch script handles all file creation.
