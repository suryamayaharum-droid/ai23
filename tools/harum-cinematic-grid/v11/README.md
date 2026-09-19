# HARUM Holographic Organism v11

A zero-paid-dependency coordination layer for the Arte Harum ecosystem.

## Core
- 16 organs × 24 logical cells = 384 logical cells.
- Real execution is capped by actual physical CPU resources; logical cells do not pretend to be physical processors.
- Shared blackboard for global workspace.
- Stigmergic pheromones for indirect prioritization.
- HoloBus peer sync with immutable events, Merkle roots and deterministic LWW state.
- Holographic capsules: every cell receives compact global capability/state digests and a routing map.
- Python + SQLite + filesystem are sufficient for coordination.
- Optional connectors are facultative organs, never mandatory dependencies.

## Proof
The current runtime executed 384/384 logical-cell audit tasks over 5 physical CPU workers. A three-peer localhost HoloBus proof started from three different states and converged to the same Merkle root.

The system remains useful without GPU, paid API, subscription, cloud database or external message broker.
