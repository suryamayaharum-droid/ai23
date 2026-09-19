# HARUM FEDERATION BUS v1

## Objetivo

Permitir que vários runtimes HARUM cooperem sem transformar todos em um processo monolítico.

## Nós possíveis

- GitHub / CI
- Vercel
- execução local
- Colab/Kaggle
- Studio OS
- CineBrain
- workers de render
- indexadores de Biblioteca
- conectores autorizados

## Contrato

Cada nó implementa quatro operações lógicas:

1. `announce(capabilities, health)`
2. `pull(task_filter)`
3. `push(result, provenance)`
4. `heartbeat(load, limits)`

O barramento central armazena apenas envelopes e metadados. Arquivos grandes permanecem no Asset Store e são referenciados por URI/hash.

## Regras

- nenhum nó pode se declarar com capacidades que não possui;
- nenhuma credencial é propagada pelo Event Bus;
- cada integração mantém seu próprio token/permissão;
- falha de um nó não paralisa a cidade;
- quotas de provedores são respeitadas;
- resultados são versionados;
- publication gates continuam independentes.

## URI de ativo

`harum://<project>/<kind>/<name>?v=<version>&sha256=<hash>`

## Topologia

```
                  +----------------+
                  |  CONTROL TOWER |
                  +-------+--------+
                          |
                    Event / Task Bus
                          |
       +------------------+------------------+
       |                  |                  |
   ATELIER            CINEMA OS          PRODUCTS
       |                  |                  |
  workers/art        render/edit        pdf/course
       +------------------+------------------+
                          |
                    GOVERNANCE
                          |
                 ARCHIVE / DISTRIBUTION
```

A federação permite crescimento horizontal: novos nós entram anunciando capacidades, sem exigir alteração do núcleo.
