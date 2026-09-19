# CONNECTOR HANDOFF PROTOCOL

ChatGPT connectors are authenticated capabilities available only in an authorized ChatGPT execution context. They are not exported into GitHub Actions.

## Contract

When background code reaches a connector-only step:

1. checkpoint all deterministic work;
2. create a sanitized envelope in `ecosystem/runtime/external-queue.json`;
3. mark the local task `WAITING_EXTERNAL`;
4. continue unrelated work;
5. on the next authorized ChatGPT pulse, claim the envelope;
6. invoke the matching connector;
7. persist result + provenance;
8. resume dependents.

No token, cookie, password, API key or session secret may appear in the envelope.

This converts a session-bound limitation into a resumable boundary rather than a system-wide stop.
