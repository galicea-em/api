# coding: utf-8
# Sketch Database Models
# authors: Jerzy Wawro
# (C) Galicea 2020

class Address():
  def __init__(self, id, login, country=None, locality=None,
               postal_code=None, region=None,
               street_address=None):
    self.country = country
    self.locality = locality
    self.postal_code = postal_code
    self.region = region
    self.street_address = street_address

class User():
  def __init__(self, id, login, password=None,
              email=None, phone_number=None,
              name=None, family_name=None, given_name=None,
              address=None):
    self.id = id
    self.login = login
    self.password = password
    self.email = email
    self.phone_number = phone_number
    self.name = name
    self.family_name = family_name
    self.given_name = given_name
    self.address = address

class ClientApplication():
  def __init__(self, id, ident, secret, system_user_id, auth_redirect_uri):
    self.id = id
    self.ident = ident
    self.secret = secret
    self.system_user_id = system_user_id
    self.auth_redirect_uri = auth_redirect_uri

class Token():
  def __init__(self,
               token_type, # access_token
               token,
               client_id, user_id,
               expires_at=None, expires_in=None,
               refresh_token=None, scope=None):
    self.token_type = token_type
    self.token = token
    self.client_id = client_id
    self.user_id = user_id
    self.expires_at = expires_at
    self.expires_in = expires_in
    self.refresh_token = refresh_token
    self.scope = scope

class Session():
  def __init__(self,
               sid, # session ID
               client_id=None,
               user_id = None):
    self.sid = sid
    self.client_id = client_id
    self.user_id = user_id

users=[
  User(1,'demo',password='demo', name='Jan Kowalski', email='jank@example.com', address=Address(1,'demo',country='Poland')),
]

applications = [
  ClientApplication(1,'demoapp', 'secret', 1, 'http://127.0.0.1:3000'),
  ClientApplication(2,'demoimp', 'secret', 1, 'http://localhost:3000/callback')
]

tokens = []

sessions = []

def get_app(client_id):
  for app in applications:
    if app.id == client_id:
      return app
  return None

def get_user(user_id):
  for u in users:
    if u.id == user_id:
      return u
  return None

def get_user_id(login,password):
  for u in users:
    if u.login==login and u.password==password:
      return u.id
  return 0

def put_access_token(token, client_id, user_id=0):
  tokens.append(Token( 'access_token', token, client_id, user_id))

def get_access_token(client_id=0, user_id=0):
  for tk in tokens:
    if tk.user_id==user_id and tk.client_id==client_id and tk.token_type=='access_token':
      return tk
  return None

def token_owner(token):
  for tk in tokens:
    if tk.token==token:
      return (tk.user_id, tk.client_id)
  return (0,0)


def put_session(sid, uid):
  sessions.append(Session(sid,user_id=uid))

def pop_session(sid, uid):
  for s in sessions:
    if s.sid==sid and s.user_id==uid:
      sessions.remove(s)

def get_session_uid(sid):
  for s in sessions:
    if s.sid==sid:
      return s.uid
  return None

def check_session(sid, uid):
  for s in sessions:
    if s.sid==sid and s.user_id==uid:
      return True
  return False

def token_for_session(sid,uid):
  if check_session(sid, uid):
    return get_access_token(user_id=uid)
  else:
    return None

