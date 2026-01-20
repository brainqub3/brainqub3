-- Brainqub3 CRM Database Schema
-- Location: raw/crm/crm.db
-- Owner: crm-lead-retriever agent (sole writer)

-- Enable foreign key support
PRAGMA foreign_keys = ON;

-- =============================================================================
-- leads: Current state of all CRM leads
-- =============================================================================
CREATE TABLE IF NOT EXISTS leads (
    id TEXT PRIMARY KEY,              -- Zoho record ID
    first_name TEXT,
    last_name TEXT,
    company TEXT,
    email TEXT,
    phone TEXT,
    lead_source TEXT,
    description TEXT,
    created_at TEXT NOT NULL,         -- When first synced locally (ISO 8601)
    updated_at TEXT NOT NULL,         -- Last sync time (ISO 8601)
    zoho_modified_time TEXT           -- Modified_Time from Zoho (ISO 8601)
);

-- =============================================================================
-- leads_history: Audit trail for all lead changes
-- =============================================================================
CREATE TABLE IF NOT EXISTS leads_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id TEXT NOT NULL,            -- FK to leads.id
    first_name TEXT,
    last_name TEXT,
    company TEXT,
    email TEXT,
    phone TEXT,
    lead_source TEXT,
    description TEXT,
    captured_at TEXT NOT NULL,        -- When this version was captured (ISO 8601)
    change_type TEXT NOT NULL,        -- 'insert', 'update', 'delete'
    FOREIGN KEY (lead_id) REFERENCES leads(id)
);

CREATE INDEX IF NOT EXISTS idx_history_lead_id ON leads_history(lead_id);
CREATE INDEX IF NOT EXISTS idx_history_captured_at ON leads_history(captured_at);

-- =============================================================================
-- sync_log: Metadata for each sync operation
-- =============================================================================
CREATE TABLE IF NOT EXISTS sync_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,         -- ISO 8601
    completed_at TEXT,                -- ISO 8601
    records_fetched INTEGER DEFAULT 0,
    records_inserted INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    status TEXT DEFAULT 'running',    -- 'running', 'success', 'failed'
    error_message TEXT
);

-- =============================================================================
-- Useful views
-- =============================================================================

-- View: Latest leads with full name
CREATE VIEW IF NOT EXISTS v_leads_summary AS
SELECT
    id,
    COALESCE(first_name, '') || ' ' || COALESCE(last_name, '') AS full_name,
    company,
    email,
    lead_source,
    updated_at
FROM leads
ORDER BY updated_at DESC;

-- View: Change history with readable timestamps
CREATE VIEW IF NOT EXISTS v_lead_changes AS
SELECT
    h.id,
    h.lead_id,
    COALESCE(h.first_name, '') || ' ' || COALESCE(h.last_name, '') AS full_name,
    h.company,
    h.change_type,
    h.captured_at
FROM leads_history h
ORDER BY h.captured_at DESC;
