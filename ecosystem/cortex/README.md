# HARUM CORTEX ASSEMBLY

A local-first collective intelligence layer for HARUM.

This is not a claim of consciousness or literal singularity. It is a reproducible
multi-model system that combines independent quantized models, durable memory,
cross-critique, synthesis, evaluations and bounded improvement.

## Core brain pack

- **Qwen3 4B Q4_K_M** — planner/synthesizer.
- **Phi-4-mini Q4_K_M** — critic/code/logic judge.
- **SmolLM3 3B Q4_K_M** — fast scout/draft.
- **Qwen3 8B Q4_K_M** — optional deeper brain on larger RAM.
- **Nomic Embed Text v1.5** — optional semantic-memory encoder.

Weights are never committed to Git. The runtime downloads/caches GGUF only when needed.

## Assembly protocol

1. Task Router chooses a pack from RAM/capabilities.
2. Brains answer independently.
3. Their outputs are anonymized/aggregated.
4. A chair brain synthesizes agreements and disagreements.
5. Result is stored with model IDs, quantization and seed.
6. High-disagreement or low-confidence output remains unresolved instead of being
   treated as truth.
7. Accepted experiences may enter a training/evaluation buffer.

## Evolution

HARUM may automatically propose changes to:
- prompts;
- model routing;
- context budgets;
- ensemble composition;
- memory retrieval;
- quantization choice.

It does **not** silently rewrite production model weights or deploy untested code.
A candidate must outperform the current version on a regression suite and preserve
license/resource/safety/rollback invariants.

## Offline principle

The cortex can run entirely through llama.cpp + GGUF. External models may be used
as optional teachers or validators, but no mission should require them for basic
operation.
