#!/bin/bash
# coding: utf-8
# authors: Jerzy Wawro, Maciej Wawro
# (C) Galicea 2020

from flask_bootstrap import Bootstrap
from flask_cors import CORS
from flask import jsonify, request
from flask_restx import Resource
from flask import request, flash, redirect, render_template, url_for
from flask_login import login_user, logout_user

from . import app
from rest import ses_login, get_host_url, get_session_auth_time, get_session_uid, get_session_sid
from rest import get_user_id, put_access_token, put_session
from rest import time_to_now, LOGIN_TIMEOUT, RESPONSE_TYPES_SUPPORTED
from rest import create_id_token
from rest import api

# CORS
CORS(app)
@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response


Bootstrap(app)

ns = api.namespace('api', description='Operacje API - obsługa serwera')

@app.route("/.well-known/openid-configuration", methods=["GET"])
# Metadata. See https://swagger.io/docs/specification/authentication/openid-connect-discovery/'
def get_well_known():
    base_url = api.base_url
    data = {
        'issuer': base_url,
        'authorization_endpoint': base_url + 'oauth/authorize',
        'token_endpoint': base_url + 'oauth/token',
        'userinfo_endpoint': base_url + 'openid/userinfo',
        'jwks_uri': base_url + 'openid/jwks',
        'scopes_supported': ['openid'],
        'response_types_supported': RESPONSE_TYPES_SUPPORTED,
        'grant_types_supported': ['authorization_code', 'implicit'],
        'subject_types_supported': ['public'],
        'id_token_signing_alg_values_supported': ['RS256'],
        'token_endpoint_auth_methods_supported': ['client_secret_post']
    }
    return jsonify(data)


@app.route("/implicit", methods=["POST","GET"])
def test_implicit():
  password=request.args.get('password')
  if password:
    login = request.args.get('login')
    user_id = get_user_id(login, password)
    if user_id is None:
      user_id=0
    elif user_id > 0:
      sid=ses_login(user_id)
      put_session(sid, user_id)
    else:
      user_id=0
  else:
    user_id = get_session_uid()
    if user_id is None:
      user_id=0
    elif user_id>0:
      auth_time = get_session_auth_time()
      if time_to_now(auth_time) > LOGIN_TIMEOUT:
        user_id=0
  scope=request.args.get('scope')
  state=request.args.get('state')
  if not state: state=''
  clientID=request.args.get('client_id')
  redirectUri = request.args.get('redirect_uri')
  if user_id>0:
    action = "/oauth/authorize"
    form_login=''
    form_scope='''Zezwalasz na ''' + scope + '''<br />
         <button type="submit">Akceptujesz?</button>
    '''
  else:
    action='/implicit'
    form_scope=''
    form_login='''
                <div class="form-group">
                    login=<input name="login"/>
                </div>
                <div class="form-group">
                    password=<input type="password" name="password"/>
                </div>
                <button type="submit">Loguj</button>
    '''
  return '''
<html>
    <head>
        <title>Test - implicit grant</title>
    </head>
<body>
 <form action="'''+action+'''" method="get">
   <input type="hidden" name="response_type" value="token"/>
   <input type="hidden" name="response_mode" value="query"/>
   <input type="hidden" name="client_id" value="''' + clientID + '''"/>
   <input type="hidden" name="redirect_uri" value="''' + redirectUri + '''"/>
   <input type="hidden" name="state" value="''' + state + '''"/>
   <input type="hidden" name="scope" value="''' + scope + '''"/>
   '''+form_scope+'''
   '''+form_login+'''
 </form>
</body>
</html>
  '''



@app.route("/login", methods=["POST"])
def login_post():
    r = request.get_json()
    if r and "user" in r:
      user_id=get_user_id(r["user"],r["password"])
      if not user_id>0:
          return jsonify({"error": "Incorrect username/password"}), 401
      sid=ses_login(user_id)
      put_session(sid, user_id)
    return jsonify({"error": "To login PUT Json({username: ..., password: ...}"}), 401

from rest import  api_openid
from rest import  api_oauth


def define():
  api.add_namespace(api_oauth)
  api.add_namespace(api_openid)
