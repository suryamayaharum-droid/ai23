# Research assimilation — 2026-09-19

## Integrated direction
- FramePack for progressive long-video generation on low VRAM.
- HunyuanVideo-1.5 step-distilled I2V as a fast route.
- LTX-2 for synchronized audio/video, keyframes and extension.
- SkyReels V3 for multi-reference, audio-guided and video-to-video.
- LightX2V for quantization, caching, distillation and offload.
- ComfyUI as the graph/API GPU backend.
- Video Depth Anything + SAM 2 + CoTracker3 for depth, masks and tracking.
- PySceneDetect + WhisperX for ingest.
- DINOv2 + VMAF for continuity/encode QC signals.
- OpenColorIO/ACES for color management.
- OpenTimelineIO for editorial interchange.
- Prefect Core as an optional self-hosted state/retry/cache layer.

## Design rule
The system maximizes quality by routing each shot to the smallest capable engine, then assembling deterministically. It does not bypass provider quotas and it keeps model/license review inside the publishing gate.
