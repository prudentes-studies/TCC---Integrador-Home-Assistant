# Prompt – Versão Aprimorada

## Objetivo
Implementar a descoberta completa de entidades (DPs) do Tuya Development Cloud conforme `codex/request.md`, sem depender do status online dos devices. O trabalho deve consolidar as respostas das APIs de devices, specifications, model e status em um pipeline único, classificar automaticamente o tipo de entidade (switch/light/cover/fan/climate/sensor/select/number/button/scene/unknown) com score e justificativa e exportar o resultado em JSON executável via CLI.

## Entradas
- `codex/request.md` com o problema de discovery incompleto e as rotas REST que devem ser usadas.
- Código da integração Home Assistant em `custom_components/prudentes_tuya_all/` (especialmente `tuya_client.py`, `coordinator.py`, `helpers.py` e entidades).
- Scripts utilitários em `scripts/` e documentação em `README.md` e `funcionalidades/tuya-integration/README.md`.

## Saídas (artefatos obrigatórios)
- Pipeline de descoberta com funções `discoverProjectDevices`, `discoverDeviceEntities`, merge de fontes (specifications + model + status) e classificação de `entityType`, reutilizando o cliente HTTP existente.
- CLI ou comando (ex.: `npm run tuya:discover`) que gera `./artifacts/tuya-entities-map.json` com devices → entidades contendo dpCode, dpId, dpType, typeSpec normalizado, access (ro/rw/wr), currentValue, entityType, confidence e reason.
- Limite de concorrência e retry/backoff para 429/5xx nas chamadas; suporte a paginação (`last_row_key`) e inclusão opcional de sub-devices.
- Testes unitários (fixtures/mocks) cobrindo paginação, merge de `dpId/dp_id`, parse do `model` (string JSON) e heurísticas de classificação.
- Documentação atualizada no `README.md` e em `funcionalidades/tuya-integration/README.md` explicando como executar o discovery, variáveis necessárias, formato do JSON e índice navegável.
- Registros em `codex/improved-prompt.md`, `codex/suggest.md`, `codex/executed.md` e `codex/error.md` refletindo decisões, sugestões e limitações.

## Passo a passo (alto nível)
1. Ler `codex/request.md` e mapear requisitos, rotas e critérios de aceite.
2. Inspecionar o cliente Tuya existente e centralizar as chamadas exigidas (/v2.0/cloud/thing/device, /v1.1/devices/{id}/specifications, /v2.0/cloud/thing/{id}/model, /v1.0/iot-03/devices/{id}/status, sub-devices opcional).
3. Implementar o pipeline de discovery com paginação, merge por dpCode e normalização de dpId/typeSpec/values (mesmo quando vierem como string JSON), preenchendo currentValue e accessMode.
4. Criar heurísticas de classificação (switch/light/cover/fan/climate/sensor/select/number/button/scene/unknown) com confidence e reason, usando dpCode, categoria e typeSpec.
5. Expor comando/CLI que executa o discovery, aplica concorrência/retry e salva o JSON final em `artifacts/tuya-entities-map.json`, além de logar um resumo no console.
6. Adicionar testes unitários para paginação, merge/normalização, parse do model e classificação; documentar como rodá-los.
7. Atualizar READMEs com instruções de uso, variáveis `TUYA_*`, árvore de documentação e links para a funcionalidade.
8. Registrar execução, sugestões e eventuais limitações em `codex/executed.md`, `codex/suggest.md` e `codex/error.md`.

## Restrições e políticas
- Manter idioma em português (pt-BR), preservando termos técnicos em inglês quando necessário.
- Não remover conteúdos válidos; apenas complementar ou corrigir mantendo rastreabilidade.
- Reaproveitar padrões de logging, autenticação e cliente HTTP existentes no repositório.
- Mascarar segredos/client_secret em logs e artefatos.

## Critérios de aceite
- O comando/fluxo de discovery lista todos os devices via `/v2.0/cloud/thing/device` com paginação e inclui sub-devices quando habilitado.
- Para cada device, as entidades combinam dpId/dpCode (specifications), typeSpec/accessMode (model) e currentValue (status), independentemente do device estar online.
- O JSON consolidado é gerado em `./artifacts/tuya-entities-map.json` e o console traz totais e erros por device.
- Heurísticas de `entityType` retornam `confidence` e `reason` coerentes; testes unitários cobrem paginação, merge e classificação.
- Documentação atualizada com índice/árvore e instruções de execução; registros `codex/*` preenchidos.

## Validações automáticas (quando aplicável)
- [ ] `npm run tuya:discover` (quando segredos TUYA_* estiverem disponíveis)
- [ ] `npm run test:python`
- [ ] `npm run lint`
