# Zero-Cost Compute Mesh

## Kaggle
As of 2026-09-19, Kaggle has retired P100 and directs Notebook users to T4x2: two T4 GPUs with 16 GB each. Harum treats them as two lanes inside one authorized Notebook session.

## Hugging Face ZeroGPU
Free users can consume small daily ZeroGPU quota. Harum treats this as burst compute for short/distilled hero shots, never as an always-on farm.

## Colab Free
Interactive notebook only. Do not use free managed Colab runtimes as distributed workers or to bypass service limits.

## GitHub Actions
Public-repository standard runners are free. Use for CI, QC, packaging, manifests and CPU post-processing, not abusive rendering.

The scaling trick is decomposition: independent microshots + deterministic CPU assembly, not quota evasion.
