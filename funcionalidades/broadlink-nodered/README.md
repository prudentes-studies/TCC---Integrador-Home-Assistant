# Integração Broadlink + Node-RED no Home Assistant

Guia em português para aprender e enviar comandos IR/RF de dispositivos Broadlink (RM Mini, RM4, etc.) usando o Node-RED integrado ao Home Assistant.

## Pré-requisitos
- Home Assistant operacional com acesso à rede local do Broadlink.
- Add-on **Node-RED** instalado (via Add-on Store) e acessível por ingress ou porta externa.
- Dispositivo Broadlink pareado no Home Assistant (`remote.*`).
- Palette `node-red-contrib-home-assistant-websocket` instalada; palette `node-red-contrib-broadlink-control` ou equivalente para IR/RF.

## Passo a passo
1. **Instalar e iniciar o Node-RED**
   - Em **Settings > Add-ons > Add-on Store**, instale o **Node-RED** e configure usuário/senha.
   - Inicie o add-on e abra a interface (Ingress ou URL externa configurada).

2. **Adicionar o dispositivo Broadlink ao Home Assistant**
   - Em **Settings > Devices & Services > Add Integration**, escolha **Broadlink** e siga o wizard de pareamento (mantenha o botão pressionado até piscar).
   - Verifique se a entidade `remote.*` foi criada e está online.

3. **Instalar palettes necessárias no Node-RED**
   - No menu do Node-RED, acesse **Manage palette > Install** e pesquise `node-red-contrib-broadlink-control`.
   - Confirme que o palette do Home Assistant (`node-red-contrib-home-assistant-websocket`) está presente para chamar serviços.

4. **Criar fluxo de aprendizado de comandos**
   - Adicione um nó **`broadlink-config`** e informe o IP do Broadlink.
   - Insira um nó **`broadlink-learn`** ligado a um nó **`inject`** para disparar o modo de aprendizado.
   - Conecte a saída a um nó **`debug`** para capturar o payload em `msg.payload`. Pressione o botão do controle IR/RF enquanto o nó está aprendendo.
   - Copie o payload capturado e armazene-o em um nó **`function`** ou em `flow/global context` para reuso.

5. **Criar fluxo de transmissão**
   - Adicione um nó **`broadlink-send`** apontando para o mesmo `broadlink-config`.
   - Conecte um nó **`inject`** ou **`function`** que envie o payload salvo (código IR/RF) para o `broadlink-send`.
   - Opcional: exponha o envio via serviço do HA usando um nó **`call-service`** (`remote.send_command`) com `entity_id` do Broadlink e `command` igual ao payload.

6. **Automatizar com entidades do Home Assistant**
   - Use um nó **`events: state`** para reagir a mudanças de entidades (botões virtuais, cenas ou switches) e disparar o fluxo de envio.
   - Combine com nós **`delay`** ou **`rbe`** para evitar repetições e controlar janelas de envio.

7. **Salvar e versionar o fluxo**
   - Clique em **Deploy** para aplicar o fluxo.
   - Exporte o fluxo (Menu > Export) e salve o JSON em `funcionalidades/broadlink-nodered/flow.json` ou em outro local versionado.

## Troubleshooting rápido
- **Não aprende comando**: confirme que o Broadlink e o Node-RED estão na mesma rede/VLAN e que a porta de descoberta não está bloqueada pelo roteador/firewall.
- **RF incompatível**: verifique se o modelo Broadlink suporta a frequência do controle (433/315 MHz).
- **Erro de autenticação**: se os nós retornarem erro de login, reconfigure a integração Broadlink no HA e atualize o IP/credenciais no `broadlink-config` do Node-RED.
- **Fluxo não dispara**: valide se o nó `events: state` está escutando a entidade correta e se o estado realmente muda conforme esperado.

## Próximos passos
- Registrar capturas de tela dos fluxos e dos nós para ilustrar o guia.
- Criar templates de fluxo pré-configurados (JSON) para controle de TV, ar-condicionado e cenas IR frequentes.
- Automatizar backup dos fluxos exportados para o repositório.
