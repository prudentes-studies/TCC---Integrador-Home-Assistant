# Prompt – Versão Aprimorada

## Objetivo
Corrigir a integração customizada `prudentes_tuya_all` do Home Assistant para que o fluxo de opções não dispare erro `AttributeError: property 'config_entry' of 'TuyaOptionsFlowHandler' object has no setter`, permitindo o carregamento correto das entidades. Documentar o procedimento de correção, possíveis causas dos avisos de desempenho (ex.: `sun.sun` demorando 0.9s) e registrar rastreabilidade completa nos artefatos `codex/*` e na documentação principal.

## Entradas
- `codex/request.md` com descrição dos erros observados na UI e no log do Home Assistant.
- Código da integração em `custom_components/prudentes_tuya_all/`, especialmente `config_flow.py`.
- Documentação existente em `README.md` e `funcionalidades/tuya-integration/README.md`.

## Saídas (artefatos obrigatórios)
- Correção no fluxo de opções da integração, eliminando o `AttributeError` e garantindo normalização segura da lista de dispositivos.
- Atualizações de documentação em `README.md` e `funcionalidades/tuya-integration/README.md` com passos de validação e troubleshooting dos erros reportados.
- Arquivos de rastreabilidade atualizados: `codex/improved-prompt.md`, `codex/suggest.md`, `codex/executed.md`, `codex/error.md`.

## Passo a passo (alto nível)
1. Ler `codex/request.md` e mapear os erros relatados (entidades não carregam; stack trace em `config_flow.py`; aviso de desempenho `sun.sun`).
2. Inspecionar `config_flow.py` e ajustar o `OptionsFlow` para usar inicialização correta (`super().__init__`) e sanitizar `device_ids` tanto para defaults quanto para entrada do usuário.
3. Rever documentação para incluir passos de atualização da integração, limpeza de cache e validações pós-correção.
4. Registrar sugestões alternativas em `codex/suggest.md` e detalhar execução em `codex/executed.md`.
5. Listar limitações ou itens não reproduzidos em `codex/error.md` (ex.: impossibilidade de validar no HA real nesta execução).

## Restrições e políticas
- Escrever textos em português (pt-BR), mantendo termos técnicos em inglês quando apropriado.
- Não remover conteúdo válido; apenas complementar ou corrigir.
- Manter rastreabilidade cruzada entre `improved-prompt`, `executed`, `suggest` e `error`.

## Critérios de aceite
- O fluxo de opções da integração não lança mais o `AttributeError` e aceita listas de devices em branco ou string, normalizando-as corretamente.
- Documentação principal e específica da funcionalidade contém seção de troubleshooting que explique a correção e como validar o carregamento de entidades.
- `codex/suggest.md` traz ao menos 5 melhorias/variações relevantes ao cenário de erro e manutenção.
- `codex/executed.md` descreve claramente o que foi feito, limitações e próximos passos.

## Validações automáticas (quando aplicável)
- [ ] `python -m compileall custom_components/prudentes_tuya_all` executado sem erros.
- [ ] Verificação manual de que a opção "Configure" da integração abre sem traçar `AttributeError` e que os defaults de Device IDs são exibidos corretamente (simulada se não houver HA disponível).
