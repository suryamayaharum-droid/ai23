# HARUM SWARM CITY — Arquitetura

## Princípio

O ecossistema cresce por **especialização + comunicação**, não por duplicação de agentes.

Cada agente possui:
- identidade operacional;
- conjunto explícito de capacidades;
- distrito;
- prioridade;
- inbox lógico;
- acesso apenas aos recursos necessários;
- saída em envelope padronizado;
- provenance.

## Envelope universal

```json
{
  "event_id": "uuid",
  "topic": "artifact.created",
  "source": "atelier_curator",
  "target": null,
  "correlation_id": "uuid",
  "task_id": "uuid",
  "hops": 3,
  "ttl_seconds": 3600,
  "payload": {},
  "created_at": "ISO-8601"
}
```

## Autocomunicação

A comunicação é indireta e rastreável:

1. agente conclui uma etapa;
2. publica evento;
3. Event Bus persiste;
4. Router identifica capacidades exigidas;
5. Dispatcher cria/ativa próxima tarefa;
6. especialista assume;
7. resultado entra no Archive + provenance;
8. gates decidem se segue adiante.

Isso permite substituir qualquer agente/modelo sem quebrar o fluxo.

## Coordenação horizontal

Especialistas do mesmo nível podem colaborar por capacidades complementares:
- `charcoal_master + tattoo_architect`
- `noir_writer + canon_guard`
- `cinebrain + compute_broker + cinema_qc`
- `product_architect + commerce_guard`

## Coordenação vertical

- Mayor: objetivo global.
- Dispatcher: decomposição e ordem.
- District agent: decisão especializada.
- Subagent/worker: execução atômica.
- Guard: validação independente.
- Archivist: versão, hash e memória.

## Resiliência

- SQLite WAL.
- tarefas idempotentes;
- dedupe por hash;
- leases para impedir execução dupla;
- dead-letter queue;
- retries limitados;
- circuit breaker por integração;
- max_hops;
- TTL;
- nenhum loop infinito;
- estado reconstruível por eventos.

## Integração com HARUM STUDIO OS

O Studio OS continua responsável por produção cinematográfica/ativos.
Swarm City decide **quem** deve agir e **em que sequência**.

`Swarm City → CineBrain / Studio OS → workers → QC → Swarm City → publicação/arquivo`

## Fronteiras

A cidade pode coordenar software e serviços conectados, mas não cria processamento persistente sozinha. Para operar continuamente precisa ser executada em um runtime real (local, GitHub Actions, Vercel, servidor, Colab/Kaggle etc.). Publicação e ações externas permanecem condicionadas a permissões e gates.
