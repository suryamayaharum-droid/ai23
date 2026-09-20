# HARUM Immune Mesh v17

The mesh now has an immune/trust layer.

## Added
- Ed25519 node identities.
- Signed events/manifests.
- Scoped, expiring capability tokens.
- Quarantine for autonomous update candidates.
- Hash verification, test gates and rollback references before promotion.

## Why this matters
A decentralized network without identity and update discipline is easy to poison. v17 makes network input non-authoritative by default and separates **receiving information** from **granting execution authority**.

## Design references
- libp2p PeerID/Noise identity pattern.
- Willow Meadowcap capability access model.
- TUF compartmentalized, expiring trust.
- in-toto signed execution/attestation chains.

The implementation here is independently small and does not claim protocol compatibility with those projects.
