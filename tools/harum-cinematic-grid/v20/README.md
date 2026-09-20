# HARUM Native Brain Fabric v20

v20 closes two major gaps left by v19:

1. **actual libp2p + Noise** using the official Go implementation;
2. **actual GGUF quantized LLM inference** using llama.cpp + Qwen3.5-0.8B Q4_0 on CPU.

## Architecture

`mission → logical brain council → local llama.cpp → signed decision artifact → secure peer layer → execution → CAS/attestation`

Logical brains share one loaded quantized model process by default. This is intentional: logical specialization should not be confused with physical compute.

## Validation

The CI workflow fails unless:
- a real libp2p stream connects;
- connection state reports security protocol `/noise`;
- the Harum application protocol negotiates;
- llama.cpp starts a local CPU server with the quantized GGUF;
- Router, Planner, Critic and Synthesizer all receive real model outputs.

The GitHub-hosted runner is a bounded validation substrate, not a permanent Harum node or render farm.
