# v20 research assimilation

Official llama.cpp documentation exposes local CPU/GPU inference, GGUF quantized models and an OpenAI-compatible `/v1/chat/completions` endpoint. The current official quick-start includes `ggml-org/Qwen3.5-0.8B-GGUF`.

The current Qwen3.5-0.8B Q4_0 GGUF is Apache-2.0, approximately 563 MB, with published SHA-256 `57d1997790d1744fba5b40a7317df71ea5e2acee28c47e78f0cce39c0703f8cf`.

Official go-libp2p examples expose the Noise secure transport. libp2p connection state reports the negotiated security protocol, so the proof asserts `/noise` rather than merely assuming encryption.

Harum therefore stops reimplementing production versions of these two primitives:
- peer transport/security → libp2p/Noise;
- local model inference → llama.cpp/GGUF.

Harum retains its own capabilities, event sourcing, CAS, attestation and orchestration above those runtimes.
