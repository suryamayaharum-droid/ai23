# HARUM ECOSYSTEM FEDERATION v7

Federação operacional de swarms funcionais para administrar o ecossistema Arte Harum.

- 16 swarms × 6 agentes = 96 agentes funcionais.
- SQLite + event bus + fila de ações externas.
- Execução paralela de auditorias e tarefas locais.
- Ações externas somente via conector/runtime autorizado.
- Gates: verdade, custo, licença, identidade, segurança e confirmação de publicação.

Os agentes são papéis de software coordenados; não são consciências independentes.

```bash
python tools/harum-federation-v7/harum_federation.py boot
python tools/harum-federation-v7/harum_federation.py mission "Auditar e administrar o ecossistema" --id ecosystem-audit-v7
python tools/harum-federation-v7/harum_federation.py status
```
