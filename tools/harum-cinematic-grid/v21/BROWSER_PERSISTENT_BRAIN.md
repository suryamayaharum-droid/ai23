# Browser Persistent Brain Path

wllama v2+ introduced ModelManager, cached model validation, split-GGUF handling, parallel shard downloads and an allowOffline option. v3.1 can force CPU-only inference with n_gpu_layers: 0.

Harum's browser path should therefore:
1. vendor the wllama WASM locally rather than rely on a CDN;
2. download a GGUF once through ModelManager;
3. validate it;
4. set allowOffline: true;
5. force n_gpu_layers: 0 when GPU independence is required;
6. keep Harum state and model manifest separate so the model can be replaced without losing organism memory.

This is an optional persistent-device path. The core still hibernates when no device is active.
