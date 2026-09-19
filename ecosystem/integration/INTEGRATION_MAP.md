# HARUM — Integration Map

## 1. Fonte canônica
`CONTEXTO_MESTRE_ARTE_HARUM.md` + `HARUM_NOIR_BIBLIA_CANONICA.md`.

## 2. Coordenação
`ecosystem/swarm/` é a camada oficial de coordenação. Mission Control recebe objetivos, Capability Mesh monta a equipe e o Event Bus conecta agentes, subagentes, Studio OS e integrações.

## 3. Identidade visual
`assets/harum-noir/identity/` define referência fixa. Todo vídeo ou imagem oficial passa pelo gate de consistência.

## 4. Narrativa
Calendário, arcos, captions, commerce map e publication pack alimentam Noir Writer + Canon Guard.

## 5. Produção audiovisual
Swarm City delega ao Cinema District. `cinebrain.py` cria o plano; `harum_router.py` escolhe rota; engines executam; `harum_review.py` e QC validam; `harum_edit.py` monta; `harum_audio_master.py` fecha áudio.

## 6. Produtos
PDFs ficam em `ecosystem/products-pdf/`. Product Architect estrutura; Commerce Guard e Truth Guard bloqueiam alegações ou disponibilidade não validadas.

## 7. Arquivo e memória
Archivist controla inventário, hashes, versões e manifestos. Memory Librarian recupera contexto e relações para qualquer distrito.

## 8. Distribuição
Site Integrator e Channel Router recebem apenas ativos aprovados. Instagram/YouTube/Studio 23 só avançam após gates de identidade, verdade, licença, QC e revisão humana quando aplicável.

## 9. Federação
`FEDERATION_BUS.md` define como runtimes locais, GitHub CI, Vercel, Colab/Kaggle, Studio OS e workers futuros podem anunciar capacidades e cooperar sem compartilhar credenciais.

## 10. Estado
GitHub = código, manifests e arquivo versionado.
Biblioteca = mestres canônicos e mídia.
Airtable = fila/estado/métricas quando conectado.
Hotmart = entrega/venda somente depois de elegibilidade e checkout validados.
