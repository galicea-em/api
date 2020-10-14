# coding: utf-8
# authors: Jerzy Wawro, Maciej Wawro
# (C) Galicea 2020


from flask_restx import reqparse
from flask_restx import Namespace, Resource
import json

from werkzeug.urls import url_encode
from flask import redirect, abort

from .oid_handle import handle_oauth_authorize, handle_grant_type_authorization_code, \
                        handle_grant_type_client_credentials
from .oid import OAuthException, time_to_now, LOGIN_TIMEOUT
from .oid_valid import validator
from .api_models import OAuth2Error, Token, TokenIntrospection
from .oid_flask import get_session_uid, get_session_auth_time
from .oid_token import get_id_token_jwk
from jwcrypto import jwk

ns = Namespace('oauth', description='OAuth API')
parser = reqparse.RequestParser()

@ns.errorhandler(OAuthException)
@ns.marshal_with(OAuth2Error)
@ns.header('OAuth Error', 'Odpowiedź z błędem defined as in Section 5.2 of OAuth 2.0 [RFC6749].')
def handle_oauth_exception(error,code=400):
    '''OAuth exceptions'''
    return {
               'error' : error.type,
               'error_description': error.message
           }

@ns.errorhandler(Exception)
@ns.marshal_with(OAuth2Error)
def handle_system_exception(error, code=400):
  '''OAuth exceptions'''
  return {
    'error': 'System error',
    'error_description': str(error)
  }



@ns.route('/authorize', #?response_type=<string:response_type>&<string:client_id>/<string:redirect_uri>/<string:scope>/<string:state>/<string:code_challenge>/<string:code_challenge_method>',
           methods=['GET',])
@ns.param('response_type', 'Typ odpowiedzi. W Authorization Code Grant musi być "code". W Implicit Grant musi być "token".')
@ns.param('client_id', 'ID Klienta.')
@ns.param('redirect_uri', """Adres przekierowania po uwierzytelnieniu.   
                    Opcjonalny, ale gdy podajemy, musi to być jedno z zarejestrowanych adresów URL.
                    W tej implementacji jest wymagany""")
@ns.param('scope', """Opcjonalny. Zakresy informacji/funkcji do których dostęp powinien potwierdzić użytkownika końcowy. 
                      Identyfikatory rozdzielone spacjami'. """)
@ns.param('state', '''Rekomendowany. Niejawny ciąg znaków, który zostanie przekazany z powrotem w odpowiedzi,  
a zatem może być używany do komunikowania stanu po stronie klienta  i zapobiegania atakom fałszowania zapytań - CSRF.''')
@ns.param('response_mode',
          '''Określa, czy parametry mają być dołączane do przekierowania w zapytaniu ("query"),  
          czy jako fragment URL ("fragment") - po znaku #.  
          Dla response_type=code wartością domyślną jest 'query' w p.p. - fragment.
          W tej implementacji parametr przyjmuje zawsze wartość domyślną (podana w zapytaniu jest ignorowana).''')
# zob, https://tools.ietf.org/html/rfc7636
#rfc7636 @ns.param('code_challenge', 'Kod do weryfikacji - opcjonalny')
#rfc7636 @ns.param('code_challenge_method', 'Metoda weryfikacji')
class AuthorizeClass(Resource):
#    @ns.marshal_with(Token)
    aparser=parser

    aparser.add_argument("response_type", type=str,required=True,
                                  choices=["token", "code", "id_token token", "id_token"])
    aparser.add_argument("client_id", type=str, default='', required=True)
    aparser.add_argument("redirect_uri", type=str, default='', required=True)
    aparser.add_argument("scope", type=str, default='',  required=False)
    aparser.add_argument("state", type=str, default='', required=False)
    aparser.add_argument("response_mode", type=str,  required=False)

    @ns.doc('autoryzacja')
    @ns.expect(aparser)
    def get(self):
        """
#Authorisation

Authorization Code Grant:  https://tools.ietf.org/html/rfc6749 4.1.1., 4.1.2

Implicit Grant: https://tools.ietf.org/html/rfc6749 4.2

"""
        try:
          args = parser.parse_args()
        except Exception as e:
          return {
            'error': 'Bad parameters',
            'error_description': str(e)
          }
        try:
          user_id = get_session_uid()
          # In case user is not logged in, we redirect to the login page and come back
          # Also if they didn't authenticate recently enough
          auth_time = get_session_auth_time()
          if not user_id or time_to_now(auth_time)>LOGIN_TIMEOUT:
            return {
              'error': 'Must login',
              'error_description': 'user is not logged in or login timeout'
            }
          (response_type, client_id, redirect_uri, scopes, state,
             code_challenge, code_challenge_method) = validator.check_oauth_authorize_args(args)
          response_params=handle_oauth_authorize(response_type, user_id, client_id,
                             redirect_uri, scopes, state)
          if 'error' in response_params:
            # If those are not valid, we must not redirect back to the client
            # - instead, we display a message to the user
            return response_params
          response_mode = 'query' if response_type == 'code' else 'fragment'
          location = '{}{}{}'.format(
            redirect_uri,
            '?' if response_mode == 'query' else '#',
            url_encode(response_params)
          )
          return redirect(location, code=302)
        except OAuthException as e:
          return {
            'error': e.type,
            'error_description': str(e)
          }


############# token

@ns.route('/token')
@ns.param('client_id', 'ID Klienta.')
@ns.param('grant_type','="authorization_code" - Required')
@ns.param('code', 'Kod uzyskany w zapytaniu /authorize - Required')
@ns.param('redirect_uri', 'Jesli podany na etapie autoryzacji - obowiązkowy (taki sam)')
@ns.param('client_secret', 'Tajne hasło uzyskane przy rejestracji aplikacji/klienta.')
#@ns.param('code_verifier', 'Obowiązkowy - o ile authorization request zawierał "code_challenge"')
class TokenClass(Resource):
    @ns.doc('token')
    @ns.marshal_with(Token)
    def post(self): 
        """

Authorization code grant

https://tools.ietf.org/html/rfc6749 4.1.3., 4.1.4

Przyklad:
     POST /token HTTP/1.1
     Host: server.example.com
     Authorization: Basic czZCaGRSa3F0MzpnWDFmQmF0M2JW
     Content-Type: application/x-www-form-urlencoded

     grant_type=authorization_code&code=SplxlOBeZQQYbYS6WxSbIA
     &redirect_uri=https%3A%2F%2Fclient%2Eexample%2Ecom%2Fcb

Zwraca JSON:
"access_token": "{Access Token}", // - Always included
"token_type": "{Token Type}", // - Always included
"expires_in": {Lifetime In Seconds}, // - Optional
"refresh_token": "{Refresh Token}", // - Optional
"scope": "{Scopes}" // - Mandatory if the granted scopes differ from the requested ones.
"""
        parser = reqparse.RequestParser()
        parser.add_argument('client_id', required=True, location='form')
        parser.add_argument('grant_type', required=True, location='form')
        parser.add_argument('code', required=True, location='form')
        parser.add_argument('redirect_uri', required=True, location='form')
        parser.add_argument('client_secret', required=False, location='form')
        parser.add_argument('code_verifier', required=False, location='form')
        args = parser.parse_args()
        try:
            if 'grant_type' not in args:
                raise OAuthException(
                    'grant_type param is missing',
                    OAuthException.INVALID_REQUEST,
                )
            if args['grant_type'] == 'authorization_code':
              (client_id, redirect_uri, client_secret, code ) = validator.check_grant_type_authorization_args(args)
              #return json.dumps(
              return handle_grant_type_authorization_code(client_id, redirect_uri, client_secret, code )
            elif args['grant_type'] == 'client_credentials':
              (client_id, client_secret)=validator.check_grant_type_client_args(args)
              return json.dumps(handle_grant_type_client_credentials(client_id, client_secret))
            else:
                raise OAuthException(
                    'Unsupported grant_type param: \'{}\''.format(args['grant_type']),
                    OAuthException.UNSUPPORTED_GRANT_TYPE,
                )
        except OAuthException as e:
            abort(400, str(e))


### introspect
@ns.route('/introspect')
@ns.param('token', 'Token - string. Required')
@ns.param('token_type_hint','Rodzaj tokenu. Domyślnie access_token - string.')
@ns.param('client_assertion_type', 'default: urn:ietf:params:oauth:client-assertion-type:jwt-bearer')
@ns.param('client_assertion', 'default: <<clientSecretJwt>>')

class IntrospectClass(Resource):

    @ns.marshal_with(TokenIntrospection)
    def post(self):
      """
      https://tools.ietf.org/html/rfc7662
      https://www.oauth.com/oauth2-servers/token-introspection-endpoint/

      W header:
      Accept
        domyślnie: 'application/json'
      Authorization
        domyślnie: 'Basic'
      """
      parser = reqparse.RequestParser()
      parser.add_argument('token', required=True, location='form')
      parser.add_argument('token_type_hint', required=False, location='form')
      parser.add_argument('client_assertion_type', required=False, location='form')
      parser.add_argument('client_assertion', required=False, location='form')
      args = parser.parse_args()
      abort(400, 'Not implemented yet')


### revoke
@ns.route('/revoke')
@ns.param('token', 'Token - string. Required')
@ns.param('token_type_hint','Rodzaj tokenu. Domyślnie access_token - string.')
class RevokeClass(Resource):
    def post(self):
      """
      tools.ietf.org/html/rfc7009
      https://www.oauth.com/oauth2-servers/listing-authorizations/revoking-access/

      W header:
      Accept
        domyślnie: 'application/json'
      Authorization
        domyślnie: 'Basic'
      """
      parser = reqparse.RequestParser()
      parser.add_argument('token', required=True, location='form')
      parser.add_argument('token_type_hint', required=False, location='form')
      args = parser.parse_args()
      abort(400, 'Not implemented yet')

@ns.route('/jwks')
class JwksClass(Resource):
  """

  Jeśli klient zechce odszyfrować id token - musi dostać klucz publiczny RSA
  """
  def get(self):
    keyset = jwk.JWKSet()
    keyset.add(
       get_id_token_jwk()
    )
    return keyset.export(private_keys=False)
