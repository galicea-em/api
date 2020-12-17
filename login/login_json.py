#!/bin/bash
# coding: utf-8
# authors: Jerzy Wawro, Maciej Wawro
# (C) Galicea 2020

from flask import jsonify, request
from conf import app
from rest import ses_login, get_user_id, put_session

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
