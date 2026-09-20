# HARUM OUROBOROS NETWORK v15 — Research synthesis

The strongest pattern is an **application envelope above many transports**. Harum keeps its own event identity, TTL, content hash, capability metadata and trust state; carriers are replaceable.

## Networks
- Willow: local-first data, capability security and Drop Format for improvised asynchronous channels.
- Reticulum: medium-agnostic stack spanning Ethernet, Wi-Fi, TCP/UDP, serial, stdio, I2P and optional radio.
- libp2p: online P2P/NAT traversal layer.
- NDN: named immutable content and caching; aligns with Harum CAS.
- Freenet (current generation): experimental WASM-contract shared-state substrate.
- Tor/I2P: optional privacy transports for explicitly configured peers; not compute substrates and not targets for hidden-service crawling.
- RaptorQ: attractive for lossy asynchronous object transfer; optional pending licensing/patent review.

## Space
SatNOGS is a global open-source ground-station network with public observation/API data. Harum may consume satellites/TLE/telemetry as a read-only sensor organ. Spacecraft command/control requires explicit operator authorization and is outside the autonomous core.

## Patents
Recent publications exist around CRDT conflict handling and DTN/satellite routing. Prefer open RFCs/protocols and independently designed generic primitives; flag claim-specific mechanisms for legal review.

## Ouroboros
Sense → Validate → Learn → Plan → Act → Measure → Replicate → Hibernate → Wake.
Untrusted network input cannot directly rewrite executable code.