# HARUM CINEMATIC GRID v2

Pipeline open-source para montar microvídeos em cenas maiores para Harum Noir / Arte Harum.

## Princípio

`roteiro -> cena -> shots -> microvídeos -> montagem -> áudio -> QC -> publicação`

Não existe um único gerador para tudo. Cada shot é roteado conforme função, VRAM, licença e consistência de identidade.

## Stack

- FFmpeg: motion em stills, normalização, montagem, áudio e QC.
- LivePortrait: close e microexpressão.
- MuseTalk: lipsync de vídeo existente.
- LTX / LTX-2: image-to-video e geração audiovisual.
- Wan 2.2: I2V/TI2V; 5B para menor barreira.
- HunyuanVideo-1.5: I2V 480p/720p quando houver GPU adequada.
- FramePack: geração progressiva de vídeo.
- SkyReels V3: referência multimodal/múltiplos sujeitos.
- RIFE: interpolação.
- Real-ESRGAN: restauração/upscale.
- WanGP / LightX2V: execução otimizada em hardware limitado.

## Compute sem assinatura

CPU faz toda a pós-produção. GPU gratuita é usada apenas para síntese curta em Colab/Kaggle/Hugging Face ZeroGPU quando disponível.

## Uso

```bash
python tools/harum-cinematic-grid/harum_cinematic.py project.json
```

O projeto JSON define uma sequência de imagens/vídeos. O compilador normaliza tudo para 9:16 CFR, aplica motion/grade/fades, concatena, adiciona ambiente/voz/música e gera QC com ffprobe.

## Gate

`FACE > CABELO > ROUPA > PALETA > MOVIMENTO > VOZ > VERDADE > CTA`

Ativos generativos que falham no gate não entram como Harum Noir oficial.
