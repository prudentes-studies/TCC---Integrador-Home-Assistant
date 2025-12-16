# Sugestões e Variações do Prompt

## Melhorias incrementais
- Incluir validação automática do JSON gerado (`artifacts/tuya-entities-map.json`) contra um schema para evitar campos ausentes ou tipos incorretos.
- Pedir logging estruturado (requestId, deviceId, rota) e máscara de `client_secret` em todos os níveis de debug.
- Solicitar que o comando de discovery aceite filtro por `category`/`productId` para rodadas rápidas de teste.
- Acrescentar requisito para fallback quando `/model` retornar erro: continuar com specifications/status e registrar aviso.
- Exigir que o pipeline salve estatísticas agregadas (média de entidades por device, quantos ro vs rw) no console e no artefato.

## Variações por objetivo/escopo
- Versão focada em Home Assistant: produzir também YAML de entities simuladas para importação manual no HA.
- Versão focada em CI: rodar discovery em modo "dry run" com fixtures e snapshots para evitar dependência de segredos.
- Versão enxuta: apenas normalizar `dpId/dp_id` e `values` em um serviço independente, sem CLI.
- Versão exploratória: exportar heurísticas em formato explicável (feature importance) e permitir ajuste via arquivo de regras.

## Ajustes de risco/custo
- Adicionar opção `--max-devices` no CLI para limitar consumo de API em ambientes com rate limit agressivo.
- Prever reexecução parcial reusando cache de devices/status para evitar hitting constante do token endpoint.
- Incluir instrução para rodar testes offline usando mocks de HTTP client quando o acesso à Tuya Cloud estiver bloqueado.
