package main

import (
	"github.com/libp2p/go-libp2p"
	"github.com/libp2p/go-libp2p/core/peer"
)

// PrivatePeerOptions returns canonical settings for a peer that has
// authorized relay candidates. Real DCUtR success must be measured
// on deployed NATed devices.
func PrivatePeerOptions(relays []peer.AddrInfo) []libp2p.Option {
	return []libp2p.Option{
		libp2p.EnableRelay(),
		libp2p.EnableAutoRelayWithStaticRelays(relays),
		libp2p.EnableHolePunching(),
	}
}
