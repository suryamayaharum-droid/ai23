# Vendoring for true offline use

The repository intentionally does not hot-link runtime code or model weights.

For a browser brain that remains functional after disconnecting the network:
1. vendor a reviewed release of `@wllama/wllama` into `web/vendor/wllama/`;
2. place a quantized GGUF model or split chunks under `web/models/`;
3. write `web/models/model.json` with model name, SHA-256 hashes, license and chunk list;
4. load with GPU layers set to zero for CPU/WASM mode;
5. cache only after hash verification;
6. keep the deterministic rules/memory path as fallback.

This is a one-time acquisition step. After code + weights are local, the browser inference path no longer needs a hosted model API.
