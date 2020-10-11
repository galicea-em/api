# coding: utf-8
# authors: Jerzy Wawro
# (C) Galicea 2020


from flask_restx import Api, fields
from conf import app


api = Api(app,
    endpoint="/",
    version='1.0',
    title='API Server',
    description='OAuth / OpenId Connect',
    doc='/help/'
)

OAuth2Error = api.model('OAuth2Error', {
  'error' : fields.String,
  'error_description' : fields.String,
})

Token = api.model('Token', {
  'access_token' : fields.String, # Token dostępu wydany przez serwer autoryzacji.
  'token_type' : fields.String,
  'expires_in' : fields.Integer, #	integer($int32) Czas życia w sekundach token dostępu.
  'refresh_token' : fields.String, # Token odświeżania wystawiony klientowi
  'scope': fields.String,  # Zakres przyznanych tokenów.
  # poniższych nie ma w standardzie rfc6749 - ale dopuszcza on rozszerzenia - zob openidconnect
  'expires_at' : fields.Integer, # Czas (RFC3339) w którym ważność tokenu wygasa
                                 # expires_in = expires_at - time.time()
                                 # https://openid.net/specs/openid-connect-registration-1_0-10.html
  # The number of seconds from 1970-01-01T0:0:0Z as measured in UTC that
  # the client_id and client_secret will expire or 0 if they do not expire.
  'id_token' : fields.String,	# Wartość Token ID powiązana z uwierzytelnioną sesją.
# opcje https://tools.ietf.org/html/rfc7636
#  'code_challenge' : fields.String, # 'Kod do weryfikacji - opcjonalny')
#  'code_challenge_method': fields.String # 'Metoda weryfikacji'
 }
)



Address = api.model('Address', {
    # Address structure
    'country' : fields.String,
    'locality' : fields.String,
    'postal_code' : fields.String,
    'region' : fields.String,
    'street_address' : fields.String,
    }
)


UserInfo = api.model('UserInfo', {
'description' : fields.String,
'OIDC UserInfo' : fields.String,
#'address	Address{...}
#'aq:location	{...}
'email' : fields.String,
'email_verified' : fields.Boolean,
'family_name' : fields.String,
'given_name' : fields.String,
'name' : fields.String,
'phone_number' : fields.String,
'phone_number_verified' : fields.Boolean,
'sub' : fields.String,
}
)

TokenIntrospection = api.model('Introspection', {
  "active": fields.Boolean,
  "client_id": fields.String,
  "username": fields.String,
  "scope": fields.String,
  "sub": fields.String,
  "aud": fields.String, # "https://protected.example.net/resource"
  "iss": fields.String, # "https://server.example.com/",
  "exp": fields.Integer,
  "iat": fields.Integer
  #"extension_field": "twenty-seven"
})