# Free Compute Strategy

- **CPU**: FFmpeg, composição, áudio, legendas, QC, proxies.
- **Kaggle**: GPU gratuita sujeita a fila/disponibilidade; boa rota para notebooks que caibam no hardware disponível.
- **Google Colab Free**: GPU gratuita possível, mas não garantida e com limites dinâmicos; usar de forma interativa, não como worker distribuído.
- **Hugging Face ZeroGPU**: contas Free elegíveis podem hospedar até 2 Spaces ZeroGPU; quota diária gratuita limitada.

O aumento de throughput vem da divisão por shots independentes, não de tentar contornar cotas.
