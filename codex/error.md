# Erros, Limitações e Itens Não Executáveis

| ID | Tipo | Descrição curta | Causa raiz | Efeito | Workaround/Plano | Status |
|----|------|-----------------|-----------|--------|------------------|--------|
| E1 | Limitação | APIs Tuya não exercitadas end-to-end | Ambiente offline/sem credenciais reais durante a execução | Fluxo de descoberta e assinatura não foi validado contra a nuvem Tuya | Testar com credenciais do Tuya Developer em ambiente de HA real; habilitar logs debug do `TuyaClient` | Aberto |
| E2 | Limitação | Testes automatizados ausentes para as novas entidades dinâmicas | Foco na implementação e documentação; sem suíte de testes configurada | Possível regressão não detectada em mapeamento de tipos/envio de comandos | Implementar pytest/unittest cobrindo assinatura, paginação e criação de entidades | Aberto |
