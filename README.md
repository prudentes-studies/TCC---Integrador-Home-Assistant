# Demo TCC CodeX / Home Assistant / Tuya Cloud

Repositório completo para demonstrar uma stack MQTT com HiveMQ CE, um dashboard CodeX/Bootstrap com backend Node.js e a integração customizada do Home Assistant que expõe todos os datapoints Tuya Cloud. Todas as imagens Docker usam a tag **`latest`** para garantir que sempre partam da versão estável mais recente.

## Sumário rápido
- [Arquitetura](#arquitetura)
- [Pré-requisitos](#pré-requisitos)
- [Guia clique a clique para subir a stack Docker](#guia-clique-a-clique-para-subir-a-stack-docker)
- [Variáveis de ambiente](#variáveis-de-ambiente)
- [Dashboard CodeX](#dashboard-codex)
- [Tutorial Home Assistant no VirtualBox](#tutorial-home-assistant-no-virtualbox)
- [Instalação da integração Tuya](#instalação-da-integração-tuya)
- [Estrutura de documentação por funcionalidade](#estrutura-de-documentação-por-funcionalidade)
- [Roadmap e troubleshooting](#roadmap-e-troubleshooting)

## Arquitetura
- **HiveMQ CE (`hivemq/hivemq-ce:latest`)** como broker MQTT (porta 1883, Control Center em 8080).
- **Node.js (`node:latest-alpine`)**: backend Express + SSE que publica/assina tópicos `tcc/demo/*`, fornece API REST, Swagger e UI com Bootstrap.
- **Demo publisher opcional**: publica mensagens em `tcc/demo/log` a cada 2s para ilustrar tráfego.
- **Integração Home Assistant**: custom component `prudentes_tuya_all` inspirado no projeto [hass-localtuya](https://github.com/xZetsubou/hass-localtuya) para expor todos os datapoints Tuya Cloud via Config/Options Flow.
- **Opcional**: container Node-RED comentado para cenários sem addon interno.

## Pré-requisitos
- Docker e Docker Compose instalados (recomendado Compose v2).
- Portas disponíveis: **3000** (dashboard), **1883**/**8080** (HiveMQ CE) e **8123** na rede do Home Assistant.
- Node.js instalado localmente **apenas** se desejar executar sem Docker.
- Acesso à internet para download das imagens Docker e comunicação com a Tuya Cloud.
- VirtualBox instalado caso vá rodar o Home Assistant OS em VM.

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
   - Edite `.env` preenchendo `MQTT_BROKER_URL`, `HA_BASE_URL`, `HA_TOKEN` e demais campos conforme a tabela abaixo.
3. **Construir e iniciar os contêineres com as imagens mais recentes**
   ```bash
   docker compose up -d --build
   ```
4. **Confirmar se todos os serviços estão no ar**
   ```bash
   docker compose ps
   ```
   - `mqtt-broker` deve exibir as portas 1883/8080; `codex-app` deve expor a 3000.
5. **Validar o dashboard e as APIs**
   - Abra `http://localhost:3000` (dashboard) em um navegador.
   - Abra `http://localhost:3000/swagger` e teste o endpoint de publicação MQTT.
6. **Habilitar o publisher de demonstração (opcional)**
   - Edite `docker-compose.yml` para alterar `deploy.replicas` do serviço `demo-publisher` para `1` e execute:
     ```bash
     docker compose up -d demo-publisher
     ```
7. **Habilitar Node-RED (opcional)**
   - Descomente o bloco `node-red` no `docker-compose.yml` (já configurado para `nodered/node-red:latest`).
   - Suba apenas ele se desejar:
     ```bash
     docker compose up -d node-red
     ```

### Rodar localmente sem Docker
```bash
npm install
cp .env.example .env
npm start
```

## Variáveis de ambiente
| Variável | Descrição | Onde usar |
|---|---|---|
| PORT | Porta do dashboard (padrão 3000) | `.env` ou variáveis do contêiner |
| MQTT_BROKER_URL | URL do broker (ex.: `mqtt://mqtt-broker:1883`) | `.env` / compose |
| MQTT_CONTROL_CENTER | URL exibida na UI para o HiveMQ Control Center | `.env` / compose |
| HA_BASE_URL | Endpoint do Home Assistant (ex.: `http://10.10.10.100:8123`) | `.env` / compose |
| HA_TOKEN | Long-lived token do Home Assistant | `.env` / compose |
| ENABLE_HA | `true` para habilitar chamadas à API do HA | `.env` / compose |
| DEMO_PUBLISHER_ENABLED | Reservado para habilitar publisher em linha (use o serviço dedicado) | `.env` |

## Dashboard CodeX
- **Rotas principais**: `/` (dashboard), `/devices` (HA states), `/mqtt` (debug), `/health` (JSON) e `/swagger` (documentação).
- **Uso guiado**:
  1. Com a stack ativa, abra `http://localhost:3000`.
  2. No painel principal, preencha **Device** e **Action** e clique em **Publicar** para enviar para `tcc/demo/cmd/{device}/{action}`.
  3. Acompanhe retornos em tempo real na área de log SSE; mensagens do publisher de demo aparecem automaticamente se o serviço estiver ativo.
  4. Clique na aba **MQTT Debug** para publicar payloads arbitrários e ver acks em `tcc/demo/ack/{device}`.
  5. Abra a aba **Devices** para listar estados do Home Assistant (requer `ENABLE_HA=true` e token válido).

## Tutorial Home Assistant no VirtualBox
Passo a passo clique a clique para a topologia descrita:
1. **Obter a imagem do HA OS**: baixe o arquivo VDI/OVA no site oficial.
2. **Criar a VM** no VirtualBox:
   - Clique em **Novo** → informe nome e selecione o arquivo OVA/VDI.
   - Ajuste memória (≥ 2 GB) e CPU (≥ 2 vCPUs), finalize a criação.
3. **Configurar rede**:
   - Abra **Configurações > Rede > Adaptador 1** e escolha **Placa em modo Bridge** atrelada à interface que acessa o roteador Deco X60.
   - Em **Avançado**, defina o endereço MAC se for reservar IP no roteador.
4. **Inicializar a VM** e aguardar o boot até o prompt `homeassistant login:`.
5. **Descobrir o IP** mostrado no console ou em **Exibir > Dispositivos de rede** e acesse `http://homeassistant.local:8123`.
6. **Fixar IP 10.10.10.100** (recomendado):
   - No Home Assistant vá em **Settings > System > Network > IPv4** e configure **Static IP** para `10.10.10.100`/24 e gateway do seu roteador, ou faça a reserva DHCP no Deco.
7. **Habilitar acesso a arquivos**:
   - Instale o addon **File Editor** via **Settings > Add-ons > Add-on Store**, clique em **Install** e depois **Start**.
   - Alternativamente, habilite o addon SSH e conecte para manipular `config/`.
8. **Copiar o custom component**:
   - Crie (ou confirme) a pasta `config/custom_components`.
   - Copie `custom_components/prudentes_tuya_all` deste repositório para `config/custom_components/prudentes_tuya_all` na VM.
9. **Reiniciar o Home Assistant** em **Settings > System > Restart** (confirme o prompt de reinício).
10. **Adicionar a integração**:
    - Vá em **Settings > Devices & Services > Add Integration**.
    - Busque por **Prudentes Tuya All** e preencha **Tuya Access ID**, **Access Secret**, **Região**, **Base URL** (ex.: `https://openapi.tuyaus.com`) e **Device IDs** separados por vírgula.
11. **Ajustar opções**:
    - Após concluir, clique em **Configure** na integração para definir intervalo de polling e habilitar/desabilitar datapoints específicos.
12. **Validar entidades**:
    - Acesse **Settings > Devices & Services > Prudentes Tuya All > Entities** e confirme a criação de sensores, switches, números, selects e o sensor de diagnóstico por dispositivo.

## Instalação da integração Tuya
- Credenciais não são salvas no código; forneça-as apenas via UI do HA.
- Polling configurável e entidades criadas para **todos** os datapoints retornados.
- Mapas de plataforma: bool → switch/binary_sensor, enum/string → select/sensor, value → number/sensor, JSON → sensor com atributos completos.
- Sensor de diagnóstico agrega todos os DPs e schema como atributos.

## Estrutura de documentação por funcionalidade
- [`funcionalidades/mqtt-dashboard/README.md`](funcionalidades/mqtt-dashboard/README.md): guia do dashboard MQTT + API, passo a passo clicável para publicar e observar mensagens.
- [`funcionalidades/tuya-integration/README.md`](funcionalidades/tuya-integration/README.md): instruções detalhadas para instalar e operar o custom component `prudentes_tuya_all` no HA.

## Roadmap e troubleshooting
- Melhorar detecção de *writable* vs *read-only* ao mapear bool para switch/binary_sensor usando o schema do spec Tuya.
- Acrescentar caching de token OAuth Tuya e refresh automático.
- Acrescentar testes automatizados (jest/pytest) e pipelines CI.
- Se o HiveMQ não subir, valide portas 1883/8080 livres; para HA, confirme IP 10.10.10.100 acessível do contêiner.
