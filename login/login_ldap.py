# coding: utf-8

from flask import request, jsonify
from rest import ses_login
from conf import app
import ldap
from conf import config

def init(uri):
  try:
    return ldap.initialize(uri)
  except ldap.LDAPError as e:
    print(e)
    return None


def chk_login(ld, userDN, user_pass):
  bind_dn = userDN
  try:
    result = ld.simple_bind(bind_dn, user_pass)
    res = ld.result(result)  # bez tego trudno ustalic, czy sukces
  except ldap.LDAPError as e:
    return False
  return True

def login_ldap(user_name, user_pass):
  config.read("conf/api.ini")
  ld=init(config['authLDAP']['uri'])
  userDN = config['authLDAP']['userAttr']+"="+user_name+","+config['authLDAP']['userBase']
  result=chk_login(ld, userDN, user_pass)
  ld.unbind()
  return result

@app.route("/login/ldap", methods=["POST"])
def login_ldap_ep():
    r = request.get_json()
    if r and "user" in r:
      res=login_ldap(r["user"],r["password"])
      if not res:
          return jsonify({"result": "Incorrect username/password"}), 401
      sid=ses_login(r["user"])
      return jsonify({"result": "success"}), 200
    return jsonify({"result": "To login PUT Json({username: ..., password: ...}"}), 401

