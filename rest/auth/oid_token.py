# -*- coding: utf-8 -*-
# authors: Jerzy Wawro, Maciej Wawro
# (C) Galicea 2020


import json
import time
from .random_tokens import alpha_numeric_string

from jwcrypto import jwk, jwt
from .oid_base import get_access_token, put_access_token


def jwk_from_json(json_key):
  key = jwk.JWK()
  key.import_key(**json.loads(json_key))
  return key


def generate_authorization_code_jwk():
  return jwk.JWK.generate(kty='oct', size=256, kid=alpha_numeric_string(16), use='sig', alg='HS256').export()

def generate_id_token_jwk():
  return jwk.JWK.generate(kty='RSA', size=2054, kid=alpha_numeric_string(16), use='sig', alg='RS256').export()

################################################################
# must be stored (configuration):

# Key used for encrypting authorization codes, exchangeable for access tokens
conf_authorization_code_jwk = generate_authorization_code_jwk()
# RSA key used for ID Token signature
conf_id_token_jwk = generate_id_token_jwk()


def get_authorization_code_jwk():
  return jwk_from_json(conf_authorization_code_jwk)

def get_id_token_jwk():
  return jwk_from_json(conf_id_token_jwk)
##################################################################


def jwt_encode(claims, key):
  token = jwt.JWT(
    header={'alg': key._params['alg'], 'kid': key._params['kid']},
    claims=claims
  )
  token.make_signed_token(key)
  return token.serialize()

def jwt_decode(serialized, key):
    token = jwt.JWT(jwt=serialized, key=key)
    return json.loads(token.claims)

def create_id_token(host_url, user_id, client_id, extra_claims):
    claims = {
        'iss': host_url,
        'sub': str(user_id),
        'aud': str(client_id),
        'iat': int(time.time()),
        'exp': int(time.time()) + 15 * 60
    }
    if 'auth_time' in extra_claims:
        claims['auth_time'] = extra_claims['auth_time']
    if 'nonce' in extra_claims:
        claims['nonce'] = extra_claims['nonce']
    if 'at_hash' in extra_claims:
        claims['at_hash'] = extra_claims['at_hash']

    key = get_id_token_jwk()
    return jwt_encode(claims, key)

def access_token_retrieve_or_create(app_id,user_id=0):
  tk=get_access_token(app_id, user_id)
  if tk:
    return tk.token
  else:
    token=alpha_numeric_string(64)
    put_access_token(token, app_id, user_id)
    return token