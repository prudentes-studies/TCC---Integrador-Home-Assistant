# Prompt – Versão Aprimorada

## Objetivo
Implementar e documentar um pipeline completo de descoberta de entidades Tuya Cloud (OpenAPI) para o projeto “prudentes tuya-all”, cobrindo autenticação, paginação de dispositivos online/offline, leitura de specification/shadow, classificação inspirada no hass-localtuya e exportação de um inventário JSON pronto para uso no Home Assistant.

## Entradas
- Arquivo: `codex/request.md` (descrição detalhada das expectativas de discovery e classificação).
- Credenciais via variáveis de ambiente: `TUYA_CLIENT_ID`, `TUYA_CLIENT_SECRET`, `TUYA_REGION`, `TUYA_BASE_URL` (e equivalentes legados `TUYA_ACCESS_ID`/`TUYA_ACCESS_SECRET`).
- Dados de mapeamento hass-localtuya exportados em `custom_components/prudentes_tuya_all/data/localtuya_mappings.json`.
- Fixtures de testes unitários em `tests/`.

## Saídas (artefatos obrigatórios)
- Cliente Tuya com assinatura HMAC-SHA256, renovação de token, paginação e retry/backoff.
- Pipeline de discovery que coleta categorias, lista completa de devices, specification + shadow por device, classificação HA e consolidação em `output/tuya_inventory.json`.
- Exportador do conhecimento hass-localtuya (`scripts/extract_localtuya_mappings.py`) e JSON gerado.
- Testes unitários cobrindo paginação, merge de specification/shadow e heurísticas de classificação.
- Documentação atualizada em `README.md` e `funcionalidades/tuya-integration/README.md`.

## Passo a passo (alto nível)
1. Ler `codex/request.md` e validar requisitos de endpoints, autenticação e heurísticas.
2. Implementar `TuyaClient` com geração de token, assinatura, tratamento de 401/429/5xx e paginação `/v1.3/iot-03/devices`.
3. Criar/ajustar pipeline de discovery: categorias, devices, specification `/v1.0/iot-03/devices/{id}/specification`, shadow `/v2.0/cloud/thing/{id}/shadow/properties`, merge, classificação (hass-localtuya + heurísticas) e export JSON.
4. Incorporar conhecimento hass-localtuya: vendorizar `ha_entities`, extrair para JSON e consumir no classificador.
5. Atualizar CLI (`scripts/tuya_discover.py`) para gerar `output/tuya_inventory.json`, parametrizar por envs e exibir resumo.
6. Atualizar documentação (README e READMEs de funcionalidades) com árvore de docs, variáveis, comandos e formato do inventário.
7. Registrar execução em `codex/executed.md`, sugestões em `codex/suggest.md` e limitações em `codex/error.md`.

## Restrições e políticas
- Sem credenciais hardcoded; todas as chaves via ENV.
- Manter compatibilidade com nomes de variáveis legados (`TUYA_ACCESS_ID/SECRET`).
- Não duplicar pipelines em linguagens diferentes; priorizar Python.
- Idioma pt-BR para textos/documentação.

## Critérios de aceite
- `output/tuya_inventory.json` gerado pelo pipeline reflete categorias, devices online/offline e entidades com dp_id/dp_code, spec (min/max/range/step/scale), classificação HA (plataforma, features, confidence, reasons).
- Retry/backoff implementado para 429/5xx e renovação de token em 401.
- Conhecimento hass-localtuya disponível em JSON e usado na classificação.
- Testes unitários cobrindo paginação, merge de specification/shadow e heurísticas passam.
- README atualizado com mapa de documentação, comandos de discovery e variáveis ENV.

## Validações automáticas (quando aplicável)
- [ ] Execução dos testes `python -m unittest tests/test_discovery.py`.
- [ ] Geração do arquivo `output/tuya_inventory.json` (mock/dados reais).
- [ ] Presença de `custom_components/prudentes_tuya_all/data/localtuya_mappings.json` atualizado.
- [ ] Documentação revisada e links funcionais para READMEs de funcionalidades.
