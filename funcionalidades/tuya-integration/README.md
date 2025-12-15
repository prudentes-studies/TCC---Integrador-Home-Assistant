# Integração Home Assistant `prudentes_tuya_all`

## Objetivo
Expor todos os datapoints Tuya Cloud via Home Assistant, criando entidades dinâmicas por DP e sensor diagnóstico por dispositivo.

## Entradas
- Credenciais Tuya Developer Cloud (Access ID/Secret, Base URL, Região).
- Lista de `device_ids` ou `uids` Tuya.

## Como instalar
1. Copie `custom_components/prudentes_tuya_all` para `config/custom_components/prudentes_tuya_all` no HA.
2. Reinicie o HA e adicione a integração via UI.
3. Informe credenciais, base URL e device_ids separados por vírgula.
4. Ajuste o polling nas opções e, se necessário, desabilite DPs específicos.

## Plataformas
- `sensor`: um sensor por DP + sensor diagnóstico com atributos completos.
- `switch` e `binary_sensor`: mapeamento básico para DPs booleanos (write/read conforme suporte do device).
- `number`: valores numéricos com escrita direta.
- `select`: strings/enums com escrita direta.

## Pontos de extensão
- Ler o schema do endpoint `/specification` para decidir writability com maior precisão.
- Persistir cache de tokens/assinaturas Tuya.
- Acrescentar testes e validação de tipos por DP.
