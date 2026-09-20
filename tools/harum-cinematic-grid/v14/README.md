# HARUM RESILIENT MESH v14

Transport-independent survival layer for the Harum organism.

Core:
- store-carry-forward Harum capsules with TTL, priority, integrity hashes and receipts;
- mergeable operation-log state;
- adaptive transport selection;
- optional adapters for Reticulum, libp2p, Yggdrasil, Syncthing, IPFS and Freenet.

No external network is the source of truth. A capsule can travel by LAN, shared folder, USB/SD, Bluetooth file transfer, nearby sharing, Syncthing or any future carrier.

Security: SHA-256 verifies integrity, not identity or secrecy. Hostile-network use must add authenticated encryption/signatures or run through an encrypted transport.
