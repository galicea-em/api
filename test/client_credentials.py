#!/usr/bin/python3
# coding: utf-8

import requests
import json
from pprint import pprint

token_url = 'http://127.0.0.1:5000/oauth/token'

class TestApp:
  def __init__(self):
    self.config={}
    self.config["client_id"]='9a195ac5-1a34-4bdd-837e-13f80bc5364d' #uuid(1)
    self.config["client_secret"]='secret'
    self.config["scopes"]='test'
    self.config["redirect_uri"]='http://127.0.0.1:8080'

  def get_token(self):
    """
    authorization = base64.standard_b64encode((self.config["client_id"] +
                                 ':' + self.config["client_secret"]).encode())
    headers = {
      "Authorization": "Basic " + authorization.decode()
    }
    # alternatively - in JSON (in this implementation)
    """
    params = {
          'client_id': self.config["client_id"],
          'client_secret': self.config["client_secret"],
          'scopes': self.config["scopes"],
          'response_type': 'token',
          'grant_type': 'client_credentials',
          'redirect_uri': self.config["redirect_uri"]
      }
    try:
      resp = requests.post(token_url, params)
      #, headers=headers)
      respdata = json.loads(resp.text)
      if 'access_token' in respdata:
        return respdata['access_token']
      else:
        pprint(respdata)
        return None

    except Exception as e:
      print(e)
      return None

  def run(self):
    print(self.get_token())

if __name__ == "__main__":
    ms_app = TestApp()
    ms_app.run()

