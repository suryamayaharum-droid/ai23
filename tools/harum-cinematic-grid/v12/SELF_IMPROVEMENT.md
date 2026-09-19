# Bounded self-improvement

The organism improves itself through **evaluated configuration evolution**, not uncontrolled model-weight rewriting.

Promotion loop:
1. observe real task outcomes;
2. generate candidate changes to role prompts, routing weights, retrieval queries or tool heuristics;
3. run held-out benchmarks;
4. run hard gates: zero-cost, truth, identity, security, license;
5. promote only if the candidate improves the score;
6. keep the previous version for rollback;
7. record the experience in durable memory.

Why not automatically retrain weights on every interaction?
- CPU training is expensive;
- self-generated data can amplify its own mistakes;
- prompt/router/retrieval evolution is cheap, reversible and measurable;
- a curated experience dataset can later become a deliberate offline LoRA/finetune job.
