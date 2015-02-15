Authentication/Authorization API
================================


Granting Access
---------------

API Consumed by the OAuth2 Server


POST /authentication

[source] + [method] + username + password => authentication_token

authentication[authentication_token] = { user_id }


GET /authentication/authentication_token

{ user_id, ... }



POST /authcodes

authentication_id + client_id + authorization_scope => authcode_id

authcodes[code_id] = { authentication_id, client_id, scope  }


authorization_scope = [
  {'http_verb': [],
   'route_url': '/foo/{foo_id}',
   }, ...
]


POST /tokens

type='auth_code' + client_id + client_secret + code => {refresh_token, access_token, expires_in}

type='refresh_token' + client_id + client_secret + refresh_token  => {refresh_token, access_token, expires_in}


access_tokens[access_token] = { client_id, user_id, authorization_scope }
refresh_tokens[refresh_token] = { access_token, client_id, user_id, authorization_scope }


Checking Access
---------------

API Consumed by the Resource Server


GET /authorization/{access_token}/{http_verb}/{route_url}

200 OK | 403 Forbidden

