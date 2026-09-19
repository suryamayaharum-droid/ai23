# HARUM Local Brain Training

The training path is deliberately separate from the inference path.

## Default candidate
Qwen3.5 2B LoRA is the first personal adaptation target because the current
Unsloth guidance estimates roughly 5 GB VRAM for bf16 LoRA. Qwen3.5 4B is a
second tier at roughly 10 GB VRAM.

## Data source
Only `accepted` entries from the verified experience buffer are compiled into
`runtime/cortex-training.jsonl`.

Minimum default: 200 verified examples.

Model self-approval is not enough. Examples should originate from:
- deterministic checks;
- successful real tasks with verified output;
- canonical HARUM documentation;
- human-approved corrections;
- test cases with known answers.

## Training gate
The script refuses to train unless:
- `HARUM_ALLOW_TRAINING=1`;
- CUDA is available;
- minimum verified dataset size is met.

It saves LoRA adapters locally. It does not upload them anywhere.

## Promotion
A trained adapter is still only a **candidate**.
Before it becomes part of the cortex it must:
1. run the regression suite;
2. beat the base model by the configured delta;
3. show no regression on truth/secret/provenance invariants;
4. pass latency/memory budget;
5. have a rollback model available.

Only after promotion should it be exported as GGUF for llama.cpp.
