# Prompt – Versão Aprimorada

## Objetivo
Gerar um repositório completo (código + READMEs técnicos) para demo de TCC contendo stack Docker com HiveMQ CE e app Node.js (dashboard CodeX/Bootstrap), além de uma integração custom do Home Assistant que expõe todos os datapoints Tuya Cloud via Config Flow.

## Entradas
- `codex/request.md` (escopo original).
- Credenciais Tuya Developer Cloud (Access ID/Secret, region/base_url) informadas pelo usuário após deploy.
- IP fixo do Home Assistant: `10.10.10.100` (rede 10.10.10.0/24).

## Saídas (artefatos obrigatórios)
- Arquivos reais no repositório: `docker-compose.yml`, `Dockerfile`, `package.json`, `src/server.js`, `src/mqtt.js`, `src/ha.js`, `views/*` (EJS + assets), `.env.example`.
- Custom component Home Assistant em `custom_components/prudentes_tuya_all/` com `manifest.json`, `__init__.py`, `config_flow.py`, `options flow`, `coordinator.py`, plataformas `sensor.py`, `switch.py`, `number.py`, `select.py`, `binary_sensor.py`, `tuya_client.py`, traduções `pt-BR/en`.
- `docs/swagger.yaml` e rota `/swagger` no Node.
- README principal com tutorial passo a passo (VirtualBox + HA), variáveis de ambiente, comandos e árvore de documentação; READMEs por funcionalidade em `funcionalidades/*`.
- Arquivos de rastreio: `codex/improved-prompt.md`, `codex/suggest.md`, `codex/executed.md`, `codex/error.md`.

## Passo a passo (alto nível)
1. Ler `codex/request.md` e extrair requisitos de rede, serviços e formatos de entrega.
2. Construir stack Docker (Node 20, HiveMQ CE, demo publisher opcional, Node-RED opcional comentado).
3. Implementar app Node (Express + SSE + mqtt.js + ha.js) com páginas `/`, `/devices`, `/mqtt`, `/health` e Swagger documentando APIs.
4. Criar UI CodeX/Bootstrap com log em tempo real, form de publicação MQTT e links para HiveMQ Control Center.
5. Desenvolver integração Home Assistant `prudentes_tuya_all` com Config Flow/Options, DataUpdateCoordinator, entidades para todos os DPs (mapear bool/enum/value/string/json) e sensor diagnóstico.
6. Produzir README detalhado (execução, variáveis, HA no VirtualBox, instalação do custom component) e READMEs por funcionalidade.
7. Registrar execução em `codex/executed.md`, erros/limitações em `codex/error.md` e sugestões de melhoria em `codex/suggest.md`.

## Restrições e políticas
- Idioma pt-BR em docs/comentários; nomes de funções em inglês (clean code).
- Não incluir Home Assistant no docker-compose; deixar claro que Tuya Cloud requer internet.
- Não hardcode tokens; usar `.env.example` e variáveis de ambiente.
- Evitar remoção de conteúdo válido; apenas adicionar/atualizar.

## Critérios de aceite
- Stack Docker sobe serviços `mqtt-broker` e `app`; demo publisher/Node-RED opcionais documentados.
- Dashboard exibe status MQTT, log em tempo real, publica tópicos conforme convenção `tcc/demo/*`, e fornece endpoints `/devices`, `/mqtt`, `/health`, `/swagger`.
- Custom component instala via UI, cria entidades para todos os DPs (inclui sensor diagnóstico) e permite ajustar polling/DPs via Options Flow.
- README principal contém tutorial clique a clique do HA no VirtualBox, variáveis de ambiente e índice para READMEs de funcionalidades.
- Arquivos `codex/*` preenchidos; sugestões ≥5 itens em `codex/suggest.md`.

## Validações automáticas
- [ ] Arquivos obrigatórios existem e não estão vazios.
- [ ] `docker-compose.yml` referencia Node 20 app e HiveMQ CE.
- [ ] Rota `/swagger` acessa `docs/swagger.yaml`.
- [ ] Custom component contém manifest/config_flow/options/coordinator/plataformas/traduções.
- [ ] README inclui tutorial HA + links para `funcionalidades/*`.
