package main

import (
	"context"
	"crypto/sha256"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"time"

	libp2p "github.com/libp2p/go-libp2p"
	"github.com/libp2p/go-libp2p/core/host"
	"github.com/libp2p/go-libp2p/core/network"
	"github.com/libp2p/go-libp2p/core/peer"
	"github.com/libp2p/go-libp2p/core/protocol"
	"github.com/libp2p/go-libp2p/p2p/security/noise"
)

const BrainProto = protocol.ID("/harum/brain-decision/20.1.0")

type Envelope struct {
	SHA256  string `json:"sha256"`
	Payload string `json:"payload_b64"`
}

type Ack struct {
	Verified bool   `json:"verified"`
	SHA256   string `json:"sha256"`
	Bytes    int    `json:"bytes"`
}

type Proof struct {
	Security    string `json:"security"`
	Transport   string `json:"transport"`
	Protocol    string `json:"protocol"`
	PayloadSHA  string `json:"payload_sha256"`
	PayloadSize int    `json:"payload_bytes"`
	Verified    bool   `json:"verified"`
	NoiseActive bool   `json:"noise_active"`
}

func makeHost() (host.Host, error) {
	return libp2p.New(
		libp2p.ListenAddrStrings("/ip4/127.0.0.1/tcp/0"),
		libp2p.Security(noise.ID, noise.New),
	)
}

func digest(b []byte) string {
	h:=sha256.Sum256(b)
	return hex.EncodeToString(h[:])
}

func main() {
	if len(os.Args)!=2 { panic("usage: brain_payload_proof <brain-proof.json>") }
	payload,err:=os.ReadFile(os.Args[1]); if err!=nil{panic(err)}
	want:=digest(payload)

	ctx,cancel:=context.WithTimeout(context.Background(),20*time.Second);defer cancel()
	a,err:=makeHost();if err!=nil{panic(err)};defer a.Close()
	b,err:=makeHost();if err!=nil{panic(err)};defer b.Close()

	b.SetStreamHandler(BrainProto,func(s network.Stream){
		defer s.Close()
		var e Envelope
		if json.NewDecoder(s).Decode(&e)!=nil{return}
		raw,err:=base64.StdEncoding.DecodeString(e.Payload);if err!=nil{return}
		got:=digest(raw)
		_ = json.NewEncoder(s).Encode(Ack{Verified:got==e.SHA256,SHA256:got,Bytes:len(raw)})
	})

	if err:=a.Connect(ctx,peer.AddrInfo{ID:b.ID(),Addrs:b.Addrs()});err!=nil{panic(err)}
	s,err:=a.NewStream(ctx,b.ID(),BrainProto);if err!=nil{panic(err)};defer s.Close()
	state:=s.Conn().ConnState()
	if err:=json.NewEncoder(s).Encode(Envelope{SHA256:want,Payload:base64.StdEncoding.EncodeToString(payload)});err!=nil{panic(err)}
	var ack Ack
	if err:=json.NewDecoder(s).Decode(&ack);err!=nil{panic(err)}
	proof:=Proof{
		Security:string(state.Security),Transport:state.Transport,Protocol:string(s.Protocol()),
		PayloadSHA:want,PayloadSize:len(payload),Verified:ack.Verified && ack.SHA256==want && ack.Bytes==len(payload),
		NoiseActive:string(state.Security)==string(noise.ID),
	}
	enc:=json.NewEncoder(os.Stdout);enc.SetIndent("","  ");_ = enc.Encode(proof)
	if !proof.Verified || !proof.NoiseActive { fmt.Fprintln(os.Stderr,"cognitive synapse proof failed");os.Exit(4) }
}
