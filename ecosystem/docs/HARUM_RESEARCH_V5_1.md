# HARUM Research v5.1 — performance + fallback mesh

Newly assimilated:
- DiffSynth-Studio (Apache-2.0): Wan runtime with VRAM management, disk/CPU offload, VAE tiling, TeaCache knobs and xFuser multi-GPU support.
- CogVideoX-2B (Apache-2.0): low-memory T2V fallback; official model card reports Diffusers INT8/TorchAO starting around 3.6 GB VRAM.
- Mochi 1 (Apache-2.0): permissive video model and ComfyUI consumer-GPU support; keep as a secondary engine after local fit benchmarking.
- Open-Sora framework (Apache-2.0): research/training framework; upstream model licenses remain separate.
- TeaCache: mostly Apache-2.0; training-free timestep cache that supports many video/image diffusion families.
- SageAttention (Apache-2.0), FlashAttention (BSD-3-Clause), TorchAO (BSD-3-Clause): acceleration/quantization layers.
- whisper.cpp (MIT): CPU-first transcription/caption route.
- VapourSynth (LGPL-2.1) and MoviePy (MIT): additional programmable post layers.
- SwarmUI: multi-GPU generation/orchestration option when owned/authorized GPUs exist; dependency licenses are mixed.
