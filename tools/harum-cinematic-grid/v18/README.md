# HARUM Living Circuit v18

This version closes the first real end-to-end loop inside one physical host using separate processes and a real TCP transport.

`Peer A signs task -> TCP -> Peer B verifies identity + capability -> allowlisted execution -> CAS -> Peer B signs receipt -> TCP -> Peer A verifies -> server restart -> same task replays idempotently from durable state`

## Properties
- Ed25519 node identity.
- Explicit expiring capability required for execution.
- Allowlisted task kinds only.
- SHA-256 content-addressed result storage.
- Persistent SQLite WAL state.
- Idempotent replay across process restart.
- Signed receipts.
- Quorum-gated update manifests.
- No paid API/GPU/VPS required for the core proof.

This does not claim multi-machine Internet deployment: the proof uses two independent processes communicating over localhost TCP on the current physical runtime.