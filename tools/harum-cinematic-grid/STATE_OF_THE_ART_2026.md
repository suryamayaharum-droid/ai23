# HARUM CINEMATIC GRID — State of the Art 2026

The pipeline is no longer one video generator. It is a modular production system:

`script -> scene graph -> shots -> model router -> render jobs -> QC -> edit -> color -> audio -> captions -> OTIO -> distribution`

## Graph and GPU orchestration
- ComfyUI: async queue, partial graph re-execution, smart VRAM/RAM, offload and quantized models.
- Harum Comfy Bridge: queues API-exported workflows on a local/authorized server and collects history.
- Airtable: editorial control-plane and render queue.
- GitHub: code, manifests, schemas and CI.

## Generation by function
- Wan2.2: preferred public-channel generative route because the official repo is Apache-2.0.
- MuseTalk 1.5: lip sync; MIT code and project states trained models are available for commercial use, subject to dependency licenses.
- LivePortrait: strong for microexpression, but bundled InsightFace models are non-commercial research; replace/remove that dependency before commercial production.
- HunyuanVideo-1.5: efficient and step-distilled but has territorial license restrictions; not a default for globally accessible YouTube masters.
- LTX-2.x: excellent audio/video + multi-keyframe; current 2026 community license requires version-specific review.
- SkyReels V3: multi-reference, audio-guided and video-to-video; commercial use is contemplated under Skywork Community License, subject to its terms.

## Acceleration / low VRAM
- LightX2V: distillation, quantization, caching and CPU/GPU/disk offload.
- WanGP: low-VRAM runtime/front-end with pose/depth/flow tools.
- Video2X: Vulkan/ncnn post-processing with Real-ESRGAN/Real-CUGAN/RIFE.

## Scene control
- Video Depth Anything Small: consistent video depth under Apache-2.0; use for parallax/camera/control.
- SAM 2: temporal masks for selective edits.
- pose/depth/flow are conditioning signals; they never replace FACE LOCK.

## Post
- FFmpeg: xfade, lut3d, EBU R128 loudnorm, black/freeze/silence QC.
- OpenColorIO/ACES: future color-management layer.
- OpenTimelineIO: NLE interchange.
- faster-whisper / whisper.cpp: local captions.
- PySceneDetect: cut detection and ingest analysis.

## Compute economy
GPU only synthesizes. CPU handles ingest, hashing/cache, proxies, edit, audio, captions, QC and packaging. Every generative shot keeps a deterministic fallback.
