# HARUM Browser Federation

## Same device
BroadcastChannel + Web Locks coordinate tabs and Web Workers.

## Different devices with no VPS
WebRTC DataChannels can connect browser nodes peer-to-peer. The initial SDP offer
and answer can be exchanged manually (copy/paste/QR). Once connected, task events
and CRDT deltas travel directly between browsers.

This deliberately avoids depending on a signaling server. Automatic discovery
across the public internet would require some signaling rendezvous service.

## Holographic state
The browser layer uses a Lamport-clock LWW map:
- every update carries clock + node ID;
- nodes gossip facts;
- merging is deterministic;
- offline nodes can reconnect and converge.

This is not intended for secrets. Shared facts are operational state only.

## Scheduling
A leader is elected per browser origin using Web Locks. The leader leases local
tasks, executes bounded batches, and returns expired leases to READY.

Across different devices there is no permanent master; each peer is an
independent cell and CRDT/gossip provides convergence.
