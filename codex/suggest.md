# Sugestões e Variações do Prompt

## Melhorias incrementais
- Incluir um checklist explícito para validar o Options Flow após atualizar dependências do Home Assistant, garantindo que atributos privados não sejam acessados diretamente.
- Pedir confirmação da versão da biblioteca `mqtt` com `npm view mqtt version` e registro no README de quando a dependência for atualizada.
- Acrescentar cenário de teste para o Options Flow simulando `config_entry.options` preenchido para garantir normalização dos `device_ids`.
- Registrar no prompt um passo de verificação de conflitos de portas (8080/1883) antes de iniciar o Docker e ao atualizar o broker.
- Solicitar que `README.md` inclua exemplos de `docker compose` usando portas alternativas para ambientes com restrição corporativa.

## Variações por objetivo/escopo
- Focar apenas em documentação: gerar guias passo a passo para subir a stack e coletar evidências sem modificar código.
- Priorizar automação: criar scripts de healthcheck (MQTT e HA) e integrá-los ao CI em vez de alterar manualmente compose/config_flow.
- Orientar migração: substituir HiveMQ por Mosquitto + Web UI e ajustar o dashboard para novo broker.
- Tornar o prompt prescritivo para testes: exigir execução de `python -m compileall` e `npm run lint` com saída anexada.

## Ajustes de risco/custo
- Oferecer opção de simulação quando o ambiente não suporta Docker, detalhando como validar as rotas manualmente.
- Prever rollback: instruir a manter a tag anterior do HiveMQ como fallback (`hivemq/hivemq-ce:latest`) caso a versão fixada não esteja disponível no registry local.
- Solicitar checkpoints intermediários (commits/PRs) para cada correção (Docker e integração) reduzindo risco de regressão cruzada.
