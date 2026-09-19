# HARUM CPU-FIRST EVENT HORIZON v9

## Central idea
GPU becomes optional. The core system is designed to stay functional on ordinary CPUs:

`text/intent -> keyframes -> sparse CPU inference/control -> procedural microshots -> deterministic edit -> audio -> QC -> publish package`

A generative model is not asked to synthesize every frame. CPU is used where it is strong:
- orchestration and planning;
- sparse image/keyframe generation when a CPU-capable model server exists;
- depth/mask/vision control;
- animation, optical interpolation, composition and encoding;
- TTS/ASR;
- durable workflows, metrics and indexing.

## Horizontal scale
`harum_cpu_mesh.py` implements a pull-based mesh over HTTP with persistent SQLite state. Workers can be separate owned machines. Localhost is the safe default; a real network deployment should add TLS/reverse proxy/firewall and a strong token.

## Vertical scale
`harum_vertical_cpu.py` detects actual CPU/RAM/SIMD and caps parallelism to avoid oversubscription. Optional execution providers: ONNX Runtime CPU, OpenVINO CPU, llama.cpp, whisper.cpp, OpenCV.

## Event Horizon
`harum_event_horizon.py` provides WAL state, event log, leases, recovery, DAG dependencies, delayed execution, retries/backoff, dead letters, snapshots and replay. It is the zero-dependency durable core. Temporal can replace/augment it later if permanent infrastructure exists.

## CPU AI Gateway
`harum_cpu_ai_gateway.py` talks to optional local services:
- OpenVINO Model Server: image generation/edit, Kokoro TTS, Whisper/ASR on CPU;
- llama.cpp: local quantized planning/router;
- eSpeak: lightweight TTS fallback.

The system must never claim physical CPU/GPU resources that do not actually exist.