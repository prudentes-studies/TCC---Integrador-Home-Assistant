# GPT‑5 Codex — Orquestração de Execução (`codex/prompt.md`)

> **Propósito:** Este arquivo **orienta o GPT‑5 Codex** a ler e **executar integralmente** o que está descrito em `codex/request.md`, a **refinar o prompt** original e a **registrar** resultados, sugestões, erros e documentação do projeto.

---

## 1) Tarefas obrigatórias (em ordem)

1. **Ler e entender `codex/request.md`.**
   - Extraia objetivos, escopo, entradas, saídas, restrições e critérios de aceite.
   - Se `request.md` não existir ou estiver vazio, **registre** em `codex/error.md` e **sugira** em `codex/suggest.md` um esqueleto mínimo.

2. **Executar integralmente as tarefas descritas em `codex/request.md`.**
   - Respeite fielmente requisitos, priorizações e formatos pedidos.
   - Se alguma tarefa for **não executável** neste ambiente (ex.: acesso a rede/FS externo), **simule o plano** e **entregue artefatos textuais** equivalentes, registrando a limitação em `codex/error.md`.

3. **Gerar um novo texto “equivalente em intenção” ao conteúdo de `codex/request.md`, porém**
   **mais bem redigido, claro, coeso e pronto para uso direto como prompt.**
   - **Salvar** como `codex/improved-prompt.md` (UTF‑8, Markdown).
   - O improved‑prompt deve ser **autossuficiente** (inclui contexto, entradas, saídas, passos, critérios de aceite e validações).

4. **Registrar sugestões de melhoria/variações do prompt** em `codex/suggest.md`.
   - Inclua variações por objetivo, detalhe, formato, risco e custo/benefício.

5. **Registrar o que foi executado** em `codex/executed.md`.
   - Faça um **sumário detalhado**, incluindo: interpretação de requisitos, decisões, artefatos gerados/alterados, checagens de qualidade, testes (quando aplicável) e próximos passos.

6. **Registrar erros/limitações/partes não executáveis** em `codex/error.md`.
   - Para cada item, traga **causa**, **efeito**, **workaround** e **ação recomendada**.

7. **Atualizar `README.md`** com **documentação ultra detalhada**:
   - Instruções de uso, **árvore de documentação** e **índice navegável**.
   - **Cada funcionalidade** deve residir em **uma pasta própria**, “envelopada”, com **seu próprio `README.md`** (que deve ser atualizado sempre) e **referenciada** no `README.md` geral.
   - Se as pastas ainda **não existirem**, descreva a **estrutura proposta** e inclua **READMEs de esqueleto** (em texto) com objetivos, entradas/saídas e pontos de extensão.

---

## 2) Regras gerais de execução

- **Idioma:** escreva todos os arquivos em **Português (pt‑BR)**, salvo trechos técnicos/nomes próprios.
- **Determinismo:** siga as seções e templates abaixo para garantir **consistência** entre execuções.
- **Não destrutivo:** **apenas adicione/atualize** os arquivos listados; não remova conteúdo válido sem motivo documentado.
- **Paths e encoding:** use caminhos **relativos ao repositório** e **UTF‑8**.
- **Sem alucinação:** quando um dado não estiver disponível, **declare a ausência**, proponha **alternativas** e registre em `codex/error.md`.
- **Validação:** aplique a **checklist** de aceite (seção 5) antes de finalizar.
- **Rastreabilidade:** mantenha referências cruzadas entre `improved-prompt.md`, `executed.md`, `error.md` e `README.md`.

---

## 3) Estrutura/saídas esperadas (arquivos)

```
/codex/request.md                # entrada (fornecida pelo usuário/projeto)
/codex/improved-prompt.md        # prompt reescrito, autossuficiente
/codex/suggest.md                # sugestões e variações do prompt
/codex/executed.md               # resumo detalhado da execução
/codex/error.md                  # erros, limitações e itens não executáveis
/README.md (ou README.md)        # documentação principal atualizada
/funcionalidades/<nome>/README.md# documentação por funcionalidade (quando aplicável)
```

> Observação: se não for possível criar arquivos/pastas reais, **inclua os conteúdos completos como blocos Markdown**
> dentro de `codex/executed.md`, com títulos claros e caminhos simulados; registre a limitação em `codex/error.md`.

---

## 4) Templates mínimos (use/adapte conforme o contexto)

### 4.1 `codex/improved-prompt.md`
```md
# Prompt – Versão Aprimorada

## Objetivo
(Explique, em 1–3 parágrafos, o objetivo geral do trabalho.)

## Entradas
- Arquivo(s): ...
- Parâmetros: ...

## Saídas (artefatos obrigatórios)
- ...

## Passo a passo (alto nível)
1. ...
2. ...

## Restrições e políticas
- ...

## Critérios de aceite
- ...

## Validações automáticas (quando aplicável)
- [ ] Arquivos gerados existem e não estão vazios
- [ ] Estrutura/formatos conforme especificação
- [ ] ...
```

### 4.2 `codex/suggest.md`
```md
# Sugestões e Variações do Prompt

## Melhorias incrementais
- ...

## Variações por objetivo/escopo
- ...

## Ajustes de risco/custo
- ...
```

### 4.3 `codex/executed.md`
```md
# Execução — Resumo Detalhado

## Contexto
- Data/hora: <preencha>
- Fonte: codex/request.md
- Versão desta execução: <hash/ID opcional>

## Interpretação do pedido
- ...

## Ações realizadas
- ...

## Artefatos gerados/atualizados
- `codex/improved-prompt.md` — ...
- `codex/suggest.md` — ...
- `codex/error.md` — ...
- `README.md` — ...
- (Outros) — ...

## Testes/checagens
- ...

## Próximos passos recomendados
- ...
```

### 4.4 `codex/error.md`
```md
# Erros, Limitações e Itens Não Executáveis

| ID | Tipo        | Descrição curta | Causa raiz | Efeito | Workaround/Plano | Status |
|----|-------------|-----------------|-----------|--------|------------------|--------|
| E1 | Limitação   | ...             | ...       | ...    | ...              | Aberto |
```

### 4.5 `README.md` (orientações de atualização)
- **Resumo do projeto**, **como usar**, **pré‑requisitos**, **variáveis/configuração**, **comandos comuns**.
- **Árvore de documentação** com links para cada **funcionalidade** em `/funcionalidades/<nome>/README.md`.
- **Padrões de contribuição** (convenções de branch/commit, revisão, testes).
- **Histórico de versões** (changelog breve) e **roadmap**.
- **Anexos** (diagramas, exemplos, FAQs, troubleshooting).

---

## 5) Checklist de qualidade (antes de finalizar)

- [ ] `codex/improved-prompt.md` está **claro, coeso e autossuficiente**.
- [ ] `codex/suggest.md` contém **pelo menos 5** melhorias/variações úteis.
- [ ] `codex/executed.md` descreve **o que foi feito** de forma **auditável**.
- [ ] `codex/error.md` lista **todas** as limitações encontradas (se houver).
- [ ] `README.md` foi **atualizado** com árvore de documentação e referências cruzadas.
- [ ] Todos os arquivos estão em **UTF‑8** e bem formatados (Markdown).

---

## 6) Notas finais de operação

- Se `codex/request.md` for **um prompt mal estruturado**, normalize e explique decisões de reescrita em `executed.md`.
- Se houver **conflitos** entre `request.md` e este guia, **priorize `request.md`**, registrando o conflito em `error.md`.
- Em ambientes sem escrita em disco, **retorne todos os artefatos em texto** dentro da própria resposta, preservando os caminhos.
