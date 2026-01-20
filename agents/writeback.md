# Writeback Agent (Brainqub3)

Goal: safely write and link knowledge to the kb/** directory.

## When to write
- User explicitly requests to store/update something
- Stable, reusable knowledge was discovered (customer insight, pattern, decision)
- A new customer or entity needs a graph node

## Where to write
- kb/customers/ - Customer knowledge graph nodes
- kb/people/ - Key people nodes
- kb/orgs/ - Organisation nodes
- kb/offers/ - Product and service pages
- kb/playbooks/ - Sales, delivery, follow-up templates
- kb/insights/ - Cross-meeting patterns, themes, retros
- kb/glossary.md - Terms, acronyms, positioning
- ME.MD - Personal preferences and principles
- BUSINESS.MD - Offerings and positioning

## Never write to
- raw/** (immutable)
- canon/** (regeneratable)

## Writing standards

### File naming
- Use lowercase with hyphens
- Include identifiers: `company-name__c-<customerid>.md`
- Date prefix where appropriate: `YYYY-MM-DD__description.md`

### Front matter
Always include YAML front matter with:
- id or relevant_id (customer_id, person_id, etc.)
- type (customer, person, org, insight, playbook)
- tags
- related links

### Linking
- Always link back to source documents
- Cross-link related kb/** entries
- Use relative paths from repo root

## Steps
1) Determine the correct location in kb/**
2) Check if an existing entry should be updated vs creating new
3) Write with proper YAML front matter
4) Update any related entries with cross-links
5) Report what was written and where
