# Research assimilation — Secure Synapse v19

libp2p binds peer identity to public keys and uses Noise to create encrypted peer channels with forward secrecy. Harum v19 adopts the architectural principle: long-term signing identity authenticates fresh ephemeral session keys.

in-toto models a supply chain as signed steps performed by authorized functionaries over expected materials/products. v19 adds a minimal signed hash-linked attestation chain for handshake, authorization, execution, CAS commit and receipt creation.

The next production-quality transport step is an actual libp2p implementation across two separately administered hosts. The current v19 proof intentionally stays dependency-light and localhost-only so the trust/execution circuit can be validated before introducing NAT traversal, relays and broader networking.
