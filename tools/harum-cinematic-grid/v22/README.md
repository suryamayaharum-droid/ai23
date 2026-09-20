# HARUM Semantic Immune System v22

The local LLM selects a typed recipe; deterministic code expands it into fixed steps.

Core rule: **prose is advisory, recipes are typed, execution is capability-gated.**

This removes a failure observed in v21.1 where a small model produced a safe action but described signature verification imprecisely. The reason text may be imperfect without changing how the cryptographic executor actually verifies hashes, signatures and scope.

An Evidence Ledger separates LLM hypotheses from verified facts. Autonomous promotion may depend only on verified evidence IDs.