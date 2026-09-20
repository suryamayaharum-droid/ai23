package main

import (
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"time"

	libp2p "github.com/libp2p/go-libp2p"
	"github.com/libp2p/go-libp2p/core/host"
	"github.com/libp2p/go-libp2p/core/network"
	"github.com/libp2p/go-libp2p/core/peer"
	"github.com/libp2p/go-libp2p/core/protocol"
	"github.com/libp2p/go-libp2p/p2p/security/noise"
)

const Proto = protocol.ID("/harum/synapse/20.0.0")

type Message struct {
	Task string `json:"task"`
	Hash string `json:"hash"`
}

type Proof struct {
	HostA       string `json:"host_a"`
	HostB       string `json:"host_b"`
	Security    string `json:"security"`
	Transport   string `json:"transport"`
	Protocol    string `json:"protocol"`
	Response    string `json:"response"`
	Connected   bool   `json:"connected"`
	NoiseActive bool   `json:"noise_active"`
}

func makeHost() (host.Host, error) {
	return libp2p.New(
		libp2p.ListenAddrStrings("/ip4/127.0.0.1/tcp/0"),
		libp2p.Security(noise.ID, noise.New),
	)
}

func main() {
	ctx, cancel := context.WithTimeout(context.Background(), 20*time.Second)
	defer cancel()

	a, err := makeHost()
	if err != nil { panic(err) }
	defer a.Close()
	b, err := makeHost()
	if err != nil { panic(err) }
	defer b.Close()

	b.SetStreamHandler(Proto, func(s network.Stream) {
		defer s.Close()
		line, err := bufio.NewReader(s).ReadString('\n')
		if err != nil && err != io.EOF { return }
		var m Message
		if json.Unmarshal([]byte(line), &m) != nil { return }
		fmt.Fprintf(s, "ack:%s\n", m.Hash)
	})

	info := peer.AddrInfo{ID:b.ID(), Addrs:b.Addrs()}
	if err := a.Connect(ctx, info); err != nil { panic(err) }
	s, err := a.NewStream(ctx, b.ID(), Proto)
	if err != nil { panic(err) }
	defer s.Close()

	state := s.Conn().ConnState()
	msg := Message{Task:"harum-native-libp2p-proof", Hash:"9f20"}
	raw,_:=json.Marshal(msg)
	if _,err:=fmt.Fprintf(s,"%s\n",raw);err!=nil{panic(err)}
	resp,err:=bufio.NewReader(s).ReadString('\n')
	if err!=nil && err!=io.EOF{panic(err)}

	proof:=Proof{
		HostA:a.ID().String(),
		HostB:b.ID().String(),
		Security:string(state.Security),
		Transport:state.Transport,
		Protocol:string(s.Protocol()),
		Response:resp,
		Connected:true,
		NoiseActive:string(state.Security)==string(noise.ID),
	}
	enc:=json.NewEncoder(os.Stdout);enc.SetIndent("","  ")
	if err:=enc.Encode(proof);err!=nil{panic(err)}
	if !proof.NoiseActive { os.Exit(3) }
}
