#!/usr/bin/python3
# coding: utf-8

from local_server import runHTTPServer, a_code
import webbrowser
import requests
from urllib.parse import urlencode, quote, unquote
from pprint import pprint

authority_url = 'http://127.0.0.1:5000/auth/authorisation/'

class TestApp:
  def __init__(self):
    self.config={}
    self.config["client_id"]='9a195ac5-1a34-4bdd-837e-13f80bc5364d'
    self.config["scopes"]='test'
    self.config["redirect_uri"]='http://127.0.0.1:8080'

  def get_authorization_code(self):
      params = {
          'client_id': self.config["client_id"],
          'scopes': self.config["scopes"],
          'response_type': 'code',
          'redirect_uri': self.config["redirect_uri"]
      }
      webbrowser.open(authority_url, 2)
      runHTTPServer()
      return a_code

  def token(self):
      result = self.app.acquire_token_silent(
          self.config["scopes"], account=None)
      if not result:
          print("No suitable token exists in cache. Let's get a new one from AAD.")
          result = self.app.acquire_token_for_client(
              scopes=self.config["scopes"])
      return result

  def run_query(self, query, req_method, headers=None, req_body=None):
      if not self._access_token:
          self.authorize()

      req_headers = {
          'Authorization': 'Bearer ' + self._access_token,
          'Accept': '*/*',
          'Content-Type': 'application/json'
      }
      if headers:
          for key in headers:
              req_headers[key] = headers[key]
      data = None
      if req_method == "POST":
          data = requests.post(query, headers=req_headers,
                               json=req_body).json()
      if req_method == "GET":
          data = requests.get(query, headers=req_headers)
      if req_method == "PUT":
          data = requests.put(query, data=req_body, headers=req_headers).json()
      return data

  def get_test(self):
    test_endpoint=''
    body = {
      }
    self.run_query(test_endpoint, "POST", None, body)

  def run(self):
    code=self.get_authorization_code()
    print(code)

if __name__ == "__main__":
    ms_app = TestApp()
    ms_app.run()

