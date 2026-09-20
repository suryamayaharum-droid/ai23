package main

import (
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"strings"
	"time"

	libp2p "github.com/libp2p/go-libp2p"
	"github.com/libp2p/go-libp2p/core/network"
	"github.com/libp2p/go-libp2p/core/peer"
	"github.com/libp2p/go-libp2p/core/protocol"
	circuitclient "github.com/libp2p/go-libp2p/p2p/protocol/circuitv2/client"
	"github.com/libp2p/go-libp2p/p2p/security/noise"
	ma "github.com/multiformats/go-multiaddr"
)

const Proto = protocol.ID("/harum/relay-proof/23.0.0")

type Proof struct {
	RelayID string
	ReceiverID string
	DialerID string
	ReservationOK bool
	Relayed bool
	NoiseActive bool
	RemoteMultiaddr string
	Response string
	Protocol string
}

func main() {
	ctx, cancel := context.WithTimeout(context.Background(), 20*time.Second)
	defer cancel()

	relay, err := libp2p.New(
		libp2p.ListenAddrStrings("/ip4/127.0.0.1/tcp/0"),
		libp2p.Security(noise.ID, noise.New),
		libp2p.ForceReachabilityPublic(),
		libp2p.EnableRelayService(),
	)
	if err != nil { panic(err) }
	defer relay.Close()

	receiver, err := libp2p.New(
		libp2p.ListenAddrStrings("/ip4/127.0.0.1/tcp/0"),
		libp2p.Security(noise.ID, noise.New),
		libp2p.EnableRelay(),
		libp2p.ForceReachabilityPrivate(),
	)
	if err != nil { panic(err) }
	defer receiver.Close()

	dialer, err := libp2p.New(
		libp2p.ListenAddrStrings("/ip4/127.0.0.1/tcp/0"),
		libp2p.Security(noise.ID, noise.New),
		libp2p.EnableRelay(),
	)
	if err != nil { panic(err) }
	defer dialer.Close()

	receiver.SetStreamHandler(Proto, func(s network.Stream) {
		defer s.Close()
		line, err := bufio.NewReader(s).ReadString('\n')
		if err != nil && err != io.EOF { return }
		fmt.Fprintf(s, "relay-ack:%s\n", strings.TrimSpace(line))
	})

	relayInfo := peer.AddrInfo{ID: relay.ID(), Addrs: relay.Addrs()}
	if err := receiver.Connect(ctx, relayInfo); err != nil { panic(err) }
	reservation, err := circuitclient.Reserve(ctx, receiver, relayInfo)
	if err != nil { panic(err) }

	relayBase := relay.Addrs()[0]
	relayPeer, _ := ma.NewMultiaddr("/p2p/" + relay.ID().String())
	circuit, _ := ma.NewMultiaddr("/p2p-circuit")
	targetPeer, _ := ma.NewMultiaddr("/p2p/" + receiver.ID().String())
	full := relayBase.Encapsulate(relayPeer).Encapsulate(circuit).Encapsulate(targetPeer)

	ai, err := peer.AddrInfoFromP2pAddr(full)
	if err != nil { panic(err) }
	if err := dialer.Connect(ctx, *ai); err != nil { panic(err) }

	s, err := dialer.NewStream(ctx, receiver.ID(), Proto)
	if err != nil { panic(err) }
	defer s.Close()
	if _, err := fmt.Fprintln(s, "harum-v23"); err != nil { panic(err) }
	resp, err := bufio.NewReader(s).ReadString('\n')
	if err != nil && err != io.EOF { panic(err) }

	state := s.Conn().ConnState()
	remote := s.Conn().RemoteMultiaddr().String()
	proof := Proof{
		RelayID:relay.ID().String(),
		ReceiverID:receiver.ID().String(),
		DialerID:dialer.ID().String(),
		ReservationOK: reservation != nil,
		Relayed: strings.Contains(remote, "p2p-circuit") || s.Conn().Stat().Limited,
		NoiseActive: string(state.Security) == string(noise.ID),
		RemoteMultiaddr:remote,
		Response:strings.TrimSpace(resp),
		Protocol:string(s.Protocol()),
	}
	enc:=json.NewEncoder(os.Stdout);enc.SetIndent("","  ");_ = enc.Encode(proof)
	if !proof.ReservationOK || !proof.Relayed || !proof.NoiseActive || proof.Protocol != string(Proto) {
		os.Exit(3)
	}
}
