# HARUM SUPABASE ORGANISM CORE

Supabase is an optional online nervous/circulatory layer for HARUM. The architecture must continue to work without it.

## What it adds
- transactional shared state;
- append-only event log;
- capability-aware durable task queue;
- atomic leases using `FOR UPDATE SKIP LOCKED`;
- heartbeat registry;
- snapshots and dead letters;
- private Realtime Broadcast from event inserts;
- optional Edge Function gateway.

## Deployment state
The Supabase connector is authenticated, but currently reports **no accessible projects**. Therefore this module is staged in GitHub and not yet deployed to a live database.

## Apply later
1. create or expose a Supabase project;
2. apply `migrations/001_harum_organism_core.sql`;
3. review Security + Performance Advisors;
4. design authenticated private Realtime policies;
5. deploy `functions/harum-organism/index.ts`;
6. store `HARUM_ORGANISM_SECRET` only in the Supabase function environment;
7. connect GitHub/portable workers through environment variables.

No secret belongs in Git, Airtable, the organism event log or task payloads.
