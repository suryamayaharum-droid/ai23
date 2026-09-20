# Browser Brain research — 2026-09-20

- @wllama/wllama 3.6.1 runs llama.cpp in browsers via WebAssembly SIMD and does not require a backend or GPU.
- `allowOffline` allows cached-model loading.
- ModelManager manages downloads, validation and cached models.
- `n_gpu_layers: 0` disables GPU inference.
- wllama recommends Q4/Q5/Q6 quantization for browser use.
- SmolLM2-135M-Instruct-GGUF is Apache-2.0; Q4_K_M is about 105 MB.