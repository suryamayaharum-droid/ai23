# HARUM Secure Synapse v19

The Living Circuit now has a cryptographic transport layer.

## Executed path

`Peer A identity → signed ephemeral X25519 handshake → server identity pin → HKDF-SHA256 → ChaCha20-Poly1305 channel → signed task → capability gate → allowlisted execution → CAS → signed receipt → signed attestation chain → encrypted response`

The server was then restarted and the identical signed task was replayed from durable SQLite state without duplicate execution.

## Security properties demonstrated locally
- mutual cryptographic peer authentication;
- ephemeral X25519 session key agreement;
- AEAD encrypted frames;
- server identity pinning;
- signed task and receipt;
- scoped capability authorization;
- content-addressed result;
- chained signed attestations;
- ciphertext tampering rejected;
- durable idempotent replay after restart.

## Important
This is a small independent Noise-inspired design, not an implementation of the Noise/libp2p wire protocol. Production Internet deployment should prefer a mature, audited transport such as libp2p Noise/TLS/QUIC rather than inventing a new public cryptographic protocol.
