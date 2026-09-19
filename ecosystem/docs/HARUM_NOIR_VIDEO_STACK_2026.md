# HARUM NOIR — VIDEO STACK 2026

## Objetivo
Manter a mesma identidade visual da Harum Noir enquanto distribuímos funções entre ferramentas diferentes.

## Stack recomendado

### 1. Gemini Omni — estação criativa multimodal
**Função:** gerar/editar vídeos a partir de texto + FACE LOCK + vídeo de referência.
**Melhor para:** cenas rápidas de rotina, reedição conversacional, mistura de imagem e vídeo.
**Regra:** anexar FACE LOCK em toda geração oficial.

### 2. Google Colab + LTX-Video 2B — laboratório open-source reproduzível
**Função:** image-to-video com seed, resolução e frames controlados.
**Melhor para:** ateliê, espelho, desenho, cidade, parede, objetos.
**Vantagem:** não depende de watermark de editor comercial; pipeline pode ser versionado.
**Perfil de GPU:** usar 2B para VRAM leve; 13B/LTX-2 apenas quando houver GPU mais forte.

### 3. LivePortrait — identidade facial e microexpressão
**Função:** animar o FACE LOCK com um driving video.
**Melhor para:** close, fala, respiração, olhar e microgestos.
**Limite:** não cria rotina/cenário do zero; precisa de movimento de referência.

### 4. ComfyUI + Wan2.2 Animate/VACE — controle corporal avançado
**Função:** movimento guiado por pose/face e substituição de personagem.
**Melhor para:** cenas full-body e consistência de movimento.
**Custo:** 14B é pesado; priorizar L4/A100/24GB+ ou cloud/paid runtime.

### 5. InVideo Agent — montagem editorial
**Função:** roteirizar, organizar capítulos, montar vídeos e versões.
**Regra:** não decidir identidade; recebe FACE LOCK + Bíblia Noir.

### 6. ElevenLabs / voz
**Função:** VOICE LOCK e narração.
**Estado:** VOICE LOCK técnico definido para o próximo ciclo: ElevenLabs `Fabi | Portuguese (BR) | Female` (`e06XicPETIbfUaeHM9zH`) com `eleven_v3`; primeiro take de 13,6 s concluído em 2026-09-19.

## Política de roteamento
- close falado -> LivePortrait + voz
- rotina gerativa -> Gemini Omni ou LTX
- full body guiado -> Wan Animate
- montagem de capítulos -> InVideo
- publicação -> Instagram conectado após gate

## Gate
`FACE > CABELO > ROUPA > PALETA > MOVIMENTO > VOZ > VERDADE > CTA`
