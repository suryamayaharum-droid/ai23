# Resilient networking research — 2026-09-19

Harum v14.1 combines several open resilience patterns:

- IETF Bundle Protocol v7: store-carry-forward for disrupted, intermittent and high-delay networks.
- Reticulum: user-space, medium-agnostic encrypted networking over Ethernet/Wi-Fi/TCP/UDP/serial/stdio/I2P and optional radio links.
- libp2p: multi-transport P2P, encrypted connections, AutoNAT, relay and hole punching.
- Yggdrasil: encrypted self-healing IPv6 overlay; public mesh is treated as untrusted.
- Syncthing: direct block-hash replication for trusted devices; suitable for immutable artifact/CAS folders.
- IPFS: content-addressed artifact identity and Merkle DAG distribution.
- Freenet 2026: experimental WASM-contract decentralized shared state with summary/delta synchronization.
- Briar and Secure Scuttlebutt: offline/direct-sync and append-only gossip design inspiration.
- Willow: offline-first eventually-consistent data, capability security, confidential sync and a Drop Format explicitly designed for arbitrary carriers such as sneakernet, email and messaging.
- Earthstar v11: Willow-powered browser/distributed/offline-first database with servers optional, Ed25519 verification and sneakernet support.
- Iroh: direct QUIC P2P with verifiable blobs, gossip and multiwriter document sync; useful as an optional high-performance transport, but hosted relay services are not a zero-paid core dependency.
- Named Data Networking: route by content name rather than host location, with reusable in-network caching; useful as routing inspiration for immutable Harum artifacts.
- RaptorQ (RFC 6330): fountain forward-error correction that can recover objects from almost any sufficiently large subset of encoding symbols; promising for future lossy-carrier model/artifact transfer.

The core is deliberately transport-agnostic:
Bundle Envelope + Content Addressing + Mergeable State + Store/Carry/Forward + Multi-Transport Router.

Harum does not claim Willow/Freenet/BPv7 wire compatibility. Their patterns are assimilated while adapters remain explicit and separately tested.
