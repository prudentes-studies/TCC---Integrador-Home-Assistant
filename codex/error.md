# Erros, Limitações e Itens Não Executáveis

| ID | Tipo | Descrição curta | Causa raiz | Efeito | Workaround/Plano | Status |
|----|------|-----------------|-----------|--------|------------------|--------|
| E1 | Limitação | Correção não validada em HA real/HACS | Ambiente de execução sem instância do Home Assistant para abrir o fluxo de opções | Não foi possível comprovar in loco a eliminação do `AttributeError` ou o carregamento das entidades | Aplicar o patch em um HA de testes, abrir **Configure** e verificar ausência de stack trace; ativar logs debug se necessário | Aberto |
| E2 | Limitação | Aviso de performance `sun.sun` não reproduzido | Falta de ambiente com entidade `sun.sun` ativa para medir tempo de atualização | Não há confirmação se o aviso persiste após correções; pode ser ruído isolado | Monitorar logs após atualização e abrir issue upstream se recorrente | Aberto |
| E3 | Limitação | Testes automatizados ausentes para o fluxo de opções | Não há suíte configurada cobrindo inicialização/normalização | Possíveis regressões futuras sem detecção imediata | Implementar testes unitários/pytest para o OptionsFlow | Aberto |
