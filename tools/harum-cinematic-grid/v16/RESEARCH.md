# HARUM Nervous System v16 — canonical research notes

The canonical default is now transport-independent and local-first.

High-value technologies:
- Willow Drop Format for asynchronous improvised-channel transfer.
- Earthstar v11 for browser/offline multiwriter data on Willow.
- Reticulum for medium-agnostic resilient links.
- libp2p for relay/NAT traversal and multi-transport P2P.
- Iroh 1.0 for direct QUIC connectivity plus verifiable blobs/gossip/doc protocols.
- Hypercore for secure append-only sparse-replicated logs.
- GNUnet CADET as a privacy-preserving decentralized encrypted overlay.
- SCION for path-aware routing, trust information and failure isolation.
- NDN as an architectural pattern for named content and caching.
- IPFS for public immutable artifact addressing.
- Freenet as an experimental WASM-contract decentralized state substrate.

Space is incorporated as a public sensing plane:
- SatNOGS public satellite/TLE/telemetry/transmitter/observation data.
- CelesTrak GP/OMM data with caching and usage-policy-aware refreshes.
No spacecraft command/control is included.

Patent watch:
Generic CRDT/DTN concepts are old/open research areas, but recent patent publications contain claim-specific synchronization, edge mesh, graph-CRDT and satellite-DTN mechanisms. v16 keeps a watch list and avoids copying claim-specific mechanisms. RaptorQ remains optional; the default FEC is a simple one-erasure XOR parity scheme.
