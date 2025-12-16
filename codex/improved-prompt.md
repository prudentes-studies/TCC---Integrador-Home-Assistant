# Prompt – Versão Aprimorada

## Objetivo
Garantir que toda a stack do projeto (Dockerfiles e serviços do docker-compose) utilize sempre as imagens mais recentes e estáveis (tag `latest`), e transformar os tutoriais existentes nos READMEs em guias clique a clique ultradetalhados para execução da stack, uso do dashboard MQTT e instalação da integração Tuya no Home Assistant.

## Entradas
- `codex/request.md` (escopo original).
- Estado atual do repositório com Dockerfiles, `docker-compose.yml` e READMEs em `README.md` e `funcionalidades/*/README.md`.

## Saídas (artefatos obrigatórios)
- `Dockerfile` e `Dockerfile.demo` usando imagem base Node com tag `latest` (preferencialmente variante leve).
- `docker-compose.yml` com serviços configurados para usar imagens `latest` ou estáveis atuais.
- `README.md` principal com tutoriais passo a passo (stack Docker, dashboard, VirtualBox + Home Assistant, integração Tuya) e índice para READMEs de funcionalidades.
- READMEs das funcionalidades (`funcionalidades/mqtt-dashboard/README.md`, `funcionalidades/tuya-integration/README.md`) reescritos com instruções clique a clique.
- Arquivos de rastreio atualizados: `codex/improved-prompt.md`, `codex/suggest.md`, `codex/executed.md`, `codex/error.md`.

## Passo a passo (alto nível)
1. Ler `codex/request.md` para extrair requisitos de atualização de imagens e melhoria de tutoriais.
2. Atualizar Dockerfiles para usar `node:latest` (variante leve) mantendo comandos existentes.
3. Ajustar `docker-compose.yml` para que todos os serviços utilizem imagens `latest` (ou a versão mais recente estável disponível) e alinhar comentários.
4. Reescrever `README.md` com guias clique a clique para subir a stack Docker, operar o dashboard, configurar HA no VirtualBox e instalar a integração Tuya; incluir índice e referências para READMEs de funcionalidades.
5. Reescrever READMEs em `funcionalidades/*` com passos detalhados (comandos, cliques e confirmações visuais) para uso de cada módulo.
6. Documentar execução em `codex/executed.md`, sugestões em `codex/suggest.md` e limitações/erros em `codex/error.md`.

## Restrições e políticas
- Linguagem: português (pt-BR) nos textos; nomes técnicos mantêm idioma original.
- Não remover conteúdo válido; apenas atualizar e complementar.
- Manter caminhos relativos e encoding UTF-8.
- Se algo não puder ser executado, registrar em `codex/error.md` com causa e workaround.

## Critérios de aceite
- Dockerfiles e `docker-compose.yml` referenciam tags `latest` (ou a versão estável mais recente disponível) para cada imagem.
- Tutoriais em todos os READMEs apresentam passos numerados clique a clique, comandos prontos para uso e validações finais.
- `README.md` contém índice navegável e links para cada funcionalidade.
- `codex/suggest.md` lista pelo menos 5 sugestões/variações úteis.
- `codex/executed.md` resume o trabalho realizado e relaciona os artefatos atualizados.

## Validações automáticas
- [ ] Dockerfiles usam `latest` no `FROM`.
- [ ] `docker-compose.yml` referencia imagens com `latest` (quando aplicável).
- [ ] READMEs contêm passos numerados e links para funcionalidades.
- [ ] Arquivos `codex/*` atualizados com execução, sugestões e erros (se houver).
