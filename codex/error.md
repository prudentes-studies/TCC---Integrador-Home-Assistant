# Erros, Limitações e Itens Não Executáveis

| ID | Tipo        | Descrição curta | Causa raiz | Efeito | Workaround/Plano | Status |
|----|-------------|-----------------|-----------|--------|------------------|--------|
| E1 | Limitação   | Não foi possível validar o HiveMQ Control Center (porta 8080) via Docker | Ambiente não possui Docker instalado/executável (`bash: command not found: docker`) | Sem evidência prática de que a tag fixada resolve o erro interno reportado | Orientar usuário a rodar `docker compose pull && docker compose up -d` em ambiente com Docker e consultar logs do serviço `mqtt-broker` | Aberto |
