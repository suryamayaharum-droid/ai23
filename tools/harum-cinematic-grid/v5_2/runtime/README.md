# HARUM Runtime Bridge v5.2

Esta camada existe para rodar dentro de uma sessão ativa do ChatGPT usando o runtime local disponível.

Executa diretamente: Python, FFmpeg/ffprobe, edição CPU, movimento determinístico de imagens, compilação de cenas, áudio, QC, hashing/cache, manifests e empacotamento.

Para ações que vivem fora do container — Airtable, GitHub, geração de imagem, voz, publicação ou GPU externa — o runtime emite ações estruturadas em `actions.jsonl`. O assistente despacha essas ações pelos conectores/ferramentas disponíveis ou por um runtime explicitamente autorizado.

O programa não é gravado nos pesos do modelo e não fica rodando permanentemente entre sessões. A integração é operacional: código + estado persistente + conectores, e pode ser invocado novamente quando o runtime estiver disponível.

## Comandos

```bash
python runtime/harum_runtime.py boot
python runtime/harum_runtime.py status
python runtime/harum_runtime.py run-scene examples/project_2317.json
python runtime/harum_runtime.py qc examples/HARUM_NOIR_2317_SCENE.mp4
python runtime/harum_runtime.py emit airtable '{"operation":"sync_runtime"}'
```
