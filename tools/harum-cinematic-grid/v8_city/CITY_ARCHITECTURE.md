# HARUM SWARM CITY v8

A cidade é uma federação hierárquica:

**City Council → 18 Districts → 72 Swarms → 360 swarm-agent roles + 18 governors + 7 central roles = 385 functional roles.**

Physical work remains elastic and honest: the local scheduler executes at most the number of real worker slots supported by the current runtime. External GPU/connector capacity is declared separately.

## State-of-the-art patterns assimilated
- Ray-inspired resource-aware scheduling, task/actor separation, data locality and placement-group concepts.
- Temporal-inspired durable workflow/replay semantics.
- NATS/JetStream-inspired pub/sub + durable work queues.
- OpenTelemetry-inspired correlated events/traces/metrics.
- Circuit breakers, idempotency keys, dead-letter queues, backpressure and content-addressed artifacts.
- SQLite WAL is the zero-dependency local control plane; optional adapters upgrade the same architecture when infrastructure exists.

## Districts
Governo, Pesquisa, Memória, Marca, Narrativa, Imagem, Cinema, Áudio, Publicação, Growth, Comércio, CRM, Web, Automação, Infraestrutura, Segurança, Qualidade e Recursos.
