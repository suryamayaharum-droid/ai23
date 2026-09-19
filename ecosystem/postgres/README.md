# HARUM BACKEND ABSTRACTION

The organism uses a tiered backend model.

- **Tier 0 — SQLite**: mandatory local availability, WAL, checkpoints.
- **Tier 1 — Generic PostgreSQL**: vendor-neutral shared durable state.
- **Tier 2 — Supabase/Neon adapters**: managed online services that add convenience, realtime, branching or serverless behavior.

The business logic lives above these providers.

## Why
A managed platform outage, quota, pricing change or plugin failure must not stop:
- local mission planning;
- event journaling;
- task checkpointing;
- archive indexing;
- deterministic CPU work.

## PostgreSQL contract
Portable SQL lives in `ecosystem/postgres/001_harum_portable_core.sql`.
Supabase-specific Broadcast/Edge behavior lives separately in `ecosystem/supabase/`.

This split is deliberate: a provider can be replaced without rewriting the organism.
