# ARTE HARUM — ESTADO COMPARTILHADO

Atualizado: 2026-09-23

## Regra de retomada

Toda nova instância, chat, Work ou agente que receber `sincronize e continue`, `continue`, `prossiga`, `publique` ou pedido equivalente DEVE, antes de publicar:

1. Ler este arquivo.
2. Ler `HARUM_NOIR/PUBLICATION_LEDGER.json`.
3. Consultar o Instagram conectado via Windsor.ai para posts/reels recentes quando disponível.
4. Comparar o ativo candidato por `source_key`, `adobe_asset_id`, `instagram_media_id`, URL/origem, título e semelhança de composição.
5. Se o ativo já tiver sido publicado em QUALQUER superfície (feed, story, reel, carousel), NÃO reutilizar, exceto quando o usuário pedir explicitamente `reposte`, `republique` ou `use de novo`.
6. Após publicar, registrar imediatamente no ledger antes da próxima peça.

## Regra editorial corrigida

**Publicado uma vez = bloqueado para reutilização visual automática.**

Não importa se a legenda, crop, canal ou contexto narrativo forem diferentes. Reaproveitar a mesma imagem como Story depois de já ter sido Feed conta como repetição e deve ser evitado.

Exceções somente por pedido explícito do usuário.

## Pré-flight obrigatório de publicação

Antes de qualquer `create_story`, `create_image_post`, `create_carousel_post` ou `create_video_post`:

- `CHECK 1 — identidade`: pertence à linha ativa Harum Noir / Arte Harum?
- `CHECK 2 — histórico`: source_key/asset/media já aparece no ledger?
- `CHECK 3 — Instagram`: já aparece no feed/reels consultados via Windsor?
- `CHECK 4 — narrativa`: avança a história em vez de repetir capítulo encerrado?
- `CHECK 5 — verdade`: não apresenta estudo como tattoo executada, sessão real ou produto disponível sem validação?
- `CHECK 6 — registro`: após sucesso, gravar media_id + source_key + data + superfície.

Se CHECK 2 ou CHECK 3 = sim, BLOQUEAR e escolher ativo inédito.

## Linha editorial ativa

Harum Noir — novo ciclo após `Caderno XV: Presença`.

Calendário-base:
- Stories: recorrentes, mas cada quadro deve usar ativo visual inédito.
- Reels: alternar gesto/processo/repertório; não reciclar imagens já usadas em feed/stories sem autorização.
- Feed: espaçado; priorizar peças inéditas e capítulos novos.

## Incidente 2026-09-23

Foram publicadas 12 Stories. Parte da sequência reutilizou imagens que já haviam aparecido no Feed. Isso foi um erro de continuidade: a regra antiga aceitava reaproveitamento com nova função narrativa; a regra foi substituída pela política **NO-REUSE** acima.

Essas peças estão registradas no ledger e não devem aparecer novamente automaticamente.

## Fonte de verdade

- Estado geral: `ARTE_HARUM_ESTADO.md`
- Histórico de publicação/ativos: `HARUM_NOIR/PUBLICATION_LEDGER.json`
- Política anti-duplicação: `HARUM_NOIR/ANTI_DUPLICATION.md`

A fonte de verdade é GitHub + leitura live do Instagram. Memória do chat sozinha NÃO é suficiente para decidir se algo já foi publicado.
