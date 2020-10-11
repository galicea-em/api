# coding: utf-8
# authors: Jerzy Wawro
# (C) Galicea 2020

from model import selected_dm
if selected_dm()=='sketch':
  from model import sketch as dm
else:
  from model import dm

def get_app(client_id):
  return dm.get_app(client_id)

def get_user(user_id):
  return dm.get_user(user_id)

def get_user_id(login,password):
  return dm.get_user_id(login,password)

def put_access_token(token, client_id, user_id=0):
  dm.put_access_token(token, client_id, user_id)

def get_access_token(client_id=0, user_id=0):
  return dm.get_access_token(client_id, user_id)

def token_owner(token):
  return dm.token_owner(token)

def put_session(sid, uid):
  dm.put_session(sid, uid)

def pop_session(sid, uid):
  return dm.pop_session(sid, uid)

def get_session_uid(sid):
  return dm.get_session_uid(sid)

def check_session(sid, uid):
  return dm.check_session(sid, uid)

def token_for_session(sid,uid):
  return dm.token_for_session(sid,uid)

