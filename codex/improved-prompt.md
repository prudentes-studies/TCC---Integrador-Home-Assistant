# Prompt – Versão Aprimorada

## Objetivo
Corrigir os problemas apontados em `codex/request.md`: (1) o Options Flow da integração `prudentes_tuya_all` dispara `AttributeError: 'ConfigEntry' object has no attribute 'hass'` ao abrir **Configure** no Home Assistant; (2) a biblioteca `mqtt` usada pelo dashboard Node.js deve ser atualizada para a versão mais recente, com ajustes de código e documentação. Entregar correções de código/configuração, documentação revisada e registros completos nos arquivos `codex/*`.

## Entradas
- `codex/request.md` com o stack trace do `AttributeError: 'ConfigEntry' object has no attribute 'hass'` e o pedido de atualizar a biblioteca `mqtt` para a versão mais recente.
- Código do componente Home Assistant em `custom_components/prudentes_tuya_all/` (especialmente `config_flow.py`).
- Código Node.js em `src/mqtt.js` e `src/server.js`, além do manifesto `package.json` (onde a dependência `mqtt` é declarada).
- Documentação existente em `README.md` e em `funcionalidades/*/README.md`.

## Saídas (artefatos obrigatórios)
- Ajuste em `config_flow.py` eliminando o `AttributeError` ao abrir o fluxo de opções do Home Assistant.
- Atualização do `package.json` para usar a versão mais recente de `mqtt` e adaptações necessárias em `src/mqtt.js` para garantir compatibilidade.
- Atualização dos READMEs (raiz e funcionalidades) com as novidades do MQTT atualizado e o troubleshooting do Options Flow Tuya, mantendo índice navegável e árvore de documentação.
- Registros consistentes em `codex/improved-prompt.md`, `codex/suggest.md`, `codex/executed.md` e `codex/error.md`.

## Passo a passo (alto nível)
1. Ler `codex/request.md` e identificar os erros solicitados.
2. Corrigir `custom_components/prudentes_tuya_all/config_flow.py` para usar atributos compatíveis com o Options Flow atual (sem acessar `config_entry.hass`).
3. Atualizar `package.json` para a versão mais recente de `mqtt` e ajustar `src/mqtt.js` para explicitar a negociação de protocolo com o broker.
4. Revisar e enriquecer `README.md` e `funcionalidades/*/README.md` com árvore de documentação, referências cruzadas e orientações de troubleshooting do Options Flow e do MQTT atualizado.
5. Preencher `codex/suggest.md` com variações e melhorias; `codex/executed.md` com o que foi feito; `codex/error.md` com limitações encontradas.

## Restrições e políticas
- Escrever em português (pt-BR), preservando termos técnicos em inglês quando necessário.
- Não remover conteúdos válidos; apenas complementar ou corrigir mantendo rastreabilidade.
- Garantir que os arquivos `codex/*` reflitam decisões, ações e limitações desta execução.

## Critérios de aceite
- Fluxo de opções do Home Assistant abre sem `AttributeError` para `config_entry`.
- Dependência `mqtt` atualizada para a versão mais recente, com código compatível e documentação refletindo a mudança.
- READMEs atualizados com índice, árvore de documentação e troubleshooting dos problemas relatados.
- `codex/suggest.md` contém pelo menos 5 sugestões; `codex/executed.md` descreve ações e verificações; `codex/error.md` lista limitações (incluindo impossibilidade de testes Docker neste ambiente).

## Validações automáticas (quando aplicável)
- [ ] `python -m compileall custom_components/prudentes_tuya_all`
- [ ] `npm run lint`
- [ ] Build opcional do Docker (`docker compose build`), quando disponível
