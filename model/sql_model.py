#!/usr/bin/python3
from sqlalchemy import create_engine, Column, Integer, Sequence, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from . import CREATING, COMMANDLINE, DB_PATH
from uuid import uuid4

if CREATING:
  Base = declarative_base()
else:
  if COMMANDLINE:
    from flask import Flask
    app=Flask('api')
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_PATH
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
  else:
    from conf import app
  from flask_sqlalchemy import SQLAlchemy
  db=SQLAlchemy(app)
  Base=db.Model

class Address(Base):
  __tablename__ = 'address'
  id = Column(Integer, Sequence('adr_id_seq'), primary_key=True)
  country = Column(String(20))
  locality = Column(String(50))
  postal_code = Column(String(6))
  region = Column(String(20))
  street_address = Column(String(40))


  def __repr__(self):
    return "<Address('%s', '%s', '%s)>" % (self.id, self.locality, self.street_address)

  def __init__(self, country=None, locality=None,
               postal_code=None, region=None,
               street_address=None):
    self.country = country
    self.locality = locality
    self.postal_code = postal_code
    self.region = region
    self.street_address = street_address


class User(Base, UserMixin):
  __tablename__ = 'user'
  __table_args__ = {'extend_existing': True}
  id = Column(Integer, Sequence('usr_id_seq'), primary_key=True)
  login = Column(String(30))
  password = Column(String(200))
  email = Column(String(50))
  phone_number = Column(String(10))
  name = Column(String(30))
  family_name = Column(String(30))
  given_name = Column(String(30))
  address_id = Column(Integer)

  def __init__(self, login, password=None,
              email=None, phone_number=None,
              name=None, family_name=None, given_name=None,
              address_id=None):
    self.login = login
    self.set_password(password)
    self.email = email
    self.phone_number = phone_number
    self.name = name
    self.family_name = family_name
    self.given_name = given_name
    self.address_id = address_id

  def set_password(self, password):
    self.password = generate_password_hash(password)

  def check_password(self, value):
    if (self.password==value):
       return True
    return check_password_hash(self.password, value)

  def is_authenticated(self):
    if isinstance(self, AnonymousUserMixin):
      return False
    else:
      return True

  def is_active(self):
    return True

  def is_anonymous(self):
    if isinstance(self, AnonymousUserMixin):
      return True
    else:
      return False

  def get_id(self):
    return self.id

  def __repr__(self):
    return '<User %r>' % self.login


class ClientApplication(Base):
  __tablename__ = 'client_app'
  id = Column(Integer, Sequence('capp_id_seq'), primary_key=True)
  ident = Column(String(40))
  secret = Column(String(40))
  system_user_id = Column(Integer)
  auth_redirect_uri = Column(String(500))
  uuid = Column(String(40))

  def __repr__(self):
    return "<ClientApplication('%s', '%s')>" % (self.id, self.auth_redirect_uri)

  def __init__(self, ident, secret, system_user_id, auth_redirect_uri):
    self.uuid = str(uuid4())
    self.ident = ident
    self.secret = secret
    self.system_user_id = system_user_id
    self.auth_redirect_uri = auth_redirect_uri

class Token(Base):
  __tablename__ = 'token'
  id = Column(Integer, Sequence('tkn_id_seq'), primary_key=True)
  token = Column(String(200))
  token_type = Column(String(20))
  client_id = Column(Integer)
  user_id = Column(Integer)
  expires_at = Column(Integer)
  expires_in = Column(Integer)
  refresh_token = Column(String(200))
  scope = Column(String(50))

  def __repr__(self):
    return "<Token('%s', '%s', '%s)>" % (self.token, self.client_id, self.user_id)

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

class Session(Base):
  __tablename__ = 'session'
  sid = Column(String(100), primary_key=True)
  client_id = Column(Integer)
  user_id = Column(Integer)

  def __repr__(self):
    return "<Session('%s', '%s', '%s)>" % (self.sid, self.client_id, self.user_id)

  def __init__(self,
               sid, # session ID
               client_id=None,
               user_id = None):
    self.sid = sid
    self.client_id = client_id
    self.user_id = user_id

class ScopeCl(Base):
  __tablename__ = 'scope_cl'
  id = Column(Integer, Sequence('scope_cl_seq'), primary_key=True)
  client_id = Column(Integer)
  scope = Column(String(20))

  def __repr__(self):
    return "<Uuid('%s', '%s)>" % (self.user_id, self.scope)

  def __init__(self, user_id=None, scope=None):
    self.user_id = user_id
    self.scope = scope

class DataManager():

  def __init__(self, db_path):
    self.engine = create_engine(db_path, echo=True)
    Base.metadata.bind = self.engine
    self.DBSession = sessionmaker(bind=self.engine)

  def create_db(self):
    try:
      Base.metadata.create_all(self.engine)
    except Exception as e:
      print('DB already exist ? [%s]' % e)

  def user_by_id(self, userid):
    return User.query.filter_by(id=userid).one()

  def user_by_name(self, name):
    return User.query.filter_by(login=name).first()

  def add_address(self, country=None, locality=None,
               postal_code=None, region=None,
               street_address=None):
    session = self.DBSession()
    address = Address(country, locality,
               postal_code, region,
               street_address)
    try:
      session.add(address)
      session.commit()
    except:
      session.rollback()
    return address.id

  def add_user(self, login, password,
               name='', email='', address_id=0):
    session = self.DBSession()
    user = User(login, password, name=name, email=email, address_id=address_id)
    try:
      session.add(user)
      session.commit()
    except:
      session.rollback()
    return user.id

  def get_client(self,client_id):
    return ClientApplication.query.filter_by(id=client_id).first()

  def get_client_by_uuid(self,uuid):
    return ClientApplication.query.filter_by(uuid=uuid).first()

  def add_client(self, ident, secret, system_user_id, auth_redirect_uri):
    session = self.DBSession()
    app = ClientApplication(ident, secret, system_user_id, auth_redirect_uri)
    try:
      session.add(app)
      session.commit()
    except:
      session.rollback()
    return app.id

  def get_user(self,user_id):
    return User.query.filter_by(id=user_id).first()

  def get_user_by_login(self, login):
    u=User.query.filter_by(login=login).first()
    if u:
      return u.id
    else:
      return 0

  def get_user_id(self, login, password):
    u=User.query.filter_by(login=login).first()
#    (a,salt,p)=u.password.split('$')
    if not u:
      return 0
    if check_password_hash(u.password,password):
      return u.id
    else:
      return 0

  def put_access_token(self, token, client_id, user_id=0):
    session = self.DBSession()
    tk=Token('access_token',token,client_id,user_id)
    try:
      session.add(tk)
      session.commit()
    except:
      session.rollback()
    return tk

  def get_access_token(self, client_id=0, user_id=0):
    return Token.query.filter_by(client_id=client_id, user_id=user_id).first()

  def token_owner(self, token):
    tk=Token.query.filter_by(token=token).first()
    if tk:
        return (tk.user_id, tk.client_id)
    return (0, 0)

  def put_session(self, sid, uid):
    session = self.DBSession()
    s=Session(sid, user_id=uid)
    try:
      session.add(s)
      session.commit()
    except:
      session.rollback()
    return s

  def pop_session(self, sid, uid):
    session = self.DBSession()
    try:
      session.query(Session).filter(Session.sid == sid and Session.uid == uid).delete()
      session.commit()
    except:
      session.rollback()

  def get_session_uid(self, sid):
    return Session.query.filter_by(sid=sid).first()

  def check_session(self, sid, uid):
    s=Session.query.filter_by(sid=sid,uid=uid).first()
    return True if s else False

  def token_for_session(self, sid, uid):
    s=Session.query.filter_by(sid=sid,uid=uid).first()
    if s:
      return self.get_access_token(user_id=uid)
    else:
      return None

def create_dm(DB_PATH):
  return DataManager(DB_PATH)
