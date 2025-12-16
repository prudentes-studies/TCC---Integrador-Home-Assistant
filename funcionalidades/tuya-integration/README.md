# Integração Home Assistant `prudentes_tuya_all`

## Objetivo
Expor todos os datapoints Tuya Cloud via Home Assistant de forma **100% dinâmica**, lendo o schema de cada dispositivo diretamente do portal Tuya Developer. A integração agora é instalada como **repositório externo via HACS** (sem cópia manual para `config/custom_components`) e cria entidades com base em `shadow`, `specification` e funções disponíveis.

## Pré-requisitos
- Home Assistant OS ativo (recomendado IP fixo `10.10.10.100`).
- Add-on **HACS** instalado e configurado.
- Credenciais do Tuya Developer Cloud: `Access ID`, `Access Secret`, `Base URL` (ex.: `https://openapi.tuyaus.com`) e `Região` (`us`, `eu`, `in`, `cn`).
- Conexão de rede do HA com a internet.

### Segredos para CI/CD
- Crie no GitHub os segredos `TUYA_ACCESS_ID`, `TUYA_ACCESS_SECRET`, `TUYA_REGION` e, opcionalmente, `TUYA_BASE_URL`.
- O workflow `CI-CD` executa `scripts/ci_tuya_discovery.py`, que só lista dispositivos quando todos os segredos estão presentes. Para testes locais completos, use o comando `npm run tuya:discover` descrito abaixo para gerar `artifacts/tuya-entities-map.json`.

## Passo a passo clique a clique — instalação via HACS
1. **Adicionar este repositório no HACS**
   - Em **HACS > Integrations**, clique no menu de três pontinhos (**⋮**) e escolha **Custom repositories**.
   - Cole a URL deste repositório Git (HTTPS) e selecione o tipo **Integration**. Confirme em **Add**.
2. **Instalar a integração**
   - Ainda em **HACS > Integrations**, clique em **Explore & Download repositories**.
   - Busque por **Prudentes Tuya All** e clique em **Download**.
   - No modal, confirme a versão sugerida e pressione **Download** novamente. Aguarde a barra de progresso terminar.
3. **Reiniciar o Home Assistant**
   - Acesse **Settings > System > Restart** e confirme **Restart** para carregar o componente recém-instalado.
4. **Criar a entry de configuração**
   - Vá em **Settings > Devices & Services > Add Integration**.
   - Pesquise **Prudentes Tuya All** e selecione.
   - Preencha **Access ID**, **Access Secret**, **Região** e **Base URL**.
   - Deixe o campo **Device IDs** vazio para habilitar **descoberta automática** via API (`/v2.0/cloud/thing/device`). O fluxo paginará usando `last_row_key` até listar todos os dispositivos.
   - Clique em **Submit** para salvar.
5. **Ajustar opções após a instalação**
   - Na tela da integração, clique em **Configure**.
   - Defina o **intervalo de polling** em segundos.
   - Opcionalmente, edite a lista de **Device IDs** (se quiser limitar) ou deixe vazia para continuar descobrindo automaticamente.
6. **Validar entidades geradas**
   - Abra **Settings > Devices & Services > Prudentes Tuya All > Entities**.
   - Confirme a criação de switches/binary_sensors para `bool` (writable ou somente leitura), números para `value/integer/float`, selects para `enum/string` e sensores para todos os datapoints, além do sensor **diagnostic** com atributos completos do schema.

## Funcionamento dinâmico
- O `TuyaClient` busca token (`/v1.0/token`) e usa o header `access_token` para assinar chamadas, com retry e backoff automático para HTTP 429/5xx.
- A cada ciclo do coordinator e no comando de discovery, são lidos:
  - **Categorias**: `/v1.0/iot-03/device-categories` para mapear `category → nome`.
  - **Lista de devices**: `/v1.3/iot-03/devices` com paginação via `last_row_key` e `has_more`, incluindo devices offline.
  - **Spec/DP ID**: `/v1.0/iot-03/devices/{id}/specification` (status + functions) normalizando `dpId/dp_id` e `values` (dict ou JSON string).
  - **Shadow/propriedades**: `/v2.0/cloud/thing/{id}/shadow/properties` para preencher `currentValue` em cada DP.
  - **Sub-devices** (opcional): `/v1.0/iot-03/devices/{id}/sub-devices` quando o device é gateway.
- O merge de fontes indexa por `dpCode`, associa `dpId`, `typeSpec`, `accessMode`, `currentValue` e classifica automaticamente o `entityType` (switch/light/fan/cover/climate/sensor/select/number/button/unknown) com score e justificativa.

## Pontos de extensão
- Cache persistente de tokens para reduzir chamadas de autenticação.
- Suporte a filtros por categoria/room ao paginar dispositivos.
- Testes automatizados adicionais cobrindo envio de comandos e fluxos de fallback quando o endpoint `/model` falhar.
- Expor o JSON de discovery como endpoint HTTP no HA para consumo externo.

## Discovery via CLI (JSON consolidado)
- Com `python` disponível, execute:
  ```bash
  export TUYA_CLIENT_ID=...
  export TUYA_CLIENT_SECRET=...
  export TUYA_REGION=us  # ou eu/in/cn
  python scripts/tuya_discover.py
  ```
- Parâmetros opcionais: `TUYA_BASE_URL`, `TUYA_CONCURRENCY` (padrão 3) e `TUYA_INCLUDE_SUB=false` para ignorar sub-devices.
- Saída: `output/tuya_inventory.json` contendo `project`, categorias, devices, entidades com `dpCode/dpId`, `dpType`, `typeSpec`, `currentValue` e classificação `ha` (plataforma/features/confidence/reasons). O console mostra contagens e erros por device; o classificador usa heurísticas mais conhecimento exportado do hass-localtuya.

## Troubleshooting específico desta versão
- **Erro no Configure com `AttributeError: 'ConfigEntry' object has no attribute 'hass'`:** a Options Flow armazena `config_entry` apenas em atributo privado e usa `self.hass` provido pelo fluxo. Atualize a integração via HACS, reinicie o Home Assistant e reabra **Configure**.
- **Device IDs exibidos como caracteres soltos:** o fluxo normaliza qualquer string separada por vírgulas antes de salvar. Reabra **Configure**, ajuste a lista (ex.: `id1,id2,id3`) e salve.
- **Entidades não aparecem após salvar opções:** deixe `Device IDs` vazio para redescoberta automática, confirme o intervalo de polling e acompanhe os logs (`custom_components.prudentes_tuya_all: debug`) para verificar se devices foram carregados.
- **Descoberta automática não retornou IDs no CI:** preencha os segredos `TUYA_*` no repositório. Sem segredos, o passo `scripts/ci_tuya_discovery.py` é ignorado e não há validação externa.
- **Falha de build da imagem Node no Docker Desktop (erro de metadata do `node:latest-alpine`):** execute `docker compose build --pull` após atualizar a tag para `node:20-alpine` e confirme que o daemon está autenticado no Docker Hub.
