# Erros, Limitações e Itens Não Executáveis

| ID | Tipo        | Descrição curta | Causa raiz | Efeito | Workaround/Plano | Status |
|----|-------------|-----------------|-----------|--------|------------------|--------|
| E1 | Limitação   | Não foi possível validar o HiveMQ Control Center (porta 8080) via Docker | Ambiente não possui Docker instalado/executável (`bash: command not found: docker`) | Sem evidência prática de que a tag fixada resolve o erro interno reportado | Orientar usuário a rodar `docker compose pull && docker compose up -d` em ambiente com Docker e consultar logs do serviço `mqtt-broker` | Aberto |
| E2 | Limitação   | Fluxo de opções da integração Tuya não testado em instância real do Home Assistant | Ambiente não possui Home Assistant disponível para abrir **Configure** | Validação do `AttributeError` depende de teste manual | Aplicar atualização via HACS no HA do usuário e confirmar abertura de **Configure** sem erro; coletar logs se persistir | Aberto |
| E3 | Limitação   | Discovery Tuya não executado contra APIs reais | Ambiente sem credenciais `TUYA_*` para autenticar no Tuya Cloud | Artefato JSON e heurísticas não foram validados com devices reais | Rodar `npm run tuya:discover` com segredos reais e revisar o log/JSON; ajustar heurísticas conforme retorno | Aberto |
