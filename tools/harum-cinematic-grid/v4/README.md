# HARUM CINEMATIC ECOSYSTEM v4 — Studio Kernel

A v4 transforma o CineBrain em um pequeno sistema operacional editorial.

## Novas peças
- harum_state.py: SQLite transacional para projetos, cenas, shots, renders, assets e eventos.
- harum_cache.py: cache endereçado por SHA-256.
- harum_storygraph.py: valida open loops/payoffs do NOIR LOOP.
- harum_mlt.py: bridge para MLT/melt, editor multitrack headless.
- harum_blender_vse.py: bridge para Blender Video Sequencer em modo headless.
- harum_benchmark.py: VMAF quando disponível; fallback SSIM/PSNR.
- harum_dashboard.py: painel HTML estático sem servidor.
- harum_doctor.py: auditoria de dependências/backends.

## Arquitetura
Editorial → StoryGraph → SceneSpec → State DB → Router → Cache → Workers → QC → Color → Timeline → Master → Publish → Metrics

FFmpeg continua sendo o kernel determinístico. MLT e Blender são backends opcionais. OpenTimelineIO é o formato de interchange e OpenColorIO/ACES é a camada de cor quando instalada.
