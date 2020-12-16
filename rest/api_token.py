# coding: utf-8
# authors: Jerzy Wawro, Maciej Wawro
#
# token + decorator 

import functools
import json
import werkzeug
from flask import jsonify, request
from .auth.oid import OAuthException
from .auth.oid_token import access_token_retrieve_or_create, get_id_token_jwk, jwt_decode
from .auth.oid_base import int_client_id

def api_token_create(client_id,user_id,scope):
  app_id=int_client_id(client_id)
  return access_token_retrieve_or_create(app_id,user_id,scope)

def api_token_decode(access_token):
  key = get_id_token_jwk()
  payload=jwt_decode(access_token, key)
  if not payload:
    raise OAuthException(
      'access_token owner',
      'invalid_request',
    )
  scope_list=payload['scope'].split() if 'scope' in payload else []
  user_id=int(payload['sub'])
  client_id=int(payload['aud']) 
  return (scope_list,user_id, client_id)

def with_api_token(scope=''):

  def endpoint_decorator(endpoint):
    @functools.wraps(endpoint)
    def wrapper(*args, **kwargs):

      try:
        access_token = None
        authorization_header = request.headers.get("Authorization")
        # check token is present
        if authorization_header:
          token_type, access_token = authorization_header.split(" ")
          if token_type:
            if token_type.lower() != "bearer":
              return jsonify({"error": "Wrong token type"}), 401
        if not access_token:
          access_token = kwargs.get('access_token')
        if not access_token:
          raise OAuthException(
            'access_token is invalid',
            'invalid_request',
          )
        (token_scope, token_user_id, token_client_id)=api_token_decode(access_token)
        scope_list=scope.split()
        for sc in scope_list:
          if not sc in token_scope:
            raise OAuthException(
            'access_token scope',
            'invalid_request',
            )
        response = endpoint(*args, **kwargs)
        return response
      except OAuthException as e:
        error_message = "error: {0}".format(e)
        return werkzeug.Response(
          response=json.dumps({'error': 'access error', 'error_message': error_message}),
          status=400,
          headers={} #cors_headers
        )
      except:
        return werkzeug.Response(
          response=json.dumps({
            'error': 'server_error',
            'error_message': 'Unexpected server error',
          }),
          headers={}, # cors_headers,
          status=500
        )

    return wrapper

  return endpoint_decorator

