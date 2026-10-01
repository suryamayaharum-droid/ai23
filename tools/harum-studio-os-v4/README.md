# HARUM STUDIO OS v4

Software-defined microstudio for Arte Harum / Harum Noir.

Architecture:
Story -> CineGraph -> Production DB/EventBus -> Scheduler -> Authorized Workers -> Assets/Versions -> Review -> QC -> Provenance -> Master -> Distribution.

Core principles:
- shot-based production, not one-shot monolithic generation
- deterministic CPU pipeline whenever possible
- GPU only for synthesis that actually needs it
- asset identity, versioning, hashes and license gates
- rebuildable masters
- optional bridges to OpenCue, Ray, OpenAssetIO, AYON, Kitsu and OpenUSD
- no quota bypass or unauthorized compute

The full distributable package is also stored in the Harum Library as HARUM_STUDIO_OS_v4.zip.
