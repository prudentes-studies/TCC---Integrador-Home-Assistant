# Demo TCC CodeX / Home Assistant / Tuya Cloud

Stack de demonstração que combina **HiveMQ CE** (broker MQTT), **dashboard CodeX/Bootstrap** com backend Node.js e a integração customizada **`prudentes_tuya_all`** do Home Assistant para expor datapoints Tuya Cloud. As imagens Docker agora usam **tags fixas** (`hivemq/hivemq-ce:2023.5`, `node:20-alpine`) para evitar erros de resolução como o do `node:latest-alpine` no Docker Desktop.

## Sumário rápido
- [Arquitetura](#arquitetura)
- [Pré-requisitos](#pré-requisitos)
- [Guia clique a clique para subir a stack Docker](#guia-clique-a-clique-para-subir-a-stack-docker)
- [Execução local sem Docker](#execução-local-sem-docker)
- [Variáveis de ambiente e segredos](#variáveis-de-ambiente-e-segredos)
- [CI/CD](#cicd)
- [Dashboard CodeX](#dashboard-codex)
- [Tutorial Home Assistant no VirtualBox](#tutorial-home-assistant-no-virtualbox)
- [Instalação da integração Tuya via HACS](#instalação-da-integração-tuya-via-hacs)
- [Documentação por funcionalidade](#documentação-por-funcionalidade)
- [Índice de documentação e referências cruzadas](#índice-de-documentação-e-referências-cruzadas)
- [Roadmap e troubleshooting](#roadmap-e-troubleshooting)

## Arquitetura
- **HiveMQ CE (`hivemq/hivemq-ce:2023.5`)** — broker MQTT nas portas 1883 (mqtt) e 8080 (Control Center) com tag fixa para evitar regressões recentes da UI.
- **App Node.js (`node:20-alpine`)** — Express + SSE, publica/assina tópicos `tcc/demo/*` usando `mqtt` 5.14.1 (protocolo MQTT v5), expõe API REST, Swagger e UI Bootstrap.
- **Demo publisher (`node:20-alpine`)** — publica mensagens em `tcc/demo/log` a cada 2s (ativado ajustando replicas no Compose).
- **Integração Home Assistant** — componente `prudentes_tuya_all` que descobre devices Tuya Cloud, cria entidades dinamicamente e oferece fluxo de opções corrigido.
- **Opcional** — container Node-RED (comentado) para cenários sem add-on interno.

## Pré-requisitos
- Docker e Docker Compose (Compose v2 recomendado).
- Portas livres: **3000** (dashboard), **1883/8080** (HiveMQ CE) e **8123** na rede do Home Assistant.
- Node.js 20+ apenas se executar fora do Docker.
- Internet para baixar imagens e acessar a Tuya Cloud.
- VirtualBox se rodar o Home Assistant OS em VM.

## Guia clique a clique para subir a stack Docker
1. **Clonar o repositório**
   ```bash
   git clone https://github.com/<sua-conta>/TCC---Integrador-Home-Assistant.git
   cd TCC---Integrador-Home-Assistant
   ```
2. **Preparar variáveis**
   ```bash
   cp .env.example .env
   ```
   - Edite `.env` preenchendo `MQTT_BROKER_URL`, `HA_BASE_URL`, `HA_TOKEN` e demais campos.
3. **Construir e iniciar os contêineres** (imagens atualizadas com `node:20-alpine`)
   ```bash
   docker compose up -d --build
   docker compose ps
   ```
   - `mqtt-broker` deve expor 1883/8080; `codex-app` deve expor 3000.
4. **Validar app e APIs**
   - Acesse `http://localhost:3000` (dashboard) e `http://localhost:3000/swagger` (API).
5. **Habilitar publisher de demonstração (opcional)**
   - No `docker-compose.yml`, altere `deploy.replicas` do serviço `demo-publisher` para `1` e rode `docker compose up -d demo-publisher`.
6. **Habilitar Node-RED (opcional)**
   - Descomente o bloco `node-red` no compose e suba com `docker compose up -d node-red`.

## Execução local sem Docker
```bash
npm install
cp .env.example .env
npm run lint
npm start
```

## Variáveis de ambiente e segredos
| Variável | Descrição | Onde usar |
|---|---|---|
| PORT | Porta do dashboard (3000 padrão) | `.env` / compose |
| MQTT_BROKER_URL | URL do broker (`mqtt://mqtt-broker:1883`) | `.env` / compose |
| MQTT_CONTROL_CENTER | URL mostrada na UI para o HiveMQ Control Center | `.env` / compose |
| HA_BASE_URL | Endpoint do Home Assistant (ex.: `http://10.10.10.100:8123`) | `.env` / compose |
| HA_TOKEN | Long-lived token do Home Assistant | `.env` / compose |
| ENABLE_HA | `true` para habilitar chamadas ao HA | `.env` / compose |
| DEMO_PUBLISHER_ENABLED | Reservado; prefira o serviço `demo-publisher` | `.env` |
| TUYA_ACCESS_ID/SECRET/REGION/BASE_URL | Segredos usados pelo passo de descoberta automática no CI | Segredos do repositório |

## CI/CD
Workflow **CI-CD** em `.github/workflows/ci.yml` com três validações:
- **Lint Node.js**: `npm ci` + `npm run lint` (checagem de sintaxe de `src/*.js` e `scripts/demoPublisher.js`).
- **Integração HA**: instala `aiohttp`, roda `python -m compileall custom_components/prudentes_tuya_all` e executa `scripts/ci_tuya_discovery.py` quando os segredos `TUYA_ACCESS_ID`, `TUYA_ACCESS_SECRET`, `TUYA_REGION` (e opcional `TUYA_BASE_URL`) estiverem configurados.
- **Docker smoke build**: `docker build` para a imagem principal e o publisher demo, garantindo que a tag `node:20-alpine` é resolvida.

### Como configurar segredos para a descoberta Tuya
1. No GitHub, acesse **Settings > Secrets and variables > Actions**.
2. Cadastre `TUYA_ACCESS_ID`, `TUYA_ACCESS_SECRET`, `TUYA_REGION` (ex.: `us`) e opcionalmente `TUYA_BASE_URL` (padrão `https://openapi.tuyaus.com`).
3. Reexecute a pipeline; o passo `Teste opcional de descoberta Tuya` exibirá a contagem de dispositivos retornados ou será ignorado se faltar algum segredo.

## Dashboard CodeX
- **Rotas**: `/` (dashboard), `/devices` (HA states), `/mqtt` (debug), `/health` (JSON) e `/swagger` (documentação Swagger).
- **Uso guiado**:
  1. Com a stack ativa, abra `http://localhost:3000`.
  2. Em **Publicar comando**, preencha **Device** e **Action** e clique em **Publicar** para enviar `tcc/demo/cmd/{device}/{action}`.
  3. Veja retornos SSE em tempo real; o publisher de demo aparece automaticamente se habilitado.
  4. Em **MQTT Debug**, publique payloads arbitrários e acompanhe `tcc/demo/ack/{device}`.
  5. Em **Devices**, liste estados do Home Assistant (requer `ENABLE_HA=true` e token válido).

## Tutorial Home Assistant no VirtualBox
1. **Baixar a imagem HA OS** (VDI/OVA) do site oficial.
2. **Criar VM** no VirtualBox com ≥2 GB RAM e ≥2 vCPUs.
3. **Configurar rede** em modo Bridge e, se desejar, definir MAC para reserva de IP.
4. **Inicializar** e acessar `homeassistant.local:8123` ou o IP exibido no console.
5. **Fixar IP 10.10.10.100** em **Settings > System > Network > IPv4** (ou reserve no roteador Deco).
6. **Instalar HACS** e seguir o fluxo da seção abaixo para adicionar a integração.
7. **Adicionar integração Prudentes Tuya All**: em **Settings > Devices & Services > Add Integration**, informe `Access ID/Secret`, `Região` e `Base URL`; deixe **Device IDs** vazio para descoberta automática.

## Instalação da integração Tuya via HACS
1. Em **HACS > Integrations**, abra **⋮ > Custom repositories**, cole a URL deste Git e escolha **Integration**.
2. Em **Explore & Download repositories**, busque **Prudentes Tuya All** e clique em **Download**.
3. Reinicie o Home Assistant em **Settings > System > Restart**.
4. Crie a integração em **Devices & Services > Add Integration** informando credenciais Tuya; deixe **Device IDs** vazio para descoberta via `/v2.0/cloud/thing/device` (pagina usando `last_row_key`).
5. Em **Configure**, ajuste o **intervalo de polling** e, se desejar, limite `Device IDs`; vazio = descoberta contínua.
6. Valide em **Entities**: switches/binary_sensors para `bool`, numbers para `value/integer/float`, selects para `enum/string`, sensores para demais datapoints e sensor `diagnostic` com atributos de schema.

## Documentação por funcionalidade
- [`funcionalidades/mqtt-dashboard/README.md`](funcionalidades/mqtt-dashboard/README.md): UI CodeX/Bootstrap para MQTT, passos para publicar/assinar, uso do Swagger e healthcheck.
- [`funcionalidades/tuya-integration/README.md`](funcionalidades/tuya-integration/README.md): instalação via HACS, descoberta automática, segredos da pipeline Tuya e troubleshooting do fluxo de opções.

## Índice de documentação e referências cruzadas
- **`README.md` (este arquivo):** visão geral da stack, pré-requisitos, comandos e troubleshooting.
- **`funcionalidades/mqtt-dashboard/README.md`:** guia operacional do dashboard MQTT e como validar o HiveMQ Control Center.
- **`funcionalidades/tuya-integration/README.md`:** fluxo completo da integração Tuya, incluindo o ajuste do Options Flow e logs recomendados.
- **`codex/request.md`:** entrada original das correções solicitadas.
- **`codex/improved-prompt.md`, `codex/suggest.md`, `codex/executed.md`, `codex/error.md`:** rastreabilidade de prompt, variações, execução e limitações encontradas nesta entrega.
- **Árvore sugerida:**
  ```
  README.md
  funcionalidades/
    mqtt-dashboard/README.md
    tuya-integration/README.md
  codex/
    request.md
    improved-prompt.md
    suggest.md
    executed.md
    error.md
  ```

### Árvore de documentação
```
README.md
funcionalidades/
  mqtt-dashboard/README.md
  tuya-integration/README.md
codex/
  request.md
  improved-prompt.md
  suggest.md
  executed.md
  error.md
```

## Roadmap e troubleshooting
- Melhorar detecção de *writable* vs *read-only* ao mapear `bool` para switch/binary_sensor usando o schema Tuya.
- Cache de token e refresh automático no `TuyaClient`.
- Testes automatizados (jest/pytest) adicionais e cobertura do fluxo de opções.
- Se HiveMQ não subir, valide portas 1883/8080 livres; para HA, confirme IP 10.10.10.100 acessível do contêiner.

### Diagnóstico de erros recentes
- **Erro ao abrir Configure — `AttributeError: 'ConfigEntry' object has no attribute 'hass'`**: atualize a integração `prudentes_tuya_all` para a versão corrigida que evita ler `config_entry.hass` dentro do Options Flow. Reinicie o Home Assistant e reabra **Configure**.
- **Dependência MQTT desatualizada**: se o dashboard não conectar ao broker, execute `npm install` após confirmar que `package.json` está em `mqtt@^5.14.1` e reinicie o serviço para negociar protocolo v5 com o HiveMQ.
- **Falha ao buildar `node:latest-alpine`**: as Dockerfiles passaram para `node:20-alpine`; execute `docker compose build --pull` para baixar a tag correta.
- **Entidades não carregam após salvar opções**: deixe `Device IDs` vazio para descoberta automática, salve e aguarde um ciclo de polling; ative logs `custom_components.prudentes_tuya_all: debug` para inspecionar.
- **Aviso de performance do `sun.sun` (~0.9s)**: entidade nativa; monitore recorrência e avalie abertura de issue upstream se o atraso aumentar.
- **Control Center do HiveMQ em `localhost:8080` retornando "Internal Error"**: utilize a tag fixa `hivemq/hivemq-ce:2023.5`, rode `docker compose pull mqtt-broker && docker compose up -d mqtt-broker` e aguarde 15–20s até o dashboard inicializar; se permanecer o erro, valide conflitos de porta 8080 ou rode `docker compose logs mqtt-broker` para inspecionar.
