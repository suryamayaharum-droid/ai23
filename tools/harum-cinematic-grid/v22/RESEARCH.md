# v22 research notes

- Qwen/Qwen3-1.7B-GGUF is Apache-2.0; its official Q8_0 GGUF is about 1.83 GB.
- llama.cpp supports JSON-schema constrained server generation.
- llama.cpp supports speculative decoding with draft models and draftless n-gram methods. v22 keeps it optional until measured because short structured decisions may not benefit.
- On constrained machines, the deep model is a sequential hot-swap/fallback rather than a permanently co-resident service.