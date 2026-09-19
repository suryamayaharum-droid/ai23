# HARUM VIDEO RESEARCH — 2026-09-19

## Architecture decision
A state-of-the-art pipeline for Harum Noir should not depend on a single model. It should be a **shot router**:

- identity-safe deterministic motion: FFmpeg
- portrait movement: LivePortrait
- lip sync: MuseTalk 1.5
- I2V / cinematic motion: Wan2.2, HunyuanVideo-1.5, LTX/LTX-2
- multi-reference/audio/video conditioning: SkyReels V3
- low-VRAM execution: WanGP
- accelerated inference: LightX2V
- interpolation: RIFE
- restoration/upscale: Real-ESRGAN
- final assembly: Harum Cinematic Grid

## Global-publishing license gate
MiniMax H3 is technically attractive (native stereo audio, multimodal context, 4–15s, up to 2K), but its current community license defines an Applicable Territory that excludes the EU, UK, South Korea and USA and also restricts display of Outputs outside the Applicable Territory. A globally accessible YouTube/Instagram publication can therefore reach excluded territories. **Do not use H3 for Harum public channel masters without a license that covers global display.**

## Compute policy
- Never bypass provider quotas or pool free accounts.
- Colab Free is interactive only; Google explicitly forbids distributed compute workers on free managed runtimes.
- Kaggle/ZeroGPU are opportunistic GPU slots.
- CPU does composition/QC/audio so scarce GPU time is spent only on synthesis.
