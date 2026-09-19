# HARUM CINEMATIC ECOSYSTEM v3 — CINEBRAIN

## Princípio central

Não existe um único gerador que seja o “estúdio”. O estúdio é o **grafo**.

`Bíblia/Face Lock → CineBrain → Scene Graph → Shot Router → Compute Broker → Render Workers → QC → Color → Audio → OTIO/Edit → Master → Distribuição → Métricas → Memória`

## Camadas fundidas

### 1. Cérebro editorial
- Bíblia Harum Noir
- NOIR LOOP
- calendário/Airtable
- continuity memory por cena

### 2. CineBrain
- `cinebrain.py`
- cria Scene Graph
- escolhe engine por tarefa, VRAM e gate de licença
- quebra a cena em jobs reproduzíveis

### 3. Workers
- CPU: FFmpeg, QC, áudio, legendas, ingest, timeline
- GPU local/ComfyUI
- Colab Free / Kaggle / HF ZeroGPU como runtimes autorizados e oportunistas
- nunca contornar limites de provedor

### 4. Análise e controle
- PySceneDetect para cortes
- Video Depth Anything para depth
- SAM 2 para máscaras
- CoTracker3 para tracking
- DINOv2 como feature backbone opcional para continuidade visual
- VMAF para comparação de encode
- OpenColorIO/ACES para normalização de cor

### 5. Síntese
- FramePack: vídeo progressivo/VRAM baixa
- Wan2.2 + LightX2V/WanGP: I2V/T2V e redução de custo computacional
- HunyuanVideo-1.5 distilled: I2V rápido
- LTX-2: áudio+vídeo/keyframes/extension
- SkyReels V3: multi-reference e áudio guiado
- MuseTalk: lipsync
- LivePortrait: microexpressão/portrait motion, sob gate de licença

### 6. Editorial e pós
- FFmpeg master
- OpenTimelineIO
- WhisperX para palavra-tempo/legendas quando necessário
- OpenColorIO/ACES
- RIFE / Real-ESRGAN opcionais

### 7. Orquestração
- `harum_compute_broker.py`: job bundles portáteis
- `harum_prefect_flow.py`: Prefect Core opcional e self-hosted
- GitHub: código/manifests/CI
- Airtable: fila, estado, métricas
- Library: ativos canônicos e masters

## Estado da arte para o Harum

O ganho mais importante não é “ter mais GPU”; é **não desperdiçar GPU**:
- identidade e enquadramento aprovados ficam em stills;
- gerativo é usado somente nos planos que precisam movimento real;
- tracking/depth/segmentation controlam pós;
- jobs são pequenos, regeneráveis e cacheáveis;
- o master é montado deterministicamente;
- licença e QC são parte do roteamento.
