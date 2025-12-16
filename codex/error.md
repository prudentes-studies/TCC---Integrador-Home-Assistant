# Erros, Limitações e Itens Não Executáveis

| ID | Tipo | Descrição curta | Causa raiz | Efeito | Workaround/Plano | Status |
|----|------|-----------------|-----------|--------|------------------|--------|
| E1 | Limitação | Testes automatizados não executados após atualizar imagens e docs | Ambiente atual sem dependências configuradas e tempo focado em documentação | Sem validação automática do build e da integração HA/MQTT | Executar `docker compose up` e rodar testes manuais/Jest/pytest em ambiente local | Aberto |
