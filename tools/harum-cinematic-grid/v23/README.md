# HARUM Browser Brain v23

v23 removes the requirement for a local inference server.

The proof loads an Apache-2.0 SmolLM2-135M-Instruct Q4_K_M model through wllama, forces `n_gpu_layers: 0`, performs real WebAssembly CPU inference in Chromium, unloads the model, blocks all later `/model.gguf` network requests, then performs a second inference from wllama's local model cache.

The Service Worker caches only the app shell; the GGUF is deliberately excluded so the offline proof exercises wllama ModelManager persistence.

A browser/device remains physical compute. This removes backend/VPS/GPU dependence, not the physical need for CPU and memory.