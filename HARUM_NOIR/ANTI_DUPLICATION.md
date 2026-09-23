# HARUM NOIR — ANTI-DUPLICATION PROTOCOL

## Objetivo
Impedir que outra instância, chat ou agente publique novamente um visual já utilizado.

## Regra principal

`VISUAL_USED_ONCE = LOCKED`

Um ativo visual usado em Feed, Story, Reel ou Carousel fica bloqueado para reutilização automática em qualquer outra superfície.

### Reutilização só é permitida se:
- o usuário pedir explicitamente repost/republicação/reuso;
- ou houver uma nova obra derivada materialmente diferente, aprovada como nova peça.

Trocar legenda, crop, ordem, canal ou CTA NÃO transforma o mesmo ativo em peça nova.

## Chave de deduplicação

Cada publicação deve registrar o máximo possível dos campos abaixo:

- `source_key`: identificador canônico criado por nós;
- `adobe_asset_id`: URN quando vier do Creative Cloud;
- `instagram_source_media_id`: quando um Story reaproveita visual previamente publicado no Instagram;
- `published_media_id`: ID devolvido pelo Instagram para a nova publicação;
- `source_url_fingerprint`: URL/origem sem depender de parâmetros temporários;
- `title_or_chapter`;
- `surface`: feed/story/reel/carousel;
- `published_at`;
- `status`.

Se qualquer chave forte coincidir, tratar como duplicata.

## Preflight universal

Antes de publicar:

1. Ler `../ARTE_HARUM_ESTADO.md`.
2. Ler `PUBLICATION_LEDGER.json`.
3. Consultar Windsor Instagram para Feed/Reels recentes.
4. Se for imagem da Adobe, comparar `adobe_asset_id`.
5. Se for mídia já existente do Instagram, comparar o `instagram_source_media_id`.
6. Se houver dúvida visual, NÃO publicar até escolher outro ativo.
7. Publicar uma peça.
8. Registrar o resultado no ledger.
9. Só então avançar para a próxima.

## Continuidade entre instâncias

Uma nova instância não deve confiar em frases como “acho que essa ainda não foi”. Ela deve verificar o ledger + Instagram live.

Palavra-chave operacional: **sincronize e continue**.

Ao recebê-la, a instância deve sincronizar antes de produzir/publicar.

## Incidente de referência

Em 2026-09-23, parte de uma sequência de 12 Stories reutilizou imagens de capítulos já publicados no Feed. Isso não deve ocorrer novamente. O incidente está preservado no ledger para aprendizado e bloqueio futuro.
