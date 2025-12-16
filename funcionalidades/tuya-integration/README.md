# Integração Home Assistant `prudentes_tuya_all`

## Objetivo
Expor todos os datapoints Tuya Cloud via Home Assistant, criando entidades dinâmicas por DP e sensor diagnóstico por dispositivo. Todas as imagens e contêineres associados usam tags `latest` para permanecer atualizados.

## Pré-requisitos
- Home Assistant OS ativo (recomendado IP fixo `10.10.10.100`).
- Acesso ao **Tuya Developer Cloud** com `Access ID`, `Access Secret`, `Base URL` e `Região` válidos.
- Pasta `config/custom_components` acessível (via File Editor ou SSH).

## Passo a passo clique a clique (instalação)
1. **Copiar os arquivos do componente**
   - No repositório local, localize `custom_components/prudentes_tuya_all`.
   - No Home Assistant, abra o addon **File Editor** → navegue até `/config` → se não existir, crie a pasta `custom_components`.
   - Clique em **Upload** e envie toda a pasta `prudentes_tuya_all` (ou arraste via cliente SSH/SCP).
2. **Reiniciar o Home Assistant**
   - Vá em **Settings > System > Restart**.
   - Confirme o prompt e aguarde o retorno da interface.
3. **Adicionar a integração**
   - Acesse **Settings > Devices & Services** e clique em **Add Integration**.
   - Busque por **Prudentes Tuya All** e selecione.
   - Preencha os campos:
     - **Tuya Access ID** e **Tuya Access Secret**: valores do Tuya Cloud.
     - **Região**: ex.: `us`, `eu`, `in`, `cn` (conforme seu projeto).
     - **Base URL**: ex.: `https://openapi.tuyaus.com`.
     - **Device IDs**: lista separada por vírgula (`abc123,def456`).
4. **Configurar opções após a instalação**
   - Na tela da integração recém-criada, clique em **Configure**.
   - Defina o **intervalo de polling** (segundos) e desabilite datapoints que não queira expor.
5. **Validar entidades criadas**
   - Abra **Settings > Devices & Services > Prudentes Tuya All > Entities**.
   - Confirme a criação de sensores (um por DP), switches/binary_sensors para booleans, numbers para valores e selects para enums/strings, além do sensor de diagnóstico.

## Plataformas suportadas
- `sensor`: um sensor por datapoint + sensor diagnóstico com atributos completos.
- `switch` e `binary_sensor`: mapeamento de datapoints booleanos conforme suporte de escrita/leitura.
- `number`: valores numéricos com escrita direta.
- `select`: strings/enums com escrita direta.

## Pontos de extensão
- Ler o schema do endpoint `/specification` para decidir writability com maior precisão.
- Persistir cache de tokens/assinaturas Tuya.
- Acrescentar testes e validação de tipos por DP.
