# HARUM NOIR — VIDEO SKILL / CREW OPERACIONAL

**Status:** habilidade operacional do ecossistema Arte Harum  
**Versão:** 1.0 — 2026-09-19

## Fonte de verdade
- `/HARUM NOIR/HARUM_NOIR_BIBLIA_CANONICA.md`
- `/HARUM NOIR/HARUM_NOIR_FACE_LOCK_CLEAN_v1.png`
- `/HARUM NOIR/HARUM_NOIR_CANONICA_STORIES.png`
- `/HARUM NOIR/HARUM_NOIR_ENGINE.json`

## InVideo
Agente/workspace:
https://ai.invideo.io/workspace/7be995f1-be5d-4d44-b3a2-99bdf551b499/v45-copilot/agents-models/09e21c86-2b88-41d2-8ce4-d956d72bcfb9/agent/f64dd3ae-6e06-45a6-b7ad-c62cad86e253

O InVideo deve receber a personagem já definida. Ele não decide rosto, cabelo, roupa-base ou paleta.

## Crew
1. **NOIR PRODUCER** — segura Bíblia, produto e continuidade.
2. **NOIR WRITER** — escreve em primeira pessoa ficcional/editorial com NOIR LOOP.
3. **NOIR STORYBOARD** — 3–7 planos, cada plano com ação concreta.
4. **NOIR CHARACTER GUARD** — compara toda imagem com FACE LOCK.
5. **NOIR DOP** — luz lateral, carbono/grafite/marfim/ouro, câmera íntima.
6. **NOIR SOUND** — VOICE LOCK: ElevenLabs Fabi (`e06XicPETIbfUaeHM9zH`) + `eleven_v3`, pt-BR íntimo/baixo/natural + ambiente discreto.
7. **NOIR EDITOR** — ritmo, respiro, silêncio, cortes por gesto.
8. **NOIR CHECKER** — não deixa publicar se houver face drift ou fato inventado.

## Prompt de produção
IDENTITY LOCK:
Use exactly the same woman as the Harum Noir FACE LOCK reference. Same adult age, same face shape, same eyes, same nose, same lips, same black chin-length bob haircut. Identity must not drift.

WARDROBE:
Matte black minimal clothing, one subtle aged-gold detail. No logos, no bright color, no trend-fashion changes.

WORLD:
Intimate nocturnal art atelier; charcoal, heavyweight ivory paper, mirrors, books, sculpture fragments, tape, coffee, graphite dust, black cat when narratively relevant.

CAMERA:
Quiet documentary intimacy, natural 50mm feeling, lateral chiaroscuro, small handheld movement, close details, no influencer posing.

PALETTE:
#0B0B0B, #242424, #EEE8DC, #B58A3A; rare #3A171B.

NEGATIVE:
No face change, no generic influencer, no glossy luxury, no corporate presenter, no exaggerated smile, no bright set, no sexualized posing, no fake biography.

## Roteiro curto
`objeto → pensamento → gesto → mudança → resíduo`

Cada vídeo deve:
- pagar a promessa em 1–3 capítulos;
- mostrar processo real ou ficcional claramente editorial;
- terminar com um gesto/frase que puxa naturalmente o próximo.

## Venda dos PDFs
Noir não interrompe a história para “fazer propaganda”.
Ela mostra o problema, a página, o gesto e só então convida.

CTA quando checkout ainda não validado:
- “eu deixei isso organizado no caderno.”
- “vou abrir esse material quando estiver pronto.”
- “acompanha por aqui.”

CTA quando checkout estiver validado:
- “o caderno completo está no link.”
- “se quiser fazer comigo, ele está disponível.”

## Publicação
Canal conectado: `@a_maior_maravilha_da_natureza`.

Antes de publicar:
`FACE → CABELO → ROUPA → PALETA → VOZ → VERDADE → NOVIDADE → CTA`.
Falhou qualquer item: não publicar como Harum Noir.

## Video Router 2026

### Gemini Omni
Usar para cenas multimodais e edição conversacional. Sempre enviar FACE LOCK.

### Colab/LTX
Usar `HARUM_NOIR_COLAB_VIDEO_LAB.ipynb` para cenas gerativas reproduzíveis. Seed é parte do registro de produção.

### LivePortrait
Usar para close, fala e microexpressão. Source = FACE LOCK; driving video = movimento.

### Wan Animate/VACE
Usar apenas quando houver GPU suficiente e necessidade de corpo/movimento controlado.

### Regra
Nenhuma ferramenta externa pode promover um resultado a “Harum Noir oficial” se o rosto divergir do FACE LOCK.
