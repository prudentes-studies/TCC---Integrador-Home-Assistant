# Demo TCC CodeX / Home Assistant / Tuya Cloud

Repositório completo para demonstrar uma stack MQTT com HiveMQ CE, um dashboard web CodeX/Bootstrap com backend Node.js 20, e uma integração customizada do Home Assistant para expor todos os datapoints Tuya Cloud (inspirada e expandida a partir do projeto [hass-localtuya](https://github.com/xZetsubou/hass-localtuya)).

## Sumário rápido
- [Arquitetura](#arquitetura)
- [Pré-requisitos](#pré-requisitos)
- [Como subir a stack Docker](#como-subir-a-stack-docker)
- [Variáveis de ambiente](#variáveis-de-ambiente)
- [Swagger das APIs](#swagger-das-apis)
- [Dashboard CodeX](#dashboard-codex)
- [Tutorial Home Assistant no VirtualBox](#tutorial-home-assistant-no-virtualbox)
- [Instalação da integração Tuya](#instalação-da-integração-tuya)
- [Estrutura de documentação por funcionalidade](#estrutura-de-documentação-por-funcionalidade)
- [Roadmap e troubleshooting](#roadmap-e-troubleshooting)

## Arquitetura
- **HiveMQ CE** como broker MQTT (porta 1883, Control Center em 8080).
- **Node.js 20 (Express + SSE)**: backend publica/assina tópicos `tcc/demo/*`, fornece API REST, Swagger e UI com Bootstrap.
- **Demo publisher opcional**: publica mensagens em `tcc/demo/log` a cada 2s para ilustrar tráfego.
- **Integração Home Assistant**: custom component `prudentes_tuya_all` com config flow, polling via DataUpdateCoordinator e criação de entidades para cada DP (sensor, binary_sensor, switch, number, select + sensor de diagnóstico).
- **Opcional**: container Node-RED (comentado) para cenários sem addon interno.

## Pré-requisitos
- Docker + Docker Compose instalados.
- Porta 3000 livre (dashboard), 1883/8080 para HiveMQ.
- Node 20+ se desejar rodar localmente sem Docker.
- Acesso à internet **apenas** para Tuya Cloud e download de imagens Docker.

## Como subir a stack Docker
```bash
docker compose up -d --build
```
Serviços:
- `mqtt-broker`: HiveMQ CE (1883/8080)
- `app`: dashboard + API em http://localhost:3000
- `demo-publisher`: desativado por padrão (replicas: 0). Ajuste no compose se desejar.
- `node-red`: comentado; descomente se não usar o addon do HA.

### Rodar localmente sem Docker
```bash
npm install
cp .env.example .env
npm start
```

## Variáveis de ambiente
| Variável | Descrição |
|---|---|
| PORT | Porta do dashboard (padrão 3000) |
| MQTT_BROKER_URL | URL do broker (ex.: mqtt://mqtt-broker:1883) |
| MQTT_CONTROL_CENTER | URL exibida na UI para o HiveMQ CC |
| HA_BASE_URL | Endpoint do Home Assistant (ex.: http://10.10.10.100:8123) |
| HA_TOKEN | Long-lived token do Home Assistant |
| ENABLE_HA | `true` para habilitar chamadas à API do HA |
| DEMO_PUBLISHER_ENABLED | Reservado para habilitar publisher em linha (use o serviço dedicado) |

## Swagger das APIs
- Endpoint: [`/swagger`](http://localhost:3000/swagger)
- Cobertura: healthcheck, publicação MQTT, listagem de estados e chamada de serviços do Home Assistant.

## Dashboard CodeX
- **Rotas**: `/` (dashboard), `/devices` (HA states), `/mqtt` (debug), `/health` (JSON).
- **Tópicos padrão**: `tcc/demo/cmd/{device}/{action}`, `tcc/demo/state/{device}`, `tcc/demo/ack/{device}`, `tcc/demo/log`.
- **Recursos**: SSE para log em tempo real, formulário para publicar comandos, link para Control Center e painel de saúde.

## Tutorial Home Assistant no VirtualBox
Passo a passo clique a clique para a topologia descrita:
1. Baixe a imagem VDI/OVA do Home Assistant OS e importe no VirtualBox.
2. Na VM, acesse **Configurações > Rede > Adaptador 1** e selecione *Bridged Adapter* associado à interface usada pelo roteador Deco X60.
3. Em **Avançado**, defina o endereço MAC se precisar reservar IP no Deco. Salve e inicialize a VM.
4. Após boot, acesse `http://homeassistant.local:8123` ou o IP atribuído. Ajuste para IP estático `10.10.10.100` via **Settings > System > Network** no HA ou via reserva DHCP no Deco.
5. Ative o addon **File Editor** ou conecte via SSH para criar/confirmar a pasta `config/custom_components`.
6. Copie a pasta `custom_components/prudentes_tuya_all` deste repo para `config/custom_components/prudentes_tuya_all`.
7. Reinicie o Home Assistant (**Developer Tools > Check config**, depois **Settings > System > Restart**).
8. Vá em **Settings > Devices & Services > Add Integration**, procure por **Prudentes Tuya All** e informe:
   - `Tuya Access ID`, `Tuya Access Secret`, `Região`, `Base URL` (ex.: https://openapi.tuyaus.com)
   - `Device IDs` separados por vírgula.
   - Intervalo de polling desejado.
9. Após salvar, abra **Options** da integração para habilitar/desabilitar DPs individualmente e ajustar polling.
10. Verifique as entidades criadas (um sensor por DP, switches/numbers/selects conforme tipo, e um sensor diagnóstico por device).

## Instalação da integração Tuya
- Requer acesso à Tuya Developer Cloud. Nenhum segredo é salvo em código.
- Polling configurável e entidades criadas para **todos** os datapoints retornados.
- Mapas de plataforma: bool → switch/binary_sensor, enum/string → select/sensor, value → number/sensor, JSON → sensor com atributos completos.
- Sensor de diagnóstico agrega todos os DPs e schema como atributos.

## Estrutura de documentação por funcionalidade
- [`funcionalidades/mqtt-dashboard/README.md`](funcionalidades/mqtt-dashboard/README.md): guia do dashboard MQTT + API.
- [`funcionalidades/tuya-integration/README.md`](funcionalidades/tuya-integration/README.md): detalhes da integração `prudentes_tuya_all`.

## Roadmap e troubleshooting
- Melhorar detecção de *writable* vs *read-only* ao mapear bool para switch/binary_sensor usando o schema do spec Tuya.
- Acrescentar caching de token OAuth Tuya e refresh automático.
- Acrescentar testes automatizados (jest/pytest) e pipelines CI.
- Se o HiveMQ não subir, confirme portas 1883/8080 livres; para HA, valide IP 10.10.10.100 alcançável do container.

