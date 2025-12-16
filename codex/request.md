Você é um engenheiro de software senior com foco em integrações IoT (Tuya OpenAPI) + Home Assistant.

Tarefa: corrigir e evoluir o repositório “prudentes tuya-all” para que ele consiga descobrir automaticamente TODAS as entidades (DPs) de TODOS os devices de um projeto na Tuya Development Cloud, incluindo devices online e offline, e produzir um mapeamento rico (device -> entidades -> tipo sugerido no Home Assistant + opções/ranges).

Contexto / problema atual:
- O projeto já consegue autenticar e acessar APIs, mas não está conseguindo “buscar entidades automaticamente”.
- Quero um fluxo de discovery: Projeto -> Lista completa de devices (device_id) -> Para cada device_id: obter DPs/propriedades + specification -> consolidar e classificar entidades.
- Entidades na Tuya são DPs (dp_id, code, type, value) e também aparecem na specification (functions/status com “values” e “range/min/max/step”).

APIs obrigatórias a usar (base URL deve ser configurável por região; ex.: openapi.tuyaus.com):
1) Listar categorias (para mapear category code -> name):
   GET /v1.0/iot-03/device-categories
2) Listar devices do projeto (com paginação por last_row_key) e pegar TODOS os device IDs (online e offline):
   GET /v1.3/iot-03/devices
   - use paginação: last_row_key + page_size (max 200)
   - garantir que realmente varre tudo até has_more=false
3) Para cada device_id, obter a “foto” das properties (dp_id, code, type, value):
   GET /v2.0/cloud/thing/{device_id}/shadow/properties
4) Para cada device_id, obter specification para saber:
   - category do device
   - functions + status (code, name, type, values/desc com range/min/max/step)
   GET /v1.0/iot-03/devices/{device_id}/specification

Referência de endpoints da Tuya (não inventar endpoints; seguir docs):
- “Get Device List” = GET /v1.3/iot-03/devices (retorna id, name, category, online, local_key, etc e paginação com last_row_key). 
- “Get the specifications and properties of the device” = GET /v1.0/iot-03/devices/{device_id}/specification.
- “Get Category List” = GET /v1.0/iot-03/device-categories.
(essas referências estão na documentação oficial da Tuya).

Assinatura e autenticação (CRÍTICO):
- Implementar corretamente o signing HMAC-SHA256 exigido pela Tuya OpenAPI (headers sign_method, client_id, t, sign, access_token quando aplicável).
- NÃO hardcodar segredos/tokens no código nem commitar credenciais.
- Colocar configuração via ENV:
  TUYA_BASE_URL
  TUYA_CLIENT_ID
  TUYA_CLIENT_SECRET
  TUYA_ACCESS_TOKEN (opcional se houver fluxo de token)
  TUYA_REFRESH_TOKEN (se aplicável)
- Implementar renovação de token quando receber 401/invalid token.
- Implementar retry com backoff para 429/5xx.

Saída desejada (artefato do discovery):
- Gerar um JSON único (ex.: output/tuya_inventory.json) com estrutura:
  {
    "project": { "source_type": "...", "source_id": "...", "fetched_at": "...", "region": "..." },
    "categories": { "<code>": "<name>" },
    "devices": [
      {
        "device_id": "...",
        "name": "...",
        "category": "dj",
        "category_name": "...",
        "online": true/false,
        "product_id": "...",
        "entities": [
          {
            "entity_id": "<device_id>__<dp_code_or_dp_id>",
            "dp_id": 20,
            "dp_code": "switch_led",
            "tuya_type": "bool|enum|value|string|raw|json",
            "current_value": <...>,
            "spec": {
              "name": "...",
              "type": "Boolean|Enum|Integer|Json|Raw|String",
              "values": { ...parsed... },
              "range": [...], "min": ..., "max": ..., "step": ..., "scale": ...
            },
            "ha": {
              "suggested_platform": "light|switch|sensor|select|number|cover|climate|fan|binary_sensor|button|unknown",
              "suggested_device_class": "...|null",
              "suggested_unit_of_measurement": "...|null",
              "features": ["brightness","color_temp","hs_color","effect","preset_mode", ...],
              "confidence": 0.0-1.0,
              "reason": ["matched hass-localtuya mapping for category dj", "dp_code contains 'bright'", ...]
            }
          }
        ]
      }
    ]
  }

Classificação para Home Assistant (o que mais importa):
- Implementar um classificador “best effort” com:
  1) Regras determinísticas por dp_code (exemplos):
     - códigos contendo "switch", "relay", "outlet" => switch (exceto quando parte de light)
     - "work_mode" (enum) => select (ou parte de light)
     - "bright", "brightness" (value/int) => number (ou parte de light)
     - "temp_value", "colour_temp" => number (ou parte de light)
     - "colour_data", "colour_data_v2" => atributo de light (hs_color)
     - "scene_data", "scene_data_v2" => effect/preset (light) se houver range/estrutura conhecida; senão unknown/string
     - "countdown" => number (segundos) ou sensor; marcar unit “s”
     - sensores: "temp", "humidity", "co2", "pm25", "voc", "battery" => sensor com device_class e unidade quando possível
  2) Agrupamento por “device entity composition”:
     - Ex.: um device category “dj” (luz) deve resultar em 1 entidade light principal,
       agrupando DPs: switch_led + bright_value(_v2) + temp_value(_v2) + work_mode + colour_data(_v2) + scene_data(_v2) + music_data etc.
     - Se existirem múltiplos canais (switch_1, switch_2…), gerar múltiplas entidades.
  3) “Unknown fallback”:
     - Se não conseguir classificar com confiança, manter suggested_platform="unknown" e registrar reason.

Integração com hass-localtuya (xZetsubou) — OBRIGATÓRIO:
- Quero que você aproveite o modelo do hass-localtuya para tornar o mapeamento mais forte e cobrir mais casos.
- O hass-localtuya documenta que o auto-configure se baseia em “DP code” + “Device Category” e usa dados armazenados em `/localtuya/core/ha_entities`, com dicts por plataforma (SWITCHES/COVERS/etc) e um DPCode class em base.py.
- Implementar no prudentes tuya-all uma camada “localtuya_knowledge” com duas opções:
  A) (Preferida) importar as tabelas do hass-localtuya como submódulo/vendor e ler os dicts de ha_entities (sem depender do Home Assistant runtime). Pode ser via:
     - copiar os arquivos relevantes para `vendor/hass_localtuya/` e manter atualização documentada; OU
     - adicionar como git submodule e extrair dados em build-time.
  B) (Fallback) manter uma versão exportada das tabelas em JSON gerada a partir do hass-localtuya (ex.: scripts/extract_localtuya_mappings.py).
- O classificador deve:
  - primeiro tentar mapear via (category -> possíveis entidades) do hass-localtuya
  - depois aplicar heurísticas por dp_code
  - por último fallback unknown.
- Também incorporar o comportamento citado no hass-localtuya de “pegar o primeiro DP disponível” para configs alternativas (ex.: current_position_dp pode aceitar lista de códigos e usar o primeiro encontrado).

Implementação (passos objetivos):
1) Localizar no código atual onde o discovery falha. Corrigir para:
   - sempre chamar GET /v1.3/iot-03/devices e paginar até obter todos os device_ids.
   - não depender do device estar online para entrar no inventário.
2) Implementar um TuyaCloudClient robusto:
   - método request() que assina corretamente
   - logs detalhados (sem vazar segredos)
   - retry/backoff e refresh token.
3) Implementar o pipeline:
   - fetch_categories()
   - fetch_all_devices()
   - para cada device:
     - fetch_specification(device_id)
     - fetch_shadow_properties(device_id)
     - merge_spec_and_shadow()
     - classify_entities_and_group()
4) Output:
   - salvar output/tuya_inventory.json
   - opcional: output/tuya_inventory.csv (flatten) para auditoria
5) Testes:
   - criar fixtures usando os exemplos que forneci (shadow/properties + specification)
   - testar parsing de values (range/min/max/step)
   - testar agrupamento light (ex.: switch_led+work_mode+bright_value_v2 etc)
6) Documentação:
   - README: como configurar ENV, rodar discovery, explicar formato do JSON.

Restrições importantes:
- Não quebrar compatibilidade com o que já existe (se existir CLI/rotas).
- Não colocar credenciais em código.
- O projeto deve rodar com `python -m prudentes_tuya_all.discover` ou comando equivalente.
- Se existir TypeScript/Node no repo, manter consistência e implementar o mesmo pipeline (mas escolha 1 linguagem principal; não duplicar à toa).

Definições:
- “Entidade” aqui = DP (dp_id + dp_code + type + value) + contexto da specification.
- “Classificar para Home Assistant” = sugerir plataforma e features, inspirado no hass-localtuya.

Entregáveis no PR:
- Código do client Tuya + discovery pipeline + classificador + export JSON
- Script de extração/integração das tabelas do hass-localtuya (conforme opção A ou B)
- Testes com fixtures
- README atualizado com instruções.

Comece produzindo:
- um plano de alterações (arquivos a criar/modificar),
- depois implemente incrementalmente com commits pequenos,
- e finalize com uma execução de exemplo (mock) usando os exemplos de responses para mostrar o JSON final.
