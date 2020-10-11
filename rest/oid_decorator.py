# coding: utf-8
# authors: Jerzy Wawro, Maciej Wawro
# (C) Galicea 2020

import functools
import json
import werkzeug
from flask import jsonify, request
from .oid import OAuthException
from .oid_flask import get_session_uid,ses_login,get_session_cid
from .oid_base import token_owner


def resource(auth='user'):
  assert auth in ['user', 'client']

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
        (user_id,client_id)=token_owner(access_token)
        if auth == 'user':
          uid=get_session_uid()
          if not uid:
            ses_login(user_id, client_id)
          elif uid != user_id:
            raise OAuthException(
              'access_token owner',
              'invalid_request',
            )
        elif auth == 'client':
          cid=get_session_cid()
          if not cid:
            ses_login(user_id, client_id)
          elif cid != client_id:
            raise OAuthException(
              'access_token owner',
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

