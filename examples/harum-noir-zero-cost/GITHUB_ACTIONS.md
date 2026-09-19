# GitHub Actions — produção sem assinatura

O workflow `.github/workflows/harum-noir-zero-cost-short.yml` transforma uma imagem em Short 9:16 usando somente runner padrão, FFmpeg e Piper pt-BR.

## Como rodar
1. Abra **Actions** no repositório.
2. Escolha **Harum Noir — Zero Cost Short**.
3. Toque em **Run workflow**.
4. Cole uma URL pública de imagem aprovada (opcional).
5. Ajuste o roteiro.
6. Ao concluir, baixe o MP4 em **Artifacts**.

Sem URL de imagem, o workflow produz uma abertura abstrata 23:17 em carbono/marfim/ouro. Isso serve como fallback editorial e teste de pipeline.

## Por que existe
A produção básica deixa de depender de editor pago ou GPU. Vídeo gerativo continua opcional via LTX no Colab; o GitHub Actions garante um caminho CPU para publicação recorrente.
