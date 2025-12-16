prudentes tuya all

PROBLEMA
O projeto não consegue buscar automaticamente as entidades (DPs) do Tuya Development Cloud apesar de ter acesso às APIs.
Eu preciso que você corrija/implemente o discovery assim:
1) Obter TODOS os deviceIDs do projeto (sem depender de “devices online” apenas).
2) Para cada deviceID, consultar online/offline e mapear TODAS as entidades/DPs do dispositivo.
3) Para cada entidade, retornar: dpCode, dpId (ou dp_id), tipo (bool/enum/value/string/raw/bitmap/struct/array…), valores/opções (range, min/max/step/unit/scale/maxlen…), e se é controlável (rw/wr) ou apenas leitura (ro).
4) Classificar automaticamente o “tipo de entidade” (ex.: switch, light, fan, cover, climate, sensor, select, number, button, scene, unknown) com um score/confiança e justificativa (heurística baseada nos dpCodes + categoria do device + presença de certos DPs).
5) Gerar uma saída consolidada (JSON) com: projeto → lista de devices → lista de entidades por device.
6) Não quebrar a arquitetura atual: reaproveite cliente HTTP, autenticação e padrões do repositório.

APIs (use estas rotas)
A) Listar devices do projeto (paginado):
   GET /v2.0/cloud/thing/device?page_size=20&last_id=...
   - Colete: id (deviceId), name/customName, category, productId, isOnline, sub, uuid, localKey (se vier), etc.
   - Implemente paginação até não retornar mais resultados.

B) Para cada deviceId:
   1) Especificações com DP ID (dpId):
      GET /v1.1/devices/{device_id}/specifications
      - Parseie “functions” e “status”.
      - ATENÇÃO: a doc fala dp_id, mas respostas podem vir como dpId. Normalize para dpId.
   2) Modelo rico (typeSpec e estrutura completa):
      GET /v2.0/cloud/thing/{device_id}/model
      - O campo result.model vem como STRING JSON. Faça JSON.parse e extraia:
        services[].properties/actions/events
      - Para properties, capture: code, accessMode, typeSpec (enum range, value min/max/step/unit/scale, string maxlen, bitmap labels, struct fields etc), abilityId.
   3) Status atual:
      GET /v1.0/iot-03/devices/{device_id}/status
      - Obtenha code → value atuais para preencher “currentValue”.
   4) (Opcional, mas recomendado) Se device.sub == true ou se for gateway:
      GET /v1.0/iot-03/devices/{device_id}/sub-devices
      - Inclua sub-devices na lista global de deviceIds e processe como devices normais.

O QUE VOCÊ DEVE FAZER NO CÓDIGO (PASSO A PASSO)
1) Inspecione o repositório e identifique onde hoje é feito:
   - autenticação/assinatura (client_id, secret, access_token, região)
   - chamadas para Tuya Cloud
   - geração/listagem atual de “entidades” (provavelmente incompleta)
2) Corrija/implemente um “Discovery Pipeline” único:
   - discoverProjectDevices(): retorna lista completa de devices (paginado)
   - discoverDeviceEntities(deviceId): retorna entidades (merge das 3 fontes: specifications + model + status)
   - mergeSources():
       a) index por dpCode (code)
       b) associe dpId a partir de /specifications
       c) associe typeSpec/accessMode/abilityId a partir do /model
       d) associe currentValue a partir do /status
       e) normalize tipos (Boolean/bool, Enum/enum, Value/value, String/string, Raw/raw, Bitmap/bitmap, Struct/struct, Array/array, Float/Double)
       f) normalize “values” quando vier como string JSON (às vezes “{}”)
3) Classificação automática do “entityType” (Home Assistant-like):
   - Regras heurísticas (exemplos mínimos):
     * LIGHT se existir dpCodes como: bright/brightness, colour/color, temp/colour_temp, work_mode + bright etc.
     * SWITCH se dpCode começar com “switch” (switch, switch_1, switch_led, relay…)
     * COVER se tiver percent_control/percent_state, control (open/close/stop), position…
     * FAN se tiver fan_speed/speed_level + switch_fan
     * CLIMATE se tiver temp_current/temp_set/mode/work_mode, eco/heating/cooling
     * SENSOR se dpCode indicar leitura: temp/humidity/pm25/co2/battery/doorcontact/pir/illumination etc.
     * SELECT se typeSpec.enum com range e não for claramente “mode” de climate/light (ou marcar como select dentro do device)
     * NUMBER se typeSpec.value/float/double com min/max
     * BUTTON se dpCode indicar “reset”, “toggle”, “click”, “alarm_clear” etc (e for write-only)
     * UNKNOWN caso não encaixe.
   - Para cada entidade, retorne:
     entityType, confidence (0..1), reason (texto curto)
4) Saída/Export:
   - Crie um comando/endpoint/rotina executável no repo, por ex:
     * CLI: `npm run tuya:discover` ou `python -m ...`
     * Output em `./artifacts/tuya-entities-map.json`
   - Estrutura sugerida do JSON:
     {
       "generatedAt": "...ISO...",
       "project": { "region": "...", "clientId": "...masked..." },
       "devices": [
         {
           "deviceId": "...",
           "name": "...",
           "category": "...",
           "productId": "...",
           "isOnline": true/false,
           "entities": [
             {
               "dpCode": "...",
               "dpId": 1,
               "abilityId": 102,
               "access": { "read": true, "write": false, "accessMode": "ro|rw|wr" },
               "dpType": "bool|enum|value|string|raw|bitmap|struct|array|float|double|date",
               "typeSpec": { ...normalizado do model... },
               "valuesRaw": "...se existir...",
               "currentValue": ...,
               "entityType": "switch|light|sensor|...",
               "confidence": 0.0,
               "reason": "..."
             }
           ]
         }
       ]
     }
   - Inclua também um resumo no console (tabela/log) com:
     totalDevices, totalEntities, entitiesPorDevice, erros/avisos por device.
5) Robustez:
   - Limite de concorrência (ex.: 3–5 devices em paralelo) + retry com backoff para 429/5xx.
   - Logs de depuração com “requestId/tid” se disponível e com máscara de secrets/tokens.
   - Se /v2.0/cloud/thing/{device_id}/model falhar, continue usando /specifications + /status.
6) Testes:
   - Adicione testes unitários para:
     * paginação do device list (last_id)
     * merge e normalização de dpId/dp_id/dpId
     * parser do model (JSON string → object)
     * heurísticas de classificação (casos de switch/light/sensor/unknown)
   - Use fixtures (JSON) e mocks do HTTP client do próprio repo.

CRITÉRIOS DE ACEITE (Definition of Done)
- Rodando o comando/fluxo de discovery, ele:
  1) lista TODOS os devices do projeto via /v2.0/cloud/thing/device (com paginação)
  2) para cada device, extrai entidades e dpId/dpCode (via /v1.1/devices/{id}/specifications)
  3) enriquece entidades com typeSpec/accessMode (via /v2.0/cloud/thing/{id}/model)
  4) traz currentValue (via /v1.0/iot-03/devices/{id}/status)
  5) gera o JSON final consolidado sem exigir que devices estejam online
  6) não quebra funcionalidades existentes e mantém padrões do repo

IMPORTANTE
- Não exponha client_secret/access_token em logs.
- Reaproveite as estruturas e padrões existentes do repositório (linguagem, lint, logger, http client).
- Se existirem múltiplos módulos de Tuya no repo, centralize o discovery num único serviço e apenas consuma esse serviço onde for necessário.
- Ao final, faça commit/PR com: código, testes, e README curto de como executar o discovery.
