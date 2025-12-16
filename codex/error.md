# Erros, Limitações e Itens Não Executáveis

| ID | Tipo | Descrição curta | Causa raiz | Efeito | Workaround/Plano | Status |
|----|------|-----------------|-----------|--------|------------------|--------|
| E1 | Limitação | Não foi possível validar o Options Flow no Home Assistant real | Ambiente atual não possui instância HA/HACS para abrir **Configure** | Ausência de comprovação prática da correção do erro 500 | Aplicar o patch em um HA de testes, abrir **Configure** e monitorar logs | Aberto |
| E2 | Limitação | Teste de descoberta Tuya não executado | Segredos `TUYA_*` não foram fornecidos neste ambiente | `scripts/ci_tuya_discovery.py` não retornou contagem real de devices | Preencher `TUYA_ACCESS_ID`, `TUYA_ACCESS_SECRET`, `TUYA_REGION` (e opcional `TUYA_BASE_URL`) no CI e reexecutar | Aberto |
| E3 | Limitação | Imagens Docker não buildadas localmente | Execução não subiu Docker/Compose no ambiente de CI local | Não há validação real das novas tags `node:20-alpine` neste host | Usar o job `docker-smoke` no GitHub Actions ou rodar `docker compose build --pull` no host do usuário | Aberto |
