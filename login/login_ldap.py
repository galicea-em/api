# coding: utf-8

from flask import  redirect, request, jsonify,  flash, url_for
from rest import ses_login, put_session
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
    if not (r and "user" in r):
      return jsonify({"result": "To login POST Json({username: ..., password: ..., ...}"}), 401
    else:
      res=login_ldap(r["user"],r["password"])
      if not res:
          return jsonify({"result": "Incorrect username/password"}), 401
      sid=ses_login(r["user"])
      put_session(sid, r["user"])
      flash("Logged in successfully.", "success")
#      return jsonify({"result": "success"}), 200
      scope = r["scope"] if "scope" in r else ""
      state = r["state"] if "state" in r else ""
      clientID = r["clientID"] if "clientID" in r else ""
      redirectUri = r["redirectUri"] if "redirectUri" in r else ""
      response_mode = r["response_mode"] if "response_mode" in r else ""
      if not response_mode: response_mode = 'query'
      return redirect(url_for("oauth_authorize_class",
                        response_type='token',
                        response_mode=response_mode,
                        redirect_uri=redirectUri,
                        scope=scope,
                        state=state,
                        client_id=clientID
                        ))
