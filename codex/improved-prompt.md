# Prompt – Versão Aprimorada

## Objetivo
Corrigir os problemas apontados em `codex/request.md`: (1) o Control Center do HiveMQ acessado em `http://localhost:8080` retorna erro interno; (2) o Options Flow da integração `prudentes_tuya_all` falha com `AttributeError` ao carregar opções no Home Assistant. Entregar correções de código/configuração, documentação revisada e registros completos nos arquivos `codex/*`.

## Entradas
- `codex/request.md` com o relato do erro 500/"Internal Error" no Docker (porta 8080) e o stack trace do `AttributeError` no Options Flow.
- Código do componente Home Assistant em `custom_components/prudentes_tuya_all/` (especialmente `config_flow.py`).
- Arquivos de orquestração Docker (`docker-compose.yml`, `Dockerfile`, `Dockerfile.demo`).
- Documentação existente em `README.md` e em `funcionalidades/*/README.md`.

## Saídas (artefatos obrigatórios)
- Ajuste em `config_flow.py` eliminando o `AttributeError` ao abrir o fluxo de opções.
- Correção no serviço MQTT do `docker-compose.yml` para estabilizar o acesso ao Control Center (porta 8080) com tag fixada.
- Atualização dos READMEs (raiz e funcionalidades) com troubleshooting detalhado dos erros relatados e índice navegável.
- Registros consistentes em `codex/improved-prompt.md`, `codex/suggest.md`, `codex/executed.md` e `codex/error.md`.

## Passo a passo (alto nível)
1. Ler `codex/request.md` e identificar os erros solicitados.
2. Corrigir `custom_components/prudentes_tuya_all/config_flow.py` para usar armazenamento compatível do `config_entry` no Options Flow.
3. Atualizar `docker-compose.yml` para fixar a tag do HiveMQ CE que mantém o Control Center estável.
4. Revisar e enriquecer `README.md` e `funcionalidades/*/README.md` com árvore de documentação, referências cruzadas e orientações de troubleshooting para 8080 e Options Flow.
5. Preencher `codex/suggest.md` com variações e melhorias; `codex/executed.md` com o que foi feito; `codex/error.md` com limitações encontradas.

## Restrições e políticas
- Escrever em português (pt-BR), preservando termos técnicos em inglês quando necessário.
- Não remover conteúdos válidos; apenas complementar ou corrigir mantendo rastreabilidade.
- Garantir que os arquivos `codex/*` reflitam decisões, ações e limitações desta execução.

## Critérios de aceite
- Fluxo de opções do Home Assistant abre sem `AttributeError` para `config_entry`.
- Serviço MQTT acessível em `http://localhost:8080` sem erro interno quando executado com a tag fixada no compose.
- READMEs atualizados com índice, árvore de documentação e troubleshooting dos problemas relatados.
- `codex/suggest.md` contém pelo menos 5 sugestões; `codex/executed.md` descreve ações e verificações; `codex/error.md` lista limitações (incluindo impossibilidade de testes Docker neste ambiente).

## Validações automáticas (quando aplicável)
- [ ] `python -m compileall custom_components/prudentes_tuya_all`
- [ ] `npm run lint`
- [ ] Build opcional do Docker (`docker compose build`), quando disponível
