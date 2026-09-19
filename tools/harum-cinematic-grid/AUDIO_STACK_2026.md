# Audio Stack 2026 — Harum Noir

## Voice
- Canonical voice stays locked until an editorial re-lock.
- Chatterbox Multilingual V3 is the preferred no-subscription candidate for a future free voice lock: MIT code, Portuguese support and a dedicated pt-BR language pack. Use only an authorized/self-owned reference if voice cloning is enabled.
- Qwen3-TTS is another multilingual route with Portuguese, voice design and voice-clone capabilities; license/checkpoint review is required before commercial deployment.
- Fish Speech uses a research-oriented license in current official releases, so it is not the default public/commercial route.

## Foley / ambience
- CPU procedural room tone remains zero-cost and deterministic.
- MMAudio can synthesize synchronized audio from video/text and its code is MIT; checkpoint/dependency terms still need review.
- FoleyCrafter is another video-to-audio option but explicitly asks commercial users to review Auffusion's license, so it stays yellow.

## Mastering
- Voice, music and foley are mixed after the visual master is approved.
- `harum_audio_master.py` outputs AAC 48 kHz and applies EBU R128 loudness normalization (default -16 LUFS, -1.5 dBTP).
