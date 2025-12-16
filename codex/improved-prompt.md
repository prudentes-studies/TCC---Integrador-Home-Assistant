# Prompt – Versão Aprimorada

## Objetivo
Implementar uma integração Tuya para Home Assistant que seja instalada como repositório Git externo (via HACS), eliminando cópia manual para `config/custom_components`. O código deve obter dinamicamente o schema e os tipos dos dispositivos a partir das APIs do Tuya Developer, criando entidades conforme `shadow`, `specification`, `functions` e `status`. A documentação precisa trazer tutoriais **clique a clique** extremamente detalhados e um índice navegável por funcionalidades.

## Entradas
- `codex/request.md` com o pedido original.
- Código existente da integração em `custom_components/prudentes_tuya_all`.
- Documentação atual em `README.md` e `funcionalidades/*/README.md`.

## Saídas (artefatos obrigatórios)
- Integração Home Assistant preparada para instalação como repositório externo (ex.: arquivo `hacs.json`).
- Cliente Tuya capaz de autenticar, paginar devices (`/v2.0/cloud/thing/device`) e buscar shadow/specification por device.
- Coordenação que descobre devices automaticamente quando não informados e cria entidades com base em tipos retornados pela API.
- Tutoriais clique a clique atualizados em `README.md` e `funcionalidades/tuya-integration/README.md`, indicando instalação via HACS e operação dinâmica.
- Arquivos de rastreabilidade atualizados: `codex/improved-prompt.md`, `codex/suggest.md`, `codex/executed.md`, `codex/error.md`.

## Passo a passo (alto nível)
1. Ler `codex/request.md` para extrair requisitos (instalação via repositório Git externo, tutoriais ultra detalhados, leitura dinâmica da Tuya API).
2. Ajustar cliente e coordinator para: obter token (`/v1.0/token`), paginar devices com `last_row_key`, consultar shadow/propriedades e specification para mapear tipos.
3. Atualizar fluxos de configuração para aceitar lista vazia e disparar descoberta automática de devices.
4. Gerar entidades (switch, binary_sensor, number, select, sensor) de acordo com `functions` (writable) e `status` (read-only) do schema retornado.
5. Preparar repositório para instalação via HACS (ex.: `hacs.json`) e remover dependência de cópia manual.
6. Reescrever READMEs com tutoriais clique a clique e índice navegável de funcionalidades.
7. Registrar execução em `codex/executed.md`, sugestões em `codex/suggest.md` e limitações em `codex/error.md`.

## Restrições e políticas
- Linguagem: português (pt-BR) nos textos; nomes técnicos mantêm idioma original.
- Não remover conteúdo válido; apenas atualizar/complementar.
- Declarar limitações em `codex/error.md` se algo não puder ser executado.

## Critérios de aceite
- Instalação documentada via repositório Git/HACS, sem instruir copiar para `config/custom_components`.
- Device IDs podem ser deixados em branco e são descobertos via API com paginação `last_row_key`.
- Entidades criadas conforme tipos retornados (`bool`, `enum/string`, `value/integer/float`) e writability (`functions` vs `status`).
- READMEs contêm passos numerados, cliques e validações finais; índice com links para funcionalidades.
- `codex/suggest.md` tem pelo menos 5 sugestões; `codex/executed.md` descreve ações realizadas.

## Validações automáticas (quando aplicável)
- [ ] Habilitar instalação via HACS (`hacs.json` presente) e documentada.
- [ ] Cliente Tuya obtém token e assina chamadas.
- [ ] Coordinator busca shadow + specification e cria entidades dinâmicas.
- [ ] READMEs incluem tutoriais clique a clique e índice navegável.
- [ ] Arquivos `codex/*` atualizados.
