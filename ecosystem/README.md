# HARUM / HARUM NOIR — Ecosystem Repository

Branch dedicada: `harum-archive`.

Este espaço consolida o ecossistema Arte Harum / HARUM NOIR sem interferir na `main`.

## Estrutura

- `assets/harum-noir/` — identidade, editorial, carvão e arquivo visual bruto.
- `ecosystem/programs/source/` — código-fonte executável e notebooks.
- `ecosystem/programs/releases/` — pacotes ZIP versionados e releases técnicos.
- `ecosystem/docs/` — documentação canônica, operação, Studio 23, Hotmart e publicação.
- `ecosystem/products-pdf/` — PDFs de produto, formação, pesquisa e mapas.
- `ecosystem/swarm/` — HARUM Swarm City: agentes, subagentes, Event Bus, Capability Mesh, Mission Control e federação.
- `ecosystem/integration/` — manifestos e mapas que conectam as camadas.

## Fluxo principal

`Brief / Bíblia / Face Lock → Swarm City → CineBrain / Studio OS → Router → Workers → QC/Gates → Edit/Master → Archive → Distribuição → Métricas/Memória`

## Coordenação multiagente

Swarm City funciona como camada de coordenação do ecossistema:

- 8 distritos;
- agentes persistentes especializados;
- subagentes efêmeros com TTL e escopo;
- comunicação orientada a eventos;
- roteamento por capacidades;
- montagem automática de equipes multiagente;
- retry limitado, dead-letter, dedupe e max_hops;
- gates independentes de cânone, verdade, licença e publicação.

## Marcas e funções

- Arte Harum — marca-mãe e linguagem autoral.
- Tattoo Studio 23 — atendimento e tatuagem.
- Método Harum — formação e mentoria.
- Harum Noir — persona editorial e selo narrativo.
- 1001 Noites com Harum — continuidade editorial e audiovisual.

## Regras de operação

1. preservar identidade visual e FACE LOCK;
2. não inventar fatos, clientes, depoimentos ou disponibilidade;
3. publicação e venda só avançam depois de gates reais;
4. programas devem funcionar com rota gratuita/fallback quando possível;
5. cada ativo deve registrar origem, papel, estado e dependências;
6. preservar mestres e versões anteriores antes de substituir qualquer coisa;
7. novos agentes entram por capacidades, não por duplicação de função;
8. nenhum segredo/credencial trafega pelo Event Bus.

Consulte `ecosystem/integration/ECOSYSTEM_MANIFEST.json`, `ecosystem/integration/INTEGRATION_MAP.md` e `ecosystem/swarm/README.md`.
