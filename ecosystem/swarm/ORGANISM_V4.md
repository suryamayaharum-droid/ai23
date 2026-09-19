# HARUM ORGANISM v4 — DIGITAL TWIN + REFLEXES

Version 4 adds a cognitive map without requiring an LLM inside the background runtime.

## Digital twin
The runtime reconstructs:
- macro city districts/swarms;
- micro agents;
- capabilities;
- resources;
- relations between providers and capabilities;
- a compact knowledge graph.

## Reflexes
Reflexes are small deterministic reactions to health signals. They are intentionally less powerful than deliberate planning.

Examples:
- dead letter → inspect;
- external bottleneck → aggregate queue;
- stale cell → request heartbeat;
- queue pressure → propose bounded sharding.

Reflexes cannot:
- publish externally;
- make commerce claims;
- carry secrets;
- bypass quotas;
- perform unauthorized writes.

## Supabase
If a Supabase project becomes available, v4 inherits the v3 hybrid state mirror automatically. If not, it remains fully functional on SQLite + Git + Airtable blackboard.
