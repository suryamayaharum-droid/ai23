# HARUM INDEPENDENCE LAYER v1

Goal: keep the organism functional when any single provider, quota, model or connector is unavailable.

## Rules
- A provider is an adapter, never the architecture.
- Every critical capability has a degraded fallback.
- State is reconstructible from journal + Git snapshot + Airtable blackboard.
- External calls are idempotent and checkpointed.
- Resource exhaustion produces WAITING_RESOURCE, not fake completion.
- No quota bypass, account pooling or hidden credential propagation.
- Compute scales through bounded fan-out; permanent capacity is only counted when physically available.
- New runtimes announce capabilities and limits before receiving work.

## Failure ladder
1. retry transient failure with bounded exponential backoff;
2. circuit-break the failing adapter;
3. reroute to another compatible resource;
4. degrade the feature;
5. queue for later;
6. ask for human input only when no safe deterministic route remains.

## Portable mesh
`mesh_gateway.py` and `portable_worker.py` use the Python standard library. Any authorized machine that can run Python can become a HARUM worker after receiving its own secret through the environment.

## Evolution
`evolution_loop.py` does not rewrite production code automatically. It emits proposals from telemetry. Promotion requires validation, regression tests, rollback and policy gates.
