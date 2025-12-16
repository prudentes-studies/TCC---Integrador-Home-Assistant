Melhore o c[odigo para que os seguintes fatores sejam atendidos:
- Matenham os tutoriais com passo a passo clique por clique o mais ultra detalhados possíveis
- Corrigir o código para não instalar na pasta config/custom_... isso não funcionou. Habilite o código para poder ser instalado como um addon externo direto via repositório git então prepare este repositório para agir assim
- modifique o código para não pré setar os tipos de dispositivos mas sim pegar as configurações via api no portal tuya developer e pegar os tipos de lá também segue exemplo de api e retorno:

lembrando que Access ID, Access Secret, Base URL e Região vão ser colocados por mim na ferramenta o device id eb1ecf94531337e404omjr vai ser pego da lista de devices que pode ser obtida também via api do developer tuya

- curl  --request GET "https://openapi.tuyaus.com/v2.0/cloud/thing/eb1ecf94531337e404omjr/shadow/properties" --header "sign_method: HMAC-SHA256" --header "client_id: kcaavw5vxxrwknr9xh3s" --header "t: 1765857185211" --header "mode: cors" --header "Content-Type: application/json" --header "sign: 2CDC4826C0556A4F605FFEE135CB19FDB19CD3695C594B6C9CB7D01374842583" --header "access_token: 624cf393561b70b8d7a46cf00785b039"

- 
{
  "result": {
    "properties": [
      {
        "code": "switch_1",
        "custom_name": "Luz da Escada",
        "dp_id": 1,
        "name": "Switch 1",
        "time": 1765297609040,
        "type": "bool",
        "value": true
      },
      {
        "code": "switch_2",
        "custom_name": "Luz do Corredor",
        "dp_id": 2,
        "name": "Switch 2",
        "time": 1765297609078,
        "type": "bool",
        "value": true
      },
      {
        "code": "switch_3",
        "custom_name": "Ar Condicionado",
        "dp_id": 3,
        "name": "Switch 3",
        "time": 1765848248476,
        "type": "bool",
        "value": true
      },
      {
        "code": "countdown_1",
        "custom_name": "",
        "dp_id": 7,
        "time": 1765204494488,
        "type": "value",
        "value": 0
      },
      {
        "code": "countdown_2",
        "custom_name": "",
        "dp_id": 8,
        "time": 1765204494488,
        "type": "value",
        "value": 0
      },
      {
        "code": "countdown_3",
        "custom_name": "",
        "dp_id": 9,
        "time": 1765204494488,
        "type": "value",
        "value": 0
      },
      {
        "code": "relay_status",
        "custom_name": "",
        "dp_id": 14,
        "time": 1765204494488,
        "type": "enum",
        "value": "off"
      },
      {
        "code": "light_mode",
        "custom_name": "",
        "dp_id": 15,
        "time": 1765204494488,
        "type": "enum",
        "value": "relay"
      },
      {
        "code": "cycle_time",
        "custom_name": "",
        "dp_id": 17,
        "time": 1765204494488,
        "type": "string",
        "value": ""
      },
      {
        "code": "random_time",
        "custom_name": "",
        "dp_id": 18,
        "time": 1765204494488,
        "type": "string",
        "value": ""
      },
      {
        "code": "switch_inching",
        "custom_name": "",
        "dp_id": 19,
        "name": "Switch inching",
        "time": 1765204494488,
        "type": "string",
        "value": ""
      }
    ]
  },
  "success": true,
  "t": 1765857186260,
  "tid": "ba940af8da3211f0b28b76913dfee52c"

}

temos também essa outra api que traz mais informações gerais uteis

curl --request GET "https://openapi.tuyaus.com/v2.0/cloud/thing/eb1ecf94531337e404omjr" --header "sign_method: HMAC-SHA256" --header "client_id: kcaavw5vxxrwknr9xh3s" --header "t: 1765857401677" --header "mode: cors" --header "Content-Type: application/json" --header "sign: 7D9E712CAE9C4610CD9563B256C07320F5AD5F5994E37BC8A53B546C9C9858B6" --header "access_token: 624cf393561b70b8d7a46cf00785b039"

{
  "result": {
    "active_time": 1744047211,
    "bind_space_id": "243186840",
    "category": "kg",
    "create_time": 1664372476,
    "custom_name": "Espelho do Corredor",
    "icon": "smart/icon/ay1553088530507BVYGE/82a1a9f919c29f4bd6bcd48bade4b866.png",
    "id": "eb1ecf94531337e404omjr",
    "ip": "191.25.226.14",
    "is_online": true,
    "lat": "-15.72",
    "local_key": "Y!aTad#vB-N$o&>9",
    "lon": "-47.89",
    "model": "EWS 1003",
    "name": "EWS 1003",
    "product_id": "4zrkiapoidml8xy7",
    "product_name": "EWS 1003",
    "sub": false,
    "time_zone": "-03:00",
    "update_time": 1744047216,
    "uuid": "e83fba96c2249126"
  },
  "success": true,
  "t": 1765857402786,
  "tid": "3ba43f95da3311f081318eca4ab25c9b"
}

pega lista devices do site mas tras no maximo 20 é preciso do last_id para pegar o restante e assim até o final

curl --request GET "https://openapi.tuyaus.com/v2.0/cloud/thing/device?page_size=20" --header "sign_method: HMAC-SHA256" --header "client_id: kcaavw5vxxrwknr9xh3s" --header "t: 1765857483239" --header "mode: cors" --header "Content-Type: application/json" --header "sign: 05419A9CCAA47D08BDA724F50CB498DBA55C09E3B3E7D4001B73ACA9C035C133" --header "access_token: 624cf393561b70b8d7a46cf00785b039"

Leia atentamenta as documentação da tuya para criar um software mais flexível que pegue a estrutura do device direto do portal developer de forma dinÂmica.
