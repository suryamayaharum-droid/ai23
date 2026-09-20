# HARUM Durable Brain Fabric v21

v21 attacks the three remaining limitations directly.

## 1. Structured-output reliability
The tiny Qwen brain is no longer allowed to emit an arbitrary plan format. `harum_structured_brain.py` uses llama.cpp schema-constrained generation, a tiny allowlisted action vocabulary, strict local validation and one bounded retry.

## 2. Model persistence independent of the inference process
`harum_model_vault.py` splits any GGUF into SHA-256 content-addressed chunks and reconstructs it with full-file verification. The CI proof additionally caches the real Qwen3.5-0.8B Q4 model in one VM and restores/verifies it in a different VM before inference.

Browser persistence is mapped to wllama ModelManager + offline cache. A persistent device is still required for truly local long-term bytes; the organism never pretends otherwise.

## 3. Fresh-host store/carry/forward
The workflow creates a signed task on one GitHub-hosted VM, carries it as an artifact, verifies and executes it on a fresh VM, then verifies the signed receipt on a third fresh VM. This proves asynchronous carrier independence across fresh execution environments.

It is not direct peer-to-peer connectivity and GitHub does not guarantee these VMs are separate physical servers. Direct NAT traversal between independently controlled devices remains a deployment test.
