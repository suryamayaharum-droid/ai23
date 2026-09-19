# HARUM NOIR — Zero Cost Studio v1
Pipeline sem assinatura para produzir Shorts da Harum Noir.

- FFmpeg/CPU: sempre funciona.
- LivePortrait: preserva identidade em closes.
- LTX-Video 2B distilled: image-to-video quando o Colab fornecer GPU.
- Piper pt-BR: voz local gratuita.
- Google Drive: arquivo mestre.
- YouTube Data API: publicação opcional via OAuth.

O Colab gratuito não garante GPU, por isso a rota CPU é o fallback permanente.