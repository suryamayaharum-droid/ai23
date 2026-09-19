# ZERO-COST COMPUTE MESH — 2026-09-19

## Rota atual
- **Kaggle**: após 15/09/2026, P100 foi retirado; o acelerador público indicado pelo próprio Kaggle é **T4x2**, duas GPUs de 16 GB. O Harum usa duas lanes de shots dentro da mesma sessão autorizada.
- **Hugging Face ZeroGPU**: free users podem usar Spaces ZeroGPU; conta Free tem cota diária curta. É tratada como burst GPU para um hero shot curto, não render farm.
- **Colab Free**: permanece útil para uso interativo, mas os termos proíbem distributed compute workers no free managed runtime. Por isso o sistema nunca o agenda como worker permanente.
- **GitHub Actions**: standard runners são gratuitos em repositórios públicos. Usamos para CI/QC/post leve, não para abusar do serviço como fazenda de render.
- **CPU**: FFmpeg, ingest, timeline, cor, áudio procedural, QC, cache e compilação ficam fora da GPU.

## 'Hack' legítimo
A multiplicação de capacidade vem de **decompor por planos** e usar cada recurso só no que ele faz bem, não de burlar cota:
`2 T4 Kaggle = duas lanes de microshots`; `ZeroGPU = burst`; `CPU/GitHub = pós`; `Colab = laboratório interativo`.
