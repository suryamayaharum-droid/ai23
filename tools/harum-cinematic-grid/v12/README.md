# HARUM Quantized Brain Assembly v12

Local-first council of quantized AI brains for the Harum Holographic Organism.

## Core design
- One shared local GGUF model process can power many logical specialist brains through role prompts and independent context.
- Optional second/third model families add diversity when RAM permits.
- SQLite FTS5 provides deterministic memory/retrieval.
- Critic + sentinel challenge consensus.
- Evolution changes prompts, routing and retrieval heuristics; base weights do not self-rewrite.
- A candidate change is promoted only after held-out benchmarks and hard gates pass.

## Current recommended tiny brain
Qwen3.5-0.8B Q4_0 (~563 MB, Apache-2.0) via llama.cpp.

## Runtime truth
The current ChatGPT container has ~5.81 GB RAM / 5 CPU cores but no llama.cpp binary or GGUF weights installed, so v12's council/orchestration was tested with a deterministic mock backend. Real local inference begins once an owned machine has llama.cpp + local GGUF files.

## Offline mode
After the llama.cpp binary and GGUF files are downloaded once to an owned machine, inference can run without paid APIs or subscriptions.
