# Research assimilation v5.1

- DiffSynth-Studio is Apache-2.0 and its Wan pipeline documents VRAM management, disk/CPU offload, VAE tiling, TeaCache and xFuser multi-GPU.
- CogVideoX-2B is Apache-2.0; the official model card documents Diffusers INT8/TorchAO inference starting around 3.6 GB VRAM.
- Mochi 1 is Apache-2.0 and has consumer-GPU support through ComfyUI.
- TeaCache is mostly Apache-2.0 and provides training-free timestep-aware caching across several diffusion/video families.
- SageAttention is Apache-2.0; TorchAO and FlashAttention are BSD-3-Clause.
- whisper.cpp is MIT and gives a CPU-first subtitle/transcription route.
- VapourSynth is LGPL-2.1; MoviePy is MIT.

Every checkpoint/dependency keeps its own license gate even when the execution framework is permissive.
