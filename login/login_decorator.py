# coding: utf-8
# authors: Jerzy Wawro, Maciej Wawro
#
# login decorator 

import functools
import json
import werkzeug
from rest import get_session_sid, get_session_uid
from rest import ext_user_id
from conf import config


def login_required(userclass=''):

  def endpoint_decorator(endpoint):
    @functools.wraps(endpoint)
    def wrapper(*args, **kwargs):
      try:
        # is login?
        uid=get_session_uid()
        username=ext_user_id(uid)
        if not username:
            raise Exception(
              'login expected',
              'invalid_request',
            )
        if userclass=='admin':
          config.read("conf/api.ini")
          ok=config['users']['admin'].find(username)>=0
        if not ok:
            raise Exception(
              'login incorrect',
              'protected zone',
            )
        response = endpoint(*args, **kwargs)
        return response
      except Exception as e:
        error_message = "error: {0}".format(e)
        return werkzeug.Response(
          response=json.dumps({'error': 'access error', 'error_message': error_message}),
          status=400,
          headers={} #cors_headers
        )

    return wrapper

  return endpoint_decorator

