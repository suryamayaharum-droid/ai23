# Research assimilation

## libp2p
Peer identity is cryptographically bound to public keys, and secure channels such as Noise add encrypted transport and forward secrecy. Harum v18 mirrors the self-certifying identity idea but does not claim libp2p wire compatibility.

## Willow / Meadowcap
Willow separates data from transport and Meadowcap uses capabilities for fine-grained access. v18 adopts explicit, receiver-bound, expiring execution capabilities.

## TUF
Secure update systems must resist arbitrary installation, rollback and freeze attacks. TUF uses signed metadata, expiration, role separation and signature thresholds. v18 adds version/expiry checks and threshold approvals for update manifests.

## in-toto
Supply-chain integrity benefits from signed evidence that authorized actors performed expected steps. v18's signed execution receipt is the first minimal attestation chain; later versions can expand it to per-step attestations.

## Nostr
Nostr demonstrates a small relay protocol in which events are content-hashed and signed while relays remain untrusted. This is useful inspiration for an optional Harum relay carrier, but v18 keeps its existing Ed25519 identity system instead of pretending NIP-01 compatibility.