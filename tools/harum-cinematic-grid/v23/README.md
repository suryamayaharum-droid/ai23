# HARUM Connectivity Fabric v23

v23 addresses the last major deployment-layer gap: reachability between peers that cannot accept direct inbound connections.

## Design
- direct libp2p connection when reachable;
- Circuit Relay v2 reservation/relay fallback;
- AutoNAT to classify public/private reachability;
- DCUtR / hole punching enabled for NATed peers;
- Noise-secured libp2p streams;
- HoloBus / signed Harum envelopes stay above the carrier.

## Proof boundary
CI can prove a real Circuit Relay v2 path between separate libp2p hosts and compile the AutoRelay + hole-punch configuration. A true two-NAT physical-device DCUtR proof still requires two independently controlled devices/networks; CI on one runner must not be called that.

## Zero-paid core
No paid relay is required by design. An owned/public Harum node may act as a bounded relay. Relay resource limits and ACLs should be enabled in deployment.