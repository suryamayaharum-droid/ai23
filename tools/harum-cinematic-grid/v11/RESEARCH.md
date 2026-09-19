# Research assimilation — v11

The design combines several established patterns:

- Blackboard architecture: independent specialists contribute to a shared structured workspace.
- Stigmergy: agents coordinate indirectly by leaving environmental traces; Harum uses virtual pheromones with decay.
- Gossip/anti-entropy: peers compare what they have seen and exchange missing events instead of requiring full connectivity.
- Local-first/CRDT thinking: local state remains primary and synchronization is a merge problem.
- Merkle/content addressing: state and artifacts are hash-verifiable and deduplicable.
- Event sourcing: immutable events make replay and long-horizon recovery possible.
- Resource-aware scheduling: hundreds of logical roles share the actual CPU/GPU pool honestly.
- Observability: events and roots make autonomy auditable.

The zero-subscription reference core intentionally does not require NATS, Ray, Automerge, libp2p or IPFS. Those projects inform the design and can later be optional adapters.
