# -*- coding: utf-8 -*-
# authors: Jerzy Wawro, Maciej Wawro
# (C) Galicea 2020

import json
import time
from .random_tokens import alpha_numeric_string

from jwcrypto import jwk, jwt
from .oid_base import get_access_token, put_access_token
from .oid_flask import get_host_url

from conf import config
from os import path

#  keys / config
def init_oct_key():
  key_jwk_file='./conf/'+config['jwt']['key']
  if not path.exists(key_jwk_file):
    jwt_key = jwk.JWK.generate(kty='oct', size=256, kid=alpha_numeric_string(16), use='sig', alg='HS256')
    with open(key_jwk_file, 'w+') as f:
      f.write(jwt_key.export())
  else:
    with open(key_jwk_file, 'r') as f:
      data = f.read()
      jwt_key=jwk.JWK.from_json(data)
  return jwt_key

def init_rsa_key():
  rsa_key_file='./conf/'+config['jwt']['rsa']
  if not path.exists(rsa_key_file):
    rsa_key = jwk.JWK.generate(kty='RSA', size=2054, kid=alpha_numeric_string(16), use='sig', alg='RS256')
    with open(rsa_key_file, 'bw+') as pem:
      pem.write(rsa_key.export_to_pem(private_key=True, password=None))
  else:
    with open(rsa_key_file, 'rb') as f:
      data = f.read()
      rsa_key = jwk.JWK.from_pem(data)
  return rsa_key


conf_authorization_code_jwk = init_oct_key()
# RSA key used for ID Token signature
conf_id_token_jwk = init_rsa_key()


def get_authorization_code_jwk():
  return conf_authorization_code_jwk

def get_id_token_jwk():
  return conf_id_token_jwk
##################################################################

def jwt_encode(claims, key):
  if key.key_type=='oct':
      alg='HS256'
  else:
      alg="RS256"
  token = jwt.JWT(
    header={'alg': alg, 'kid': key._params['kid']},
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
    """
    if 'auth_time' in extra_claims:
        claims['auth_time'] = extra_claims['auth_time']
    if 'nonce' in extra_claims:
        claims['nonce'] = extra_claims['nonce']
    if 'at_hash' in extra_claims:
        claims['at_hash'] = extra_claims['at_hash']
    """
    claims.update(extra_claims)
    key = get_id_token_jwk()
    return jwt_encode(claims, key)

def access_token_retrieve_or_create(app_id,user_id=0,scope=''):
  tk=get_access_token(app_id, user_id)
  if tk:
    return tk.token
  else:
    #token=alpha_numeric_string(64)
    token=create_id_token(get_host_url(), user_id, app_id, {'scope':scope})
    put_access_token(token, app_id, user_id)
    return token