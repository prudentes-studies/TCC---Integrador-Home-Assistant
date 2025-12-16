# Dashboard MQTT CodeX

## Objetivo
UI CodeX/Bootstrap com backend Node.js (imagens Docker `latest`) para monitorar e publicar mensagens MQTT em tópicos `tcc/demo/*`, além de expor Swagger e saúde.

## Pré-requisitos rápidos
- Stack Docker desta raiz ativa (`docker compose up -d --build`).
- Broker MQTT acessível (o serviço `mqtt-broker` sobe HiveMQ CE automaticamente).
- Navegador apontando para `http://localhost:3000`.

## Passo a passo clique a clique (Docker)
1. **Subir os serviços**
   ```bash
   docker compose up -d --build
   docker compose ps
   ```
   Confirme que `mqtt-broker` e `codex-app` estão rodando. O broker usa a tag `hivemq/hivemq-ce:2023.5` para manter o Control Center estável.
2. **Abrir o dashboard**
   - Acesse `http://localhost:3000`.
   - O painel inicial já mostra campos **Device** e **Action**.
3. **Publicar um comando MQTT**
   - Preencha **Device** (ex.: `lamp`) e **Action** (ex.: `on`).
   - Clique em **Publicar**: o backend envia para `tcc/demo/cmd/{device}/{action}`.
   - Observe na área de log SSE as confirmações em `tcc/demo/ack/{device}` e mensagens em `tcc/demo/log` (se o publisher de demo estiver ativo).
4. **Testar via Swagger**
   - Clique em **Swagger** no menu ou acesse `http://localhost:3000/swagger`.
   - Expanda o endpoint de publicação MQTT, clique em **Try it out**, edite o payload e pressione **Execute**. Confira o `curl` gerado e a resposta HTTP.
5. **Explorar o debug MQTT**
   - Acesse a aba **MQTT Debug** no menu.
   - Informe o **Topic** (ex.: `tcc/demo/custom`) e um **Message** JSON, clique em **Publish** e verifique o log de acks.
6. **Visualizar estados do Home Assistant (opcional)**
   - Garanta `ENABLE_HA=true` e um token válido no `.env`.
   - Abra a aba **Devices** e clique em **Atualizar** para listar as entidades retornadas pelo HA.

## Troubleshooting rápido do HiveMQ Control Center (8080)
- Se `http://localhost:8080` mostrar "Internal Error", execute `docker compose pull mqtt-broker` seguido de `docker compose up -d mqtt-broker` e aguarde até 20 segundos para a UI inicializar.
- Verifique conflitos de porta 8080 no host e, se necessário, altere o mapeamento para outra porta livre (ex.: `- "8081:8080"`).
- Consulte `docker compose logs mqtt-broker` para conferir mensagens de erro antes de reabrir a página.

## Tópicos padrão
- `tcc/demo/cmd/{device}/{action}`: comandos.
- `tcc/demo/state/{device}`: estados simulados/retornados.
- `tcc/demo/ack/{device}`: confirmações.
- `tcc/demo/log`: logs gerais (inclui publisher de demo).

## Pontos de extensão
- Adicionar autenticação JWT no Express.
- Incluir cache e replays de mensagens.
- Ajustar UI para múltiplos brokers ou namespaces.
