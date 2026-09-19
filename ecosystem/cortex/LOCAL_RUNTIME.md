# LOCAL CORTEX RUNTIME

## Runtime pin
Smoke validation uses a pinned llama.cpp Linux CPU release. The model weights stay in
the Hugging Face cache and are never committed to Git.

## Why GGUF
GGUF + llama.cpp gives HARUM a portable CPU-first execution path across Linux,
Windows and macOS, independent of a hosted inference API.

## Model cache
llama.cpp uses the Hugging Face local cache layout. CI caches only the selected
small model between runs.

## Validation tiers
- Tier A: Python architecture/unit tests — no model required.
- Tier B: one quantized 3B local inference smoke test.
- Tier C: multi-brain council benchmark.
- Tier D: optional LoRA/QLoRA training on authorized GPU resources.

No tier may claim success until its runtime output exists.
