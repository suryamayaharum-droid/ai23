# HARUM NOIR — FORMATOS DE PUBLICAÇÃO

Atualizado: 2026-09-23

## Regra central

Nenhum ativo visual deve ser enviado diretamente ao Instagram sem uma versão preparada para a superfície de destino.

### Stories
- Proporção obrigatória: **9:16**.
- Alvo preferencial: **1080 × 1920 px**.
- Formato: JPEG para publicação via Windsor/Instagram.
- Antes de publicar: enquadrar, preservar rosto/corpo/mãos/cavalete, verificar visualmente a versão final e só então enviar.
- Nunca usar imagem 3:4, 4:5 ou quadrada diretamente em `create_story`.

### Feed vertical
- Proporção preferencial: **4:5**.
- Alvo: **1080 × 1350 px**.
- Preservar cabeça, mãos e contexto principal; evitar cortes que mudem anatomia ou pose.

### Feed quadrado
- 1:1 apenas quando a composição pedir.
- Alvo: 1080 × 1080 px.

### Reels
- Vídeo 9:16.
- Alvo: 1080 × 1920 px.
- Conferir capa e primeiro frame antes de publicar.

## Pré-flight visual obrigatório

1. Conferir o ativo-mestre.
2. Criar versão específica da superfície.
3. Verificar proporção.
4. Fazer preview visual da versão final.
5. Conferir se não houve esticamento, achatamento, corte de rosto/mãos/corpo ou deformação.
6. Consultar `PUBLICATION_LEDGER.json` para evitar duplicação.
7. Publicar.
8. Registrar media_id + source_key + superfície + status.

## Incidente de 2026-09-23

Algumas Stories foram enviadas com proporção inadequada e apareceram distorcidas/cortadas. A causa foi o uso de arquivo preparado para outra superfície sem normalização para 9:16.

A partir desta correção, versões 9:16 verificadas visualmente substituem esse comportamento. Stories corrigidas desta sequência:
- 18129042745682740
- 18463368931141526
- 17936837649365679
- 18494550127102858

Essas quatro publicações pertencem ao ciclo **Momento Noir · modelo vivo feminino** e são consideradas bloqueadas para reutilização automática.
