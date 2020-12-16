#!/bin/bash
# coding: utf-8
# authors: Jerzy Wawro, Maciej Wawro
# (C) Galicea 2020

from flask import jsonify, request

from conf import app
from rest import ses_login, get_session_auth_time, get_session_uid, get_user_id, put_session
from rest import time_to_now, LOGIN_TIMEOUT

@app.route("/login", methods=["POST","GET"])
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
  clientID=request.args.get('client_id')
  redirectUri = request.args.get('redirect_uri')
  if not state: state=''
  if not scope: scope=''
  if not clientID: clientID=''
  if not redirectUri: redirectUri=''
  if user_id>0: # consent screen
    action = "/oauth/authorize"
    form_login=''
    form_scope='''Zezwalasz na ''' + scope + '''<br />
         <button type="submit">Akceptujesz?</button>
    '''
  else:
    action='/login' 
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



@app.route("/json_login", methods=["POST"])
def login_post():
    r = request.get_json()
    if r and "user" in r:
      user_id=get_user_id(r["user"],r["password"])
      if not user_id>0:
          return jsonify({"error": "Incorrect username/password"}), 401
      sid=ses_login(user_id)
      put_session(sid, user_id)
    return jsonify({"error": "To login PUT Json({username: ..., password: ...}"}), 401
