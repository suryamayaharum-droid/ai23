# HARUM SWARM CITY v1

Camada multiagente do ecossistema Arte Harum / HARUM NOIR.

## Objetivo

Coordenar agentes e subagentes por capacidades, eventos e workflows sem acoplar o sistema a um único modelo, provedor ou computador.

A cidade não é uma entidade consciente. É um sistema de software orientado a eventos com:

- registro de agentes e capacidades;
- Event Bus persistente em SQLite;
- tarefas com TTL, prioridade, dependências e deduplicação;
- roteamento por capacidade;
- workflows multiagente;
- comunicação agente→evento→agente;
- provenance e logs;
- gates de cânone, verdade, licença e publicação;
- adaptadores para Cinema, Editorial, Produto, Tattoo, Site, GitHub e distribuição;
- execução local/offline por padrão.

## Distritos

1. **Control Tower** — planejamento, decomposição e saúde da rede.
2. **Atelier** — desenho, carvão, tattoo, anatomia e curadoria visual.
3. **Noir Editorial** — personagem, narrativa, calendário e continuidade.
4. **Cinema** — CineBrain, shot routing, render, áudio, edição e QC.
5. **Products** — PDFs, cursos, catálogo, Hotmart e empacotamento.
6. **Distribution** — site, GitHub, YouTube, Instagram e publicação.
7. **Memory & Archive** — inventário, manifestos, hashes e recuperação.
8. **Governance** — verdade, direitos, segurança, canon lock e publication gate.

## Comunicação nativa

Todo agente publica e consome envelopes de evento.

```
task.created
  ↓
router.assigned
  ↓
agent.started
  ↓
artifact.created
  ↓
review.requested
  ↓
gate.passed | gate.failed
  ↓
task.completed
```

Um agente não chama outro por dependência rígida. Ele publica um evento ou cria uma tarefa com capacidades necessárias. O roteador escolhe o melhor especialista disponível.

## Anti-loop

- `max_hops` padrão: 12
- `ttl_seconds` padrão: 3600
- hash de deduplicação por intenção + payload
- um agente não pode reabrir a mesma tarefa concluída sem versão nova
- falhas repetidas entram em `BLOCKED`, não em retry infinito
- publicação exige gates explícitos

## Execução

```bash
python ecosystem/swarm/harum_swarm.py bootstrap
python ecosystem/swarm/harum_swarm.py seed
python ecosystem/swarm/harum_swarm.py status
python ecosystem/swarm/harum_swarm.py demo
```

Banco padrão: `runtime/harum_swarm.db`.

## Integração

HARUM SWARM CITY fica acima do Studio OS:

`Brief/Story → Swarm City → Workflow/DAG → Studio OS/CineBrain/Workers → Review/Gates → Archive/Distribution`
