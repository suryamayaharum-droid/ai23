# OPTIONAL EDGE RUNTIMES

These adapters are deliberately optional. The HARUM core must continue without them.

## Cloudflare candidate

Current official docs describe Workers Free, SQLite-backed Durable Objects on the Free plan, and Cloudflare Workflows with durable steps/retries. This makes it a strong candidate for a lightweight online coordinator.

Do not hard-code account IDs or tokens. Deployment should receive all secrets from the platform environment.

Recommended role:
- HTTP ingress for worker heartbeats;
- small SQLite-backed state projection;
- WebSocket/event relay;
- durable workflow for long waits;
- never store large media here.

## Vercel candidate

Use as:
- status/control API;
- dashboard;
- observability;
- lightweight request-driven orchestration.

Do not make it the only state store.

## Core rule

The edge runtime is an adapter. Git + journal + blackboard remain sufficient to reconstruct the organism.
