localhost:8080 da internal error

e o pacote na hora de carregar entidades agora alerta erro no log: "Registrador: aiohttp.server
Fonte: /usr/local/lib/python3.13/site-packages/aiohttp/web_protocol.py:481
Ocorreu pela primeira vez: 04:09:15 (1 ocorrência )
Último registro: 04:09:15

Error handling request from 10.0.0.9
Traceback (most recent call last):
  File "/usr/local/lib/python3.13/site-packages/aiohttp/web_protocol.py", line 510, in _handle_request
    resp = await request_handler(request)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.13/site-packages/aiohttp/web_app.py", line 569, in _handle
    return await handler(request)
           ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.13/site-packages/aiohttp/web_middlewares.py", line 117, in impl
    return await handler(request)
           ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/src/homeassistant/homeassistant/components/http/security_filter.py", line 92, in security_filter_middleware
    return await handler(request)
           ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/src/homeassistant/homeassistant/components/http/forwarded.py", line 87, in forwarded_middleware
    return await handler(request)
           ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/src/homeassistant/homeassistant/components/http/request_context.py", line 26, in request_context_middleware
    return await handler(request)
           ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/src/homeassistant/homeassistant/components/http/ban.py", line 86, in ban_middleware
    return await handler(request)
           ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/src/homeassistant/homeassistant/components/http/auth.py", line 242, in auth_middleware
    return await handler(request)
           ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/src/homeassistant/homeassistant/components/http/headers.py", line 41, in headers_middleware
    response = await handler(request)
               ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/src/homeassistant/homeassistant/helpers/http.py", line 73, in handle
    result = await handler(request, **request.match_info)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/src/homeassistant/homeassistant/components/http/decorators.py", line 83, in with_admin
    return await func(self, request, *args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/src/homeassistant/homeassistant/components/config/config_entries.py", line 272, in post
    return await super().post(request)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/src/homeassistant/homeassistant/components/http/data_validator.py", line 74, in wrapper
    return await method(view, request, data, *args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/src/homeassistant/homeassistant/helpers/data_entry_flow.py", line 76, in post
    return await self._post_impl(request, data)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/src/homeassistant/homeassistant/helpers/data_entry_flow.py", line 83, in _post_impl
    result = await self._flow_mgr.async_init(
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<2 lines>...
    )
    ^
  File "/usr/src/homeassistant/homeassistant/data_entry_flow.py", line 316, in async_init
    flow = await self.async_create_flow(handler, context=context, data=data)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/src/homeassistant/homeassistant/config_entries.py", line 3682, in async_create_flow
    return handler.async_get_options_flow(entry)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^
  File "/config/custom_components/prudentes_tuya_all/config_flow.py", line 62, in async_get_options_flow
    return TuyaOptionsFlowHandler(config_entry)
  File "/config/custom_components/prudentes_tuya_all/config_flow.py", line 69, in __init__
    self.config_entry = config_entry
    ^^^^^^^^^^^^^^^^^
AttributeError: property 'config_entry' of 'TuyaOptionsFlowHandler' object has no setter"
