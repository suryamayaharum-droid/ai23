# HARUM ORGANISM — Airtable / GitHub / Vercel Bridge

## Papel de cada camada

- **Airtable Editorial OS**: blackboard persistente e humano-legível. A cidade macroscópica v8 vive aqui: 18 distritos e 72 swarms.
- **GitHub `harum-archive`**: DNA do organismo. Código, configurações, testes, event schema, snapshots e histórico.
- **HARUM Swarm runtime**: células microscópicas de coordenação e guardas transversais.
- **GitHub Actions**: marca-passo gratuito do organismo; executa pulso, homeostase, testes e snapshot operacional.
- **Vercel**: camada candidata de API/dashboard sempre online. Conector disponível; nenhuma credencial é colocada no repositório.
- **ChatGPT connectors**: ponte autorizada para Airtable, GitHub, Vercel, Adobe, ElevenLabs, HeyGen, Windsor.ai, Drive e outros órgãos.

## Holografia operacional

“Holográfico” aqui significa que cada célula recebe um pacote compacto com:
1. sua função local;
2. digest global;
3. mapa de 18 distritos/72 swarms;
4. recursos disponíveis;
5. missões ativas;
6. regras invariantes.

Isso permite roteamento e recuperação sem depender de uma chamada direta ao Mayor para cada decisão.

## Sincronização

Estado local usa SQLite/WAL + fatos imutáveis + relógio lógico por célula. O merge é CRDT-inspired: fatos são unidos por ID e a visão materializada converge deterministicamente.

Airtable contém duas tabelas de ponte:
- **Organism State** — estado/holograma/heartbeat.
- **Organism Bus** — envelopes de eventos inter-runtime.

Nenhuma tabela deve receber tokens, cookies, senhas ou segredos.

## Limite real

Conectores ChatGPT não são bibliotecas Python que um GitHub Action pode chamar sozinho. Portanto:
- GitHub Actions executa o núcleo determinístico local;
- ChatGPT atua como bridge quando um conector autenticado é necessário;
- Vercel pode futuramente hospedar API pública/privada se criarmos uma implantação dedicada.
