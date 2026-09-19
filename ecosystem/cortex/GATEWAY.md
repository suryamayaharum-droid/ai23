# HARUM Cortex Gateway

The gateway makes the local model assembly look like one OpenAI-compatible
provider.

Default endpoint:

`http://127.0.0.1:8899/v1`

Models:
- `harum-cortex:auto` — resource-aware single local brain.
- `harum-cortex:council` — independent proposals + synthesis.
- individual registered brain IDs.

## Security
The server binds to localhost by default. Binding to a non-local interface is
blocked unless `HARUM_CORTEX_API_KEY` exists.

The API key protects the gateway only. It is never copied into the organism bus
or committed to Git.

## Why this matters
Consumers are decoupled from model families. A swarm can keep calling the same
provider while the underlying brain changes from SmolLM to Qwen, Phi, a
fine-tuned HARUM adapter, or a council.
