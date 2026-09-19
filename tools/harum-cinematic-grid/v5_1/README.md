# HARUM Cinematic v5.1 — Plugin Runtime

v5.1 extends Harum Fusion with a plugin-style runtime.

New layers:
- DiffSynth-Studio for low-VRAM Wan execution, VAE tiling, offload, TeaCache and xFuser multi-GPU.
- CogVideoX-2B as an Apache-2.0 low-memory T2V fallback.
- Mochi 1 as an Apache-2.0 secondary video model.
- TeaCache, SageAttention, TorchAO and FlashAttention as optional speed/memory layers.
- whisper.cpp for CPU captions/transcription.
- VapourSynth / MoviePy as extra programmable post layers.

Scaling is legal/authorized: decompose scenes into microshots, use the two GPUs in a single Kaggle T4x2 session when available, burst to ZeroGPU within quota, keep Colab interactive, and run deterministic post/QC on CPU.

No account pooling, quota evasion, watermark bypass or unlicensed commercial route is allowed.
