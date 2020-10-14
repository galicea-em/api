# -*- coding: utf-8 -*-
# authors: Jerzy Wawro, Maciej Wawro
# (C) Galicea 2020


import uuid
from datetime import datetime
from flask import ( session, url_for )
from .oid import datetime_to_timestamp

def ses_login(user_id, client_id=0):
    sid=str(uuid.uuid4().hex)
    session['sid'] = sid
    session['uid'] = user_id
    session['cid'] = client_id
    session['auth_time'] = datetime_to_timestamp(datetime.now())
    return sid

def ses_logout():
    session.pop('uid', None)
    session.pop('sid', None)
    session.pop('cid', None)

def get_session_sid():
  return session.get('sid')

def get_session_uid():
  return session.get('uid')

def get_session_cid():
  return session.get('uid')

def get_session_auth_time():
  t=session.get('auth_time')
  if t:
    return int(t)
  else:
    return 0

def get_host_url():
  return url_for('login')

