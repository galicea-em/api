# -*- coding: utf-8 -*-
# authors: Jerzy Wawro, Maciej Wawro
# (C) Galicea 2020

import time
import base64

from jwcrypto import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

from .oid import OAuthException
from .oid_flask import get_session_sid, get_host_url
from .oid_token import jwt_encode, jwt_decode
from .oid_token import get_authorization_code_jwk, create_id_token, access_token_retrieve_or_create

from .oid_valid import validator


def handle_oauth_authorize(response_type, user_id, client_id, redirect_uri, scopes, state):
  try:
    app = validator.validate_client(client_id)
    redirect_uri = validator.validate_redirect_uri(app, redirect_uri)
  except OAuthException as e:
    return  {
              'error': e.type,
              'error_description': str(e)
            }
  response_params = {}
  # state, if present, is just mirrored back to the client
  if state:
    response_params['state'] = state
  response_types = response_type.split()
  extra_claims = {
    'sid': get_session_sid(),
  }
  if 'code' in response_types:
    # Generate code that can be used by the client server to retrieve
    # the token. It's set to be valid for 60 seconds only.
    # TODO: The spec says the code should be single-use. We're not enforcing
    # that here.
    payload = {
      'redirect_uri': redirect_uri,
      'client_id': client_id,
      'user_id': user_id,
      'scopes': scopes,
      'exp': int(time.time()) + 60
    }
    payload.update(extra_claims)
    key = get_authorization_code_jwk()
    response_params['code'] = jwt_encode(payload, key)
  if 'token' in response_types:
    access_token = access_token_retrieve_or_create(client_id,user_id,scopes)
    response_params['access_token'] = access_token
    response_params['token_type'] = 'bearer'

    # at_hash - część id_token (OpenID) która  może być użyta do walidacji access_tokena
    # https://openid.net/specs/openid-connect-core-1_0.html#ImplicitTokenValidation
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(access_token.encode('ascii'))
    at_hash = digest.finalize()
    b64=base64.urlsafe_b64encode(at_hash[:16])
    # decode - because python3 error - TypeError: a bytes-like object is required, not 'str'
    b64=b64.decode()
    extra_claims['at_hash'] = b64.strip('=')
  if 'id_token' in response_types:
    response_params['id_token'] = create_id_token(get_host_url(), user_id, client_id, extra_claims)
  return response_params


def handle_grant_type_authorization_code(client_id, redirect_uri, code, scope):
  app = validator.validate_client(client_id)
  redirect_uri = validator.validate_redirect_uri(app, redirect_uri)
  if not code:
    raise OAuthException(
      'code param is missing',
      OAuthException.INVALID_GRANT,
    )
  key = get_authorization_code_jwk()
  try:
    payload = jwt_decode(code, key)
  except jwt.JWTExpired:
    raise OAuthException(
      'Code expired',
      OAuthException.INVALID_GRANT,
    )
  except ValueError:
    raise OAuthException(
      'code malformed',
      OAuthException.INVALID_GRANT,
    )
  if payload['client_id'] != app.id:
    raise OAuthException(
      'client_id doesn\'t match the authorization request',
      OAuthException.INVALID_GRANT,
    )
  if payload['redirect_uri'] != redirect_uri:
    raise OAuthException(
      'redirect_uri doesn\'t match the authorization request',
      OAuthException.INVALID_GRANT,
    )

  # Retrieve/generate access token. We currently only store one per user/app
  token = access_token_retrieve_or_create(
    app.id,
    payload['user_id']
  )
  response = {
    'access_token': token,
    'token_type': 'bearer'
  }
  if 'openid' in payload['scopes']:
    extra_claims = {name: payload[name] for name in payload if name in ['sid', 'nonce']}
  if scope:
    extra_claims['scope']=scope
    #? response['id_token'] = create_id_token(req, payload['user_id'], app, extra_claims)
    response['id_token'] = create_id_token(get_host_url(),  payload['user_id'], app.id, extra_claims)
  return response


def handle_grant_type_client_credentials(client_id, client_secret, scope):
  app = validator.validate_client(client_id)
  validator.validate_client_secret(app, client_secret)
  # Could be replaced with data migration
  if not app.system_user_id:
    raise OAuthException(
      'not implemented yet',
      OAuthException.INVALID_REQUEST
    )
  token = access_token_retrieve_or_create(app.id,scope=scope)
  return {
    'access_token': token,
    'token_type': 'bearer'
  }

