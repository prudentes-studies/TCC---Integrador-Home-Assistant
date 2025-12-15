# Dashboard MQTT CodeX

## Objetivo
UI CodeX/Bootstrap com backend Node.js 20 para monitorar e publicar mensagens MQTT em tópicos `tcc/demo/*`, além de expor Swagger e saúde.

## Entradas
- Variáveis de ambiente (.env) descritas na raiz.
- Broker MQTT acessível (HiveMQ CE pelo compose).

## Como usar
1. Suba a stack `docker compose up -d --build`.
2. Acesse http://localhost:3000 e abra `/swagger` para testar as APIs.
3. Use o formulário da home para publicar em `tcc/demo/cmd/{device}/{action}` e veja acks/logs em tempo real.
4. Abra `/devices` para inspecionar estados do Home Assistant (se habilitado).

## Tópicos
- `tcc/demo/cmd/{device}/{action}`: comandos.
- `tcc/demo/state/{device}`: estados simulados/retornados.
- `tcc/demo/ack/{device}`: confirmações.
- `tcc/demo/log`: logs gerais (inclui publisher de demo).

## Pontos de extensão
- Adicionar autenticação JWT no Express.
- Incluir cache e replays de mensagens.
- Ajustar UI para múltiplos brokers ou namespaces.
