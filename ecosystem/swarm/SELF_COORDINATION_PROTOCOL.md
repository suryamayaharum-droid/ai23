# SWARM SELF-COORDINATION PROTOCOL v1

## Regra de operação
Agentes não duplicam trabalho por impulso. Cada tarefa nasce com intenção, capacidades exigidas, correlation_id, TTL e max_hops.

## Handoff
Um agente conclui sua parte e publica o resultado. A etapa seguinte é ativada pelo grafo de workflow e roteada pelo conjunto de capacidades.

## Cruzamento de habilidades
Quando uma tarefa exige capacidades que nenhum agente possui sozinho, o Mayor decompõe em subetapas menores. Cada subetapa recebe um especialista e mantém o mesmo correlation_id.

## Memória
O Archivist registra artefato, versão, hash, origem e relação com tarefas. O Memory Librarian transforma isso em contexto recuperável para os próximos agentes.

## Guardas independentes
Canon Guard, Truth Guard, License Guard e Publication Guard não são subordinados ao agente criador da peça. Eles podem bloquear a cadeia.

## Recuperação
- falha transitória: retry limitado;
- falha repetida: dead-letter;
- integração indisponível: WAITING_EXTERNAL;
- TTL vencido: dead-letter;
- loop: bloqueio por max_hops;
- duplicação: hash de dedupe.

## Autonomia controlada
O sistema pode escolher rota, especialista, ordem e recuperação dentro das políticas cadastradas. Ações externas sensíveis e publicação oficial exigem permissões reais e, quando configurado, revisão humana.
