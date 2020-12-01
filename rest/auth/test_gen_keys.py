# -*- coding: utf-8 -*-

import json
from .random_tokens import alpha_numeric_string
from jwcrypto import jwk
from pprint import pprint
from conf import config

def generate_authorization_code_jwk():
  code=jwk.JWK.generate(kty='oct', size=256, kid=alpha_numeric_string(16), use='sig', alg='HS256').export()
  with open('authorization_code.jwk','w+') as f:
    f.write(code)
  return code

def generate_id_token_jwk():
  id_token_jwk=jwk.JWK.generate(kty='RSA', size=2054, kid=alpha_numeric_string(16), use='sig', alg='RS256')
  with open('id_token_jwk.key','bw+') as pem:
    pem.write(id_token_jwk.export_to_pem(private_key=True, password=None))
  with open('id_token_jwk.pem','bw+') as pem:
    pem.write(id_token_jwk.export_to_pem(private_key=False, password=None))
  return id_token_jwk.export()

conf_authorization_code_jwk = generate_authorization_code_jwk()
conf_id_token_jwk = generate_id_token_jwk()

print('authorization_code_jwk:')
pprint(json.loads(conf_authorization_code_jwk))
print('id_token_jwk:')
pprint(json.loads(conf_id_token_jwk))

print('=======================================================')

# from file
with open('authorization_code.jwk', 'r') as f:
  data = f.read()
print(json.loads(data))

print('=======================================================')

with open('id_token_jwk.key', 'rb') as f:
  data = f.read()
conf_id_token_jwk2=jwk.JWK.from_pem(data).export()
pprint(json.loads(conf_id_token_jwk2))

