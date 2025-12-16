# Erros, Limitações e Itens Não Executáveis

| ID | Tipo        | Descrição curta | Causa raiz | Efeito | Workaround/Plano | Status |
|----|-------------|-----------------|-----------|--------|------------------|--------|
| E1 | Limitação   | Discovery não executado contra a Tuya Cloud real | Credenciais/segredos `TUYA_CLIENT_ID`/`TUYA_CLIENT_SECRET` não fornecidos neste ambiente | Sem geração real de `output/tuya_inventory.json` com dados de produção | Executar `python scripts/tuya_discover.py` em ambiente com segredos válidos ou usar fixtures de teste | Aberto |
