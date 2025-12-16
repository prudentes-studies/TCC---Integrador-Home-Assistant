# Prompt – Versão Aprimorada

## Objetivo
Reestruturar a integração **`prudentes_tuya_all`** para que seja uma réplica fidedigna (clean code, comentários em pt-BR e documentação completa) do projeto **hass-localtuya** (`https://github.com/xZetsubou/hass-localtuya`), preservando todas as funcionalidades originais. Incluir ainda instruções passo a passo para integrar dispositivos **Broadlink** ao **Node-RED** no Home Assistant e documentar tudo no repositório.

## Entradas
- Arquivo de referência: `codex/request.md`.
- Repositório de origem: `https://github.com/xZetsubou/hass-localtuya` (código e funcionalidades a serem espelhados).
- Base existente do repositório atual (`custom_components/prudentes_tuya_all` e docs correlatas).
- Ferramentas e dependências locais disponíveis (Python/Home Assistant; Node-RED/Broadlink para documentação).

## Saídas (artefatos obrigatórios)
- Código da integração `prudentes_tuya_all` alinhado ao hass-localtuya: plataformas, entidades, fluxos de configuração/opções e suporte a DP/lan/Cloud equivalentes, com comentários em português e clean code.
- Documentação ampliada em `README.md` e em READMEs por funcionalidade, incluindo um guia detalhado de integração Broadlink + Node-RED no Home Assistant.
- Registro de execução (`codex/executed.md`), erros/limitações (`codex/error.md`) e sugestões de melhoria (`codex/suggest.md`).
- Estrutura de funcionalidades com READMEs dedicados (Tuya, MQTT/dashboard, Broadlink+Node-RED) linkada no `README.md` principal.

## Passo a passo (alto nível)
1. Mapear funcionalidades do hass-localtuya: plataformas suportadas, discovery, fluxo de opções, tratamento de DP Codes/IDs, gerenciamento de conexão LAN e caches.
2. Portar/alinhar o código da integração `prudentes_tuya_all` para equivalência funcional, aplicando clean code e comentários em pt-BR. Registrar gaps ou itens não portados.
3. Atualizar/expandir documentação: visão geral da integração, cobertura de funcionalidades trazidas do hass-localtuya, limites conhecidos e exemplos de configuração.
4. Criar guia passo a passo para integração Broadlink + Node-RED no Home Assistant e referenciar no `README.md` e em `funcionalidades/broadlink-nodered/README.md`.
5. Preencher `codex/executed.md`, `codex/suggest.md` e `codex/error.md` com rastreabilidade, sugestões e limitações encontradas.
6. Revisar checklist de qualidade e validar links/estrutura de documentação.

## Restrições e políticas
- Comentários e documentação em **pt-BR**; nomes de APIs/DPs mantidos conforme origem.
- Sem hardcode de credenciais; uso de variáveis/configs padrão do Home Assistant.
- Preservar compatibilidade com estruturas/DPs esperadas pelo hass-localtuya.
- Não remover funcionalidades existentes; apenas alinhar/adicionar e documentar gaps.

## Critérios de aceite
- Plataformas e funcionalidades do hass-localtuya mapeadas e refletidas (ou registradas como gap) em `prudentes_tuya_all`.
- Documentação principal descreve como usar a integração, o mapeamento de features trazidas do hass-localtuya e o guia Broadlink + Node-RED.
- READMEs por funcionalidade existentes e referenciados na árvore de documentação.
- `codex/*` atualizados com execução, sugestões e limitações.

## Validações automáticas (quando aplicável)
- [ ] Linters/testes da integração executados ou documentados.
- [ ] Links de documentação funcionando e árvore de funcionalidades atualizada.
- [ ] Guia Broadlink + Node-RED revisado e referenciado no `README.md`.
