Quero que você gere APENAS CÓDIGO (arquivos) de um repositório GitHub completo para a demo do meu TCC.
NÃO gere apresentação, roteiro, “entregáveis”, nem texto acadêmico. Só código + README técnico de execução.

CENÁRIO / REDE (fixo)
- Roteador de borda: TP-Link ER605 V2 (WAN via tethering USB do celular).
- Roteador interno: Deco X60 (usarei só 1 unidade do kit).
- Sub-rede interna: 10.10.10.0/24.
- Home Assistant roda em VirtualBox no notebook, IP fixo: 10.10.10.100.
- Node-RED já existe dentro do Home Assistant (addon). Só subir Node-RED em container se for NECESSÁRIO, como opcional.

OBJETIVO DO REPO (o que precisa existir)
A) Stack Docker (SEM Home Assistant):
- HiveMQ broker em container (porta MQTT 1883; Control Center 8080).
- Um Web App “CodeX/Bootstrap” (frontend bonito) + Node.js (backend) em container:
  - Dashboard web que:
    1) Mostra status do MQTT (conectado/desconectado) + log de mensagens em tempo real (via WebSocket/SSE do Node).
    2) Permite publicar comandos em tópicos MQTT (botões) e ver os acks/status voltando.
    3) Tem páginas: / (dashboard), /devices (tabela), /mqtt (debug), /health (json).
  - Backend Node.js (Express) que:
    - Conecta no MQTT usando mqtt.js.
    - Opcional: chama a API REST do Home Assistant (10.10.10.100) para acionar services (com token em env var), apenas se eu habilitar.
- Opcional (comente no compose): Node-RED container, caso eu não queira usar o do Home Assistant.

B) Integração custom do Home Assistant (instalável via GitHub):
- Pasta: custom_components/prudentes_tuya_all/
- Integração via Config Flow (UI do HA).
- Ela deve usar Tuya Developer Cloud (OpenAPI) e expor TODOS os atributos:
  - Buscar specification do device (status set + instruction set):
    GET /v1.0/iot-03/devices/{device_id}/specification
  - Buscar functions (instruction set simplificado):
    GET /v1.0/iot-03/devices/{device_id}/functions
  - Buscar status atual e detalhes do device:
    GET /v1.0/devices/{device_id}
  - Enviar comandos:
    POST /v1.0/iot-03/devices/{device_id}/commands  body: {"commands":[{"code":"...","value":...}]}
- A integração deve:
  1) Permitir configurar credenciais Tuya (access_id/client_id, access_secret, region/base_url) e uma lista de device_ids (ou uid se você implementar listagem).
  2) Para cada device_id, criar entidades para TODOS os DPs (status codes) — sem “filtrar por tipo” como algumas integrações fazem.
  3) Mapear DP types para plataformas HA quando possível:
     - bool -> switch / binary_sensor (dependendo se writable)
     - enum -> select
     - value (numérico) -> number ou sensor (com min/max/step se disponível)
     - string/json -> sensor (state resumido) + attributes com payload completo
  4) Mesmo quando mapear para switch/number/select, manter atributos extras expostos (raw dp, schema, etc).
  5) Ter um “diagnostic sensor” por device contendo JSON com TODOS os DPs como attributes (para “mostrar tudo” na banca).
  6) Polling com DataUpdateCoordinator (interval configurável nas Options).
  7) UI amigável: nomes melhores (code + nome do device), ícones razoáveis, e Options Flow para:
     - habilitar/desabilitar DPs individualmente
     - renomear DP
     - ajustar polling

IMPORTANTE (sobre inspiração LocalTuya)
- Eu vou te passar um link do repositório base do LocalTuya depois: [LINK_LOCALTUYA_AQUI].
- Por enquanto: implemente do zero com base em boas práticas HA (config entries + coordinator), mas com a mesma “ideia” de entidades por DP.

Demonstração MQTT (obrigatório)
- Defina uma convenção de tópicos:
  - tcc/demo/cmd/{device}/{action}
  - tcc/demo/state/{device}
  - tcc/demo/ack/{device}
  - tcc/demo/log
- O Node.js deve publicar e assinar esses tópicos e exibir na UI.
- Inclua um “demo publisher” (script Node ou container opcional) que publique mensagens simuladas a cada 2s em tcc/demo/log para mostrar o protocolo mesmo sem devices.

ENTREGAS DO CODE (formato)
- Gere uma árvore de arquivos e o conteúdo de CADA arquivo.
- Use headers tipo: “### path/to/file.ext” seguido de um bloco de código.
- Inclua:
  - docker-compose.yml
  - Dockerfile do node app
  - package.json
  - src/server.js, src/mqtt.js, src/ha.js
  - views (Bootstrap/CodeX) e assets mínimos
  - README.md com comandos de execução e variáveis de ambiente
  - custom_components/prudentes_tuya_all/ com:
    - manifest.json
    - __init__.py
    - config_flow.py
    - options_flow (separado ou integrado)
    - coordinator.py
    - platforms: sensor.py, switch.py, number.py, select.py, binary_sensor.py
    - tuya_client.py (assinar requests e token)
    - translations pt-BR/en (mínimo)
- Segurança:
  - Nunca hardcode token/segredo.
  - Use .env.example.
  - README explica onde colar o custom_component no HA (config/custom_components) e como reiniciar.

Restrições
- NÃO inclua Home Assistant no docker-compose.
- Não dependa de internet para a parte MQTT local e UI local.
- A parte Tuya Cloud obviamente depende de internet; deixe isso claro no README.
- Gere código funcional e minimalista (rodável) e com logs.

Use Node 20+ no container do Node.js.

no read-me coloque um tutorial passo a passo clique por clique de como configurar o home assistant jno virtual box e os próximos passos para realizar todas as integrações. quero umswagger documentando as apis e todos os códigos devem utilizar funções em ingles e o metodo cleanCode mas os comentários e documentações devem ser todas em português. utilize como base este projeto "https://github.com/xZetsubou/hass-localtuya" mas melhore ele, crie interfaces melhores para ler dados dele fora do home assistante e para dentro do home assistant deixe ele bem mais amigavel e completo construindo um passo a passo de utilização do novo código gerado que melhorará a integração anterior do XZetsubou.

