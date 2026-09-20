# Research notes — 2026-09-20

- llama.cpp currently supports JSON-schema constrained generation on server endpoints, including response_format on chat completions.
- libp2p's current connectivity stack uses AutoNAT, Circuit Relay v2 and DCUtR hole punching to connect nodes behind NAT/firewalls.
- GitHub documents that standard hosted jobs (except single-CPU container runners) receive newly provisioned virtual machines which are decommissioned after the job. This makes separate jobs useful for portability/store-carry-forward validation, but not proof of separate physical hosts.
- wllama v2+ includes model management/caching, validation, split GGUF handling and allowOffline; v3.1 supports n_gpu_layers: 0 for CPU-only browser inference.
