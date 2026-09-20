# HARUM Crystal Cortex v24 — deep research synthesis

The practical solution is a dual-plane organism. The hot plane uses libp2p AutoNAT, Circuit Relay v2 and DCUtR hole punching for low-latency peer connectivity. The cold plane uses signed Drop/store-carry-forward capsules, so synchronization still completes when two peers are never online together.

Relays should not be eliminated; they should be disposable and untrusted. A private peer should reserve with more than one relay, attempt a direct upgrade, and retain an end-to-end encrypted relayed path if the NAT cannot be punched. Address discovery is optional and plural: DHT/bootstrap, persisted peer stores, LAN discovery, manually exchanged invites, or Pkarr/mainline-DHT style records.

For a growing cortex, flooding all lesson IDs is the wrong scaling model. Willow range-based set reconciliation and Nostr Negentropy show that peers can recursively compare compact fingerprints and descend only into disagreeing ranges. Minisketch/PinSketch is a strong optional optimization when differences are small; rateless IBLT research is promising when difference cardinality is unknown. v24 implements a dependency-free prefix-Merkle reconciliation layer.

Validated model outputs become signed lesson capsules, but they do not automatically become rules. A rule is crystallized only after at least three validated capsules, at least two distinct model sources, at least two distinct validators, and zero contradictory validated actions. Exact matches and active class rules bypass the LLM. Approximate matches are context only.
