# Brainqub3 Second Brain

A local-first, file-based second brain architecture powered by Claude Code. Turn Claude into your personalised knowledge agent for understanding customers, identifying opportunities, and surfacing next best actions by bringing your business data directly into Claude Code.

**Built by [Brainqub3](https://brainqub3.com/)** — AI engineering consultancy shipping production-grade agents and automations for SMEs.

---

## Getting Help

**Claude can help you with any setup or customisation in this repo.** Simply ask:

- "Help me configure the Google Calendar integration"
- "How do I connect a different CRM?"
- "Add a new data source for Slack messages"
- "Modify the CRM schema to include custom fields"

Claude has full context of this repository and can guide you through any changes.

---

## Quick Start

### 1. Clone and open in Claude Code

```bash
git clone <your-repo-url>
cd brainqub3
claude  # Opens Claude Code in this directory
```

### 2. Fill out your profile files

Before using the agent, populate these two files with your information:

| File | Purpose |
|------|---------|
| `ME.MD` | Your bio, expertise, communication preferences, operating principles |
| `BUSINESS.MD` | Your offerings, positioning, target audience, proof points |

These files give Claude the context it needs to provide personalised assistance.

### 3. Configure integrations (optional)

See [Integrations](#integrations) below for setting up Google Calendar, Zoho CRM, etc.

---

## Architecture Overview

```
brainqub3/
├── CLAUDE.MD           # Agent instructions and orchestration rules
├── ME.MD               # Personal context (edit this first)
├── BUSINESS.MD         # Business offerings (edit this first)
├── agents/             # Sub-agent prompts
├── raw/                # Immutable source data (append-only, never edit)
│   ├── calendars/      # Calendar exports
│   ├── crm/            # CRM database and exports
│   ├── gmail/          # Email data
│   ├── linkedin/       # LinkedIn exports
│   └── youtube/        # YouTube analytics
├── kb/                 # Knowledge base (agent-writable)
│   ├── customers/      # Customer profiles and insights
│   ├── insights/       # Patterns and observations
│   ├── playbooks/      # Repeatable processes
│   └── decisions/      # Key decisions with rationale
├── state/              # Machine state (caches, checkpoints)
├── scripts/            # Utility scripts and APIs
│   ├── ingest/         # Data ingestion scripts
│   └── crm/            # CRM database schema
└── .claude/            # Claude Code configuration
    ├── agents/         # Agent definitions
    └── skills/         # Skill definitions (rlm, kb-update)
```

### Key Concepts

| Layer | Read/Write | Purpose |
|-------|------------|---------|
| `raw/` | Read-only | Immutable source dumps. Never edit after ingestion. |
| `kb/` | Read/Write | Your curated knowledge base. Safe for Claude to update. |
| `state/` | Read/Write | Machine-managed state, caches, checkpoints. |
| `ME.MD` / `BUSINESS.MD` | Read/Write | Your personal and business context. |

---

## Key Files

### CLAUDE.MD

The main instruction file that tells Claude how to behave as your second brain agent. It defines:

- Data access policies (what to read, what to write)
- Query workflows and response formats
- Sub-agent orchestration rules
- Privacy and quality guardrails

### ME.MD

Your personal profile. Include:

- Bio and background
- Technical expertise
- Operating principles
- Communication preferences
- Current focus areas

### BUSINESS.MD

Your business context. Include:

- Company offerings (problem → outcome → who it's for)
- Positioning and differentiators
- Target audience
- Proof points and case studies

---

## Sub-agents

The system includes specialised sub-agents for different tasks:

| Agent | File | Purpose |
|-------|------|---------|
| External Research | `agents/external-research.md` | Web research for current events, competitors, pricing |
| Calendar Fetch | `agents/calendar-fetch.md` | Fetches Google Calendar events to `raw/calendars/` |
| CRM Lead Retriever | (built-in) | Syncs leads from Zoho CRM to the local SQLite database |
| RLM Subcall | `.claude/agents/rlm-subcall.md` | Extracts relevant info from large contexts |

---

## Skills

Skills are reusable workflows invoked with `/command` syntax:

| Skill | Command | Purpose |
|-------|---------|---------|
| RLM | `/rlm` | Long-context retrieval over local files (meetings, CRM, kb) |
| KB Update | `/kb-update` | Safely write and link knowledge to `kb/` |
| CRM Sync | `/crm-sync` | Sync leads from Zoho CRM into local SQLite |

---

## CRM Database

CRM data is stored in a SQLite database at `raw/crm/crm.db`. The schema (`scripts/crm/db_schema.sql`) includes:

| Table | Purpose |
|-------|---------|
| `leads` | Current state of all CRM leads |
| `leads_history` | Full audit trail of all changes (insert/update/delete) |
| `sync_log` | Metadata for each sync operation |

### Zoho CRM Integration

A Zoho CRM MCP server is already connected. To use it:

1. Configure your Zoho OAuth credentials
2. Use `/crm-sync` to pull leads into the local database
3. Query your leads naturally: "Show me all leads from last week"

### Customising the Schema

The current schema is designed for Zoho Leads. You may want to:

- Add custom fields specific to your CRM
- Change field names to match a different CRM provider
- Add new tables for other CRM objects (Contacts, Deals, etc.)

**Just ask Claude**: "Help me modify the CRM schema to add a 'deal_value' field"

---

## Integrations

### Google Calendar API

The repo includes a Google Calendar fetch script (`scripts/ingest/gcal_fetch.py`) for pulling calendar events.

#### Setup

1. Create OAuth credentials in Google Cloud Platform:
   - Go to [GCP Console](https://console.cloud.google.com/)
   - Create a new project (or use existing)
   - Enable the **Google Calendar API**
   - Create OAuth 2.0 credentials (Desktop app type)

2. Set environment variables in `scripts/.env`:

   ```bash
   GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-client-secret
   ```

3. Install dependencies and authenticate:

   ```bash
   pip install -r scripts/ingest/requirements.txt
   python scripts/ingest/gcal_fetch.py auth
   ```

4. Fetch events:

   ```bash
   python scripts/ingest/gcal_fetch.py fetch           # Next 7 days
   python scripts/ingest/gcal_fetch.py fetch --days 30 # Next 30 days
   ```

Events are saved to `raw/calendars/gcal/`.

### Building Custom Integrations

You can extend the system with your own APIs and data sources:

- Add ingestion scripts to `scripts/ingest/`
- Store raw data in `raw/<source-name>/`
- Ask Claude to help: "Create an integration to fetch Slack messages"

---

## Customisation

This repo is designed to be customised. Claude can help you:

- **Add new data sources**: Gmail, Notion, Jira, Slack, etc.
- **Change CRM providers**: HubSpot, Salesforce, Pipedrive, etc.
- **Create new sub-agents**: Specialised agents for your workflows
- **Modify the knowledge base structure**: Adapt `kb/` to your needs
- **Build automation scripts**: Data processing, reporting, alerts

**Just ask**: "Help me add a HubSpot integration" or "Create an agent for weekly reporting"

---

## What You Can Do With This

Once configured, you can ask Claude things like:

- "What did I discuss with Acme Corp in our last meeting?"
- "Show me all leads from Q4 who mentioned pricing concerns"
- "What are the common objections I'm hearing from prospects?"
- "Draft a follow-up email based on yesterday's call"
- "What should I prioritise this week based on my calendar and pipeline?"
- "Update my knowledge base with insights from today's meetings"

---

## Important Notes

### This is a Template

This repository is **not a production system**. It's a template and starting point for building your own personalised productivity agent. You should:

- Customise the schema for your specific needs
- Add integrations relevant to your workflow
- Extend the agents and skills as needed
- Treat it as a foundation to build upon

### Privacy

- All data stays local on your machine
- Raw data in `raw/` is treated as sensitive by default
- Claude won't include PII in responses unless explicitly requested

---

## Contributing

This project is maintained by [Brainqub3](https://brainqub3.com/).

For questions, customisation help, or to discuss building production AI agents for your business, visit [brainqub3.com](https://brainqub3.com/).

---

## Licence

See [LICENSE](LICENSE) for details.
