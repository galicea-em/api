#!/bin/bash
# coding: utf-8
# authors: Jerzy Wawro, Maciej Wawro
# (C) Galicea 2020

from flask_bootstrap import Bootstrap
from flask_cors import CORS
from flask import jsonify

from . import app
from rest import RESPONSE_TYPES_SUPPORTED
from rest import api
from login import init_login

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


from rest import  api_openid
from rest import  api_oauth

def define():
  init_login('flask')
#  init_login('simple')
  api.add_namespace(api_oauth)
  api.add_namespace(api_openid)
