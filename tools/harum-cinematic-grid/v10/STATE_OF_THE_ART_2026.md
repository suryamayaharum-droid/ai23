# HARUM CPU CINEMA v10 — State of the Art Notes (2026-09-19)

## Decision
GPU is an enhancement, not a dependency. The production core stays CPU-native and composes approved pixels into cinematic motion.

## CPU-native generation / inference
- OpenVINO Model Server 2026 exposes OpenAI-compatible image generation/edit endpoints and documents CPU serving for INT8 Stable Diffusion 1.5. It also exposes CPU TTS with Kokoro-82M INT8.
- llama.cpp supports CPU inference across AVX/AVX2/AVX512/AMX and low-bit quantization, useful for a future local planner/router.
- ncnn is a lightweight CPU inference runtime optimized for ARM/x86 edge workloads with fp16/int8 routes.
- ONNX Runtime CPU Execution Provider remains a portable inference fallback.

## CPU cinema
- OpenCV supplies robust global motion estimation and optical-flow primitives; v10 uses rigid face-aware parallax and provides a DIS optical-flow interpolation adapter.
- FFmpeg remains the deterministic final encoder, audio mixer and QC backend.
- The v10 CAS stores outputs by SHA-256 so duplicate renders can be reused.

## Scaling
- Vertical: quantization, SIMD, bounded thread pools, content cache, render at working resolution then upscale for master.
- Horizontal: Event Horizon v9 + pull-based CPU Mesh split independent shots across owned/authorized machines.
- Durable horizon: leases, idempotency, retries/backoff, dead letters, snapshots, replay.

## Current runtime proof
- CPU: 5 logical cores, ~5.81 GB RAM, AVX2 + AVX512.
- GPU: none.
- CPU Cinema v10 Face Lock proof: 4 microshots / 2 workers / ~8.875 s master / 1080x1920 / 24 fps / H.264 + AAC / ~10.18 s wall render in this runtime.
- Technical QC: no black, freeze or silence condition detected.

## Principle
Do not spend neural compute on frames that can be produced by camera mathematics, compositing and deterministic motion. Spend neural compute only on the sparse frames or semantic operations where it changes the result materially.
