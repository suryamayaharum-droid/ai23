# HARUM STUDIO OS v4 — “Nossa Hollywood”

Um **microestúdio cinematográfico software-defined** para Arte Harum / Harum Noir.

Ele não é um único gerador. É uma fábrica em departamentos, com estado, ativos, shots, jobs, workers, revisão, provenance, QC e distribuição.

## Núcleo

- SQLite Production DB — projects → sequences → scenes → shots → tasks → versions → reviews.
- CineGraph — DAG de produção por plano.
- Scheduler — capability/VRAM-aware.
- Event Bus — toda mudança importante vira evento.
- Asset URIs — `harum://project/kind/name?v=N`.
- Provenance — SHA-256 de entradas/saídas + engines/licenças.
- Publication Gates — só deixa passar asset com licença/QC/canon/truth aprovados.
- Review/Dailies — contact sheet e pacote de revisão.
- Telemetry — JSONL de spans/erros/tempo.
- Plugin SDK — departamentos e engines podem crescer sem editar o núcleo.
- Bridges — OpenCue, Ray, OpenAssetIO, Kitsu, AYON e OpenUSD.

## Quickstart

```bash
python -m harumstudio.cli bootstrap --db runtime/studio.db
python -m harumstudio.cli status --db runtime/studio.db
python -m harumstudio.cli dispatch --db runtime/studio.db
```

O scheduler **não burla cotas** e só usa workers registrados/autorizados.

## Arquitetura

`Story → CineGraph → DB/EventBus → Scheduler → Workers → Assets/Versions → Review → QC → Provenance → Master → Distribution`

O objetivo é escalar do Short para episódio sem perder identidade nem capacidade de reconstruir qualquer master.
