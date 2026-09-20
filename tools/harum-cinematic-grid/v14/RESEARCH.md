# Resilient networking research — 2026-09-19

Harum v14 combines several open resilience patterns:

- IETF Bundle Protocol v7: store-carry-forward for disrupted, intermittent and high-delay networks.
- Reticulum: user-space, medium-agnostic encrypted networking over Ethernet/Wi-Fi/TCP/UDP/serial/stdio/I2P and optional radio links.
- libp2p: multi-transport P2P, encrypted connections, AutoNAT, relay and hole punching.
- Yggdrasil: encrypted self-healing IPv6 overlay; public mesh is treated as untrusted.
- Syncthing: direct block-hash replication for trusted devices; suitable for immutable artifact/CAS folders.
- IPFS: content-addressed artifact identity and Merkle DAG distribution.
- Freenet 2026: experimental WASM-contract decentralized shared state with summary/delta synchronization.
- Briar and Secure Scuttlebutt: offline/direct-sync and append-only gossip design inspiration.

The core is deliberately transport-agnostic:
Bundle Envelope + Content Addressing + Mergeable State + Store/Carry/Forward + Multi-Transport Router.
