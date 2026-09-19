# Neon Portability Validation — 2026-09-19

Status: **PASSED ON TEMPORARY BRANCH**

The HARUM portable PostgreSQL core was validated on Neon PostgreSQL 17 without modifying the production branch.

## Verified
- schema creation;
- 6 HARUM tables;
- 12 indexes;
- heartbeat/upsert;
- JSONB/vector-clock state;
- capability arrays;
- durable task insertion;
- atomic capability-aware task lease;
- lease expiry reconciliation;
- idempotent event insertion;
- PostgreSQL notification trigger.

## Behavioral test
A temporary worker:
1. registered heartbeat;
2. claimed a compatible task;
3. received a timed lease;
4. simulated lease expiry;
5. reconciler returned the task to READY;
6. emitted an idempotent organism event.

## Architecture result
The durable state contract is now proven portable across:
- SQLite local core;
- generic PostgreSQL;
- Neon PostgreSQL;
- Supabase-compatible PostgreSQL design.

Supabase remains useful for Realtime Broadcast and Edge Functions, but basic organism correctness no longer depends on Supabase.

## Production state
No Neon production schema was changed. Promotion from the temporary migration branch remains behind Neon's explicit migration-approval gate.
