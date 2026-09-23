# ARTE HARUM — ESTADO COMPARTILHADO

Atualizado: 2026-09-23

## Regra de retomada

Toda nova instância, chat, Work ou agente que receber `sincronize e continue`, `continue`, `prossiga`, `publique` ou pedido equivalente DEVE, antes de publicar:

1. Ler este arquivo.
2. Ler `HARUM_NOIR/PUBLICATION_LEDGER.json`.
3. Ler `HARUM_NOIR/PUBLISHING_FORMATS.md`.
4. Consultar o Instagram conectado via Windsor.ai para posts/reels recentes quando disponível.
5. Comparar o ativo candidato por `source_key`, `adobe_asset_id`, `instagram_media_id`, URL/origem, título e semelhança de composição.
6. Se o ativo já tiver sido publicado em QUALQUER superfície (feed, story, reel, carousel), NÃO reutilizar, exceto quando o usuário pedir explicitamente `reposte`, `republique` ou `use de novo`.
7. Criar uma versão específica para a superfície de destino antes de publicar.
8. Fazer preview visual final e conferir que não houve distorção, achatamento ou corte indevido.
9. Após publicar, registrar imediatamente no ledger antes da próxima peça.

## Regra editorial corrigida

**Publicado uma vez = bloqueado para reutilização visual automática.**

Não importa se a legenda, crop, canal ou contexto narrativo forem diferentes. Reaproveitar a mesma imagem como Story depois de já ter sido Feed conta como repetição e deve ser evitado.

Exceções somente por pedido explícito do usuário.

## Regra técnica de formato

- Stories: 9:16, preferencialmente 1080×1920, JPEG, com preview visual antes de enviar.
- Feed vertical: 4:5, preferencialmente 1080×1350.
- Reels: 9:16, com capa e primeiro frame conferidos.
- Nunca enviar um arquivo 3:4/4:5/quadrado diretamente para Story.

Detalhes em `HARUM_NOIR/PUBLISHING_FORMATS.md`.

## Pré-flight obrigatório de publicação

Antes de qualquer `create_story`, `create_image_post`, `create_carousel_post` ou `create_video_post`:

- `CHECK 1 — identidade`: pertence à linha ativa Harum Noir / Arte Harum?
- `CHECK 2 — histórico`: source_key/asset/media já aparece no ledger?
- `CHECK 3 — Instagram`: já aparece no feed/reels consultados via Windsor?
- `CHECK 4 — narrativa`: avança a história em vez de repetir capítulo encerrado?
- `CHECK 5 — verdade`: não apresenta estudo como tattoo executada, sessão real ou produto disponível sem validação?
- `CHECK 6 — formato`: arquivo final está na proporção correta da superfície e foi visualmente verificado?
- `CHECK 7 — registro`: após sucesso, gravar media_id + source_key + data + superfície.

Se CHECK 2 ou CHECK 3 = sim, BLOQUEAR e escolher ativo inédito.

## Linha editorial ativa

### Harum Noir — ciclo `Momento Noir`

Série independente do antigo ciclo `Caderno`.

Objetivo: presença diária mais humana e íntima, mostrando vida de atelier, processo, modelo vivo, estudo livre, corpo inteiro, autorretrato, paisagens espontâneas, cafés e desenho de pessoas em situações cotidianas.

Direção visual:
- artista feminina recorrente com aparência consistente;
- cabelo curto/chanel escuro;
- corpo e rosto preservados entre cenas;
- carvão, papel, ateliê realista, luz natural/dourada;
- menos layout artificial, mais fotografia editorial íntima;
- textos humanos, curtos, observacionais, sem tom de manifesto em toda publicação.

Subciclo atual: **modelo vivo feminino**.

Stories corrigidas e publicadas em 9:16:
- 18129042745682740
- 18463368931141526
- 17936837649365679
- 18494550127102858

Esses ativos já estão bloqueados para reutilização automática.

## Incidentes 2026-09-23

### Reuso visual
Foram publicadas 12 Stories. Parte da sequência reutilizou imagens que já haviam aparecido no Feed. Isso foi um erro de continuidade. A política foi substituída por **NO-REUSE**.

### Distorção de Stories
Alguns arquivos foram enviados em proporção inadequada e ficaram distorcidos/cortados. A causa foi publicar arquivo preparado para outra superfície sem normalização para 9:16. A regra agora exige versão específica + preview antes de qualquer publicação.

## Fonte de verdade

- Estado geral: `ARTE_HARUM_ESTADO.md`
- Histórico de publicação/ativos: `HARUM_NOIR/PUBLICATION_LEDGER.json`
- Política anti-duplicação: `HARUM_NOIR/ANTI_DUPLICATION.md`
- Formatos e preflight visual: `HARUM_NOIR/PUBLISHING_FORMATS.md`

A fonte de verdade é GitHub + leitura live do Instagram. Memória do chat sozinha NÃO é suficiente para decidir se algo já foi publicado.
