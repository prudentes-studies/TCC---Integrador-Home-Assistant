# Prompt – Versão Aprimorada

## Objetivo
Corrigir falhas reportadas em `codex/request.md`, garantindo que a integração `prudentes_tuya_all` não gere erro 500 ao abrir o fluxo de opções, que o build Docker funcione com imagens válidas e que exista uma esteira CI/CD cobrindo app Node, componente HA e discovery Tuya. Entregar documentação detalhada e rastreável, mantendo todos os arquivos `codex/*` e `README.md` atualizados.

## Entradas
- `codex/request.md` com o stack trace do `TypeError` no Options Flow e o log de falha de build do `node:latest-alpine`.
- Código da integração em `custom_components/prudentes_tuya_all/`, especialmente `config_flow.py`.
- Dockerfiles (`Dockerfile`, `Dockerfile.demo`) e `docker-compose.yml`.
- Documentação existente em `README.md` e `funcionalidades/tuya-integration/README.md`.

## Saídas (artefatos obrigatórios)
- Patch em `config_flow.py` eliminando o `TypeError` na inicialização do Options Flow e garantindo normalização dos IDs.
- Dockerfiles ajustados para tags válidas e compose sem atributo `version` obsoleto.
- Pipeline CI/CD em `.github/workflows/ci.yml` com lint Node, compileall do componente e teste opcional de descoberta Tuya usando segredos.
- Script auxiliar `scripts/ci_tuya_discovery.py` para validar listagem de devices quando segredos são fornecidos.
- Documentação atualizada (`README.md`, `funcionalidades/tuya-integration/README.md`) descrevendo as correções, o uso da pipeline e os segredos necessários.
- Rastreabilidade completa em `codex/improved-prompt.md`, `codex/suggest.md`, `codex/executed.md`, `codex/error.md`.

## Passo a passo (alto nível)
1. Ler `codex/request.md` e mapear erros: TypeError no Options Flow, build do `node:latest-alpine` e necessidade de CI/CD para descoberta de entidades.
2. Corrigir `config_flow.py` para inicializar o Options Flow sem chamar `super().__init__` com argumentos e manter `config_entry`/`hass` acessíveis.
3. Atualizar Dockerfiles para `node:20-alpine` e remover `version` obsoleto do `docker-compose.yml`.
4. Criar workflow GitHub Actions com jobs: lint Node (npm ci + lint), compileall do componente e teste opcional de descoberta Tuya com segredos; build Docker smoke.
5. Adicionar script `scripts/ci_tuya_discovery.py` que só roda quando segredos `TUYA_*` estão presentes e retorna contagem de devices.
6. Atualizar READMEs com árvore de documentação, instruções de CI/CD, segredos requeridos e troubleshooting dos erros relatados.
7. Registrar execução, sugestões e limitações nos arquivos `codex/*` conforme templates.

## Restrições e políticas
- Idioma: português (pt-BR) mantendo termos técnicos em inglês quando adequado.
- Não remover conteúdo válido; apenas complementar ou corrigir.
- Garantir rastreabilidade cruzada entre `improved-prompt`, `executed`, `suggest` e `error`.
- Preferir tags Docker fixas e compatíveis com o `package.json` (`engines: node >=20`).

## Critérios de aceite
- Options Flow abre sem lançar `TypeError` e mantém lista de devices normalizada.
- Build Docker não falha por tag inexistente e o compose não emite alerta de `version` obsoleto.
- Pipeline CI/CD executa passos descritos e documenta claramente quais segredos são necessários para testar a descoberta automática.
- READMEs trazem índice navegável, árvore de documentação e troubleshooting dos erros de request.
- `codex/suggest.md` contém pelo menos 5 variações/melhorias úteis; `codex/executed.md` detalha ações e limitações; `codex/error.md` registra itens não testados.

## Validações automáticas (quando aplicável)
- [ ] `python -m compileall custom_components/prudentes_tuya_all`
- [ ] `npm run lint`
- [ ] `docker build` para Dockerfile e Dockerfile.demo
- [ ] Execução de `scripts/ci_tuya_discovery.py` quando segredos `TUYA_*` estiverem disponíveis
