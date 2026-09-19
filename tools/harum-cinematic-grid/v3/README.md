# HARUM CINEMATIC ECOSYSTEM v3 — CineBrain

O estúdio é um grafo, não um único modelo.

```
Bíblia/Face Lock
→ CineBrain
→ Scene Graph
→ Shot Router
→ Compute Broker
→ Render Workers
→ QC / Color / Audio
→ OpenTimelineIO / Master
→ Instagram + YouTube
→ Métricas / Memória
```

## Novas camadas
- CineBrain: planeja cena e escolhe engine por tarefa, VRAM e gate de licença.
- Compute Broker: divide a cena em jobs portáteis para CPU, GPU local, Colab, Kaggle ou ZeroGPU, sem contornar quotas.
- Semantic QC: drift de luz/cor e rota opcional DINOv2 para continuidade visual.
- Ingest: PySceneDetect/WhisperX para transformar footage existente em shot library.
- Prefect Core opcional: retries, cache e estados self-hosted.
- OpenColorIO/ACES: gestão de cor.
- VMAF: qualidade perceptual de encode.
- SAM 2 + CoTracker3 + Video Depth Anything: máscaras, tracking e depth.

O master continua determinístico via FFmpeg/Harum CineGrid.
