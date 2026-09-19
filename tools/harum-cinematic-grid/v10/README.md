# HARUM CPU CINEMA / MEDIA FABRIC v10

The exponential step after Event Horizon v9 is to make **media itself CPU-native**.

## What changed
- face-aware rigid foreground + inpainted background parallax;
- CPU microshots rendered independently and in parallel;
- optical-flow interpolation adapter using OpenCV DIS;
- content-addressed storage (CAS) for every artifact;
- event-horizon compatible tasks;
- final 1080x1920 H.264/AAC master without requiring a GPU.

## Principle
Do not ask a diffusion model to synthesize 240 frames when 4 canonical frames + physically plausible motion can tell the scene. Neural generation becomes sparse and optional.

## State-of-the-art path
When installed, OpenVINO Model Server can provide CPU image generation/editing and TTS; llama.cpp can provide quantized CPU planning; whisper.cpp can provide CPU ASR. The Media Fabric remains functional when none of those optional services exist.
