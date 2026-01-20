# Brainqub3 Second Brain

A local-first, file-based second brain architecture for personal and business knowledge management.

## Structure

```
brainqub3/
├── CLAUDE.MD          # Agent orchestration rules
├── ME.MD              # Personal context (agent-writable)
├── BUSINESS.MD        # Business offerings (agent-writable)
├── agents/            # Sub-agent prompts
├── raw/               # Immutable source data (append-only)
├── canon/             # Normalised documents for retrieval
├── kb/                # Knowledge base (agent-writable)
├── state/             # Machine-managed state
└── scripts/           # Utility scripts
```

## Layers

### raw/ (Read-only, append-only)
Immutable source dumps from Gmail, CRM, LinkedIn, YouTube, and Calendar. Never edited after ingestion.

### canon/ (Read-only, regeneratable)
Normalised Markdown documents with YAML front matter. Optimised for search and retrieval.

### kb/ (Read/Write)
The actual "second brain" - curated knowledge, customer graphs, insights, and playbooks. Safe for the agent to update.

## Naming conventions

- **Meetings**: `canon/meetings/YYYY/YYYY-MM-DD__client-name__call-type__m-<sourceid>.md`
- **Leads**: `canon/leads/YYYY/YYYY-MM-DD__crm__lead-name__l-<leadid>.md`
- **Customers**: `canon/customers/company-name__c-<customerid>.md`
- **KB nodes**: `kb/customers/company-name__c-<customerid>.md`

## Document format

All documents in canon/ and kb/ use Markdown with YAML front matter for searchability and linking.

## RLM Scopes

Retrieval scopes are defined in `state/rlm-scopes.yaml` and map to folder paths for targeted searches.
