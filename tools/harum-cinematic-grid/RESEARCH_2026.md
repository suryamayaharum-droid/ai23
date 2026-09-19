# HARUM VIDEO RESEARCH — 2026-09-19

## Architecture decision

A state-of-the-art Harum Noir pipeline is a shot router, not one generator:

- identity-safe motion: FFmpeg
- portrait motion: LivePortrait
- lip sync: MuseTalk 1.5
- I2V: Wan2.2, HunyuanVideo-1.5, LTX/LTX-2
- multi-reference/audio/video: SkyReels V3
- low-VRAM execution: WanGP
- accelerated inference: LightX2V
- interpolation: RIFE
- upscale: Real-ESRGAN
- final assembly: Harum Cinematic Grid

## Global-publishing license gate

MiniMax H3 is technically attractive, but its current Community License defines an Applicable Territory that excludes the EU, UK, South Korea and USA and restricts display of Outputs outside the Applicable Territory. A globally accessible YouTube/Instagram master can cross those territories. Do not route Harum public-channel masters through H3 without a license that covers global display.

## Compute policy

- Never bypass provider quotas or pool free accounts.
- Colab Free is interactive only; Google explicitly forbids distributed-compute workers on free managed runtimes.
- Kaggle/ZeroGPU are opportunistic GPU slots.
- CPU handles composition/QC/audio so scarce GPU time is spent on synthesis only.
