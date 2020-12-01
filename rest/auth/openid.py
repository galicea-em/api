# coding: utf-8
# authors: Jerzy Wawro, Maciej Wawro
# (C) Galicea 2020

from flask_restx import Namespace, Resource, reqparse

from werkzeug.urls import url_encode
from flask import redirect

from .api_models import UserInfo
from .oid import OAuthException
from .oid_valid import validator
from .oid_handle import handle_oauth_authorize
from .oid_flask import get_session_uid
from .oid_decorator import resource
from .oid_base import get_user


ns = Namespace('openid', description='OpenID Connect')
parser = reqparse.RequestParser()

@ns.route('/authorize')
@ns.param('scope', '''Opcjonalny. Zakresy informacji/funkcji do których dostęp powinien potwierdzić użytkownika końcowy. 
                      Identyfikatory rozdzielone spacjami. Dla  OpenID Connect (OIDC) wśród nich zawsze musi być "openid" ''',
                  default='openid')
@ns.param('response_type', '''Typ odpowiedzi.  Prawidłowe odpowiedzi to:
 "code"," id_token", "token", "token_id_token",  "code_id_token", "code_token" oraz "code_tokenid_token".
''')
@ns.param('client_id', 'ID Klienta.')
@ns.param('redirect_uri', """Adres przekierowania po uwierzytelnieniu.   
                    Opcjonalny, ale gdy podajemy, musi to być jedno z zarejestrowanych adresów URL.
                    W tej implementacji jest wymagany""")
@ns.param('state', '''Rekomendowany. Niejawny ciąg znaków, który zostanie przekazany z powrotem w odpowiedzi,  
a zatem może być używany do komunikowania stanu po stronie klienta  i zapobiegania atakom fałszowania zapytań - CSRF.''')
@ns.param('response_mode',
          '''Określa, czy parametry mają być dołączane do przekierowania w zapytaniu ("query"),  
          czy jako fragment URL ("fragment") - po znaku #.  
          Dla response_type=code wartością domyślną jest 'query' w p.p. - fragment.
          W tej implementacji parametr przyjmuje zawsze wartość domyślną (podana w zapytaniu jest ignorowana).''')

@ns.param('nonce', '''Parametr nonce przez klienta jest zawarty w każdym tokenie  wygenerowanym dla sesji.  
  Uniemożliwia ponowne wykorzystanie zgłoszeń przechwyconych przez nieuprawnione osoby (tak zwany atak powtórki).  
  zob. https://hueniverse.com/beginners-guide-to-oauth-part-iii-security-architecture-e9394f5263b5.''')
@ns.param('display',
          '''Tryb wyświetlania uwierzytelnienia, który może być  "page"," popup" lub "modal". Domyślne jest "page".
          W tej implementacji ignorowany. ''')
@ns.param('prompt',
          '''Rozdzielana spacjami lista (znaki ASCII uwzględniająca wielkość liter, która określa, 
          czy serwer autoryzacji monituje użytkownika końcowego o ponowne  uwierzytelnienie i zgodę. 
          Obsługiwane wartości to  "none", "login", "consent", "select_account".  
          W tej implementacji ignorowany. 
          ''')
@ns.param('max_age', 'Określa dozwolony czas w sekundach od czasu ostatniego aktywnego uwierzytelnienia użytkownika końcowego. ')
@ns.param('ui_locales', '''Określa preferowany język do użycia na stronie autoryzacji,  
jako oddzieloną spacjami listę znaczników języka BCP47.
Lista uporządkowana według preferencji. Na przykład wartość „fr-CA fr en”.
''')
@ns.param('id_token_hint', '''Opcjonalny. W tej implementacji ignorowany.''')
@ns.param('login_hint', '''Podpowiedź dotycząca identyfikatora logowania. Opcjonalny. W tej implementacji ignorowany. 
''')
@ns.param('acr_values', '''Konteksty autoryzacji. Łańcuch identyfikatorów oddzielonych spacjami - 
według preferencji. Używa wartość może zostać przekazana w polu arc generowanego tokenu JWT 
(https://openid.net/specs/openid-connect-core-1_0.html#IDToken).
Opcjonalny. W tej implementacji ignorowany.
''')
class OpenIdAuthorizeClass(Resource):
    aparser=parser

    aparser.add_argument("scope", type=str, default='',  required=True)
    aparser.add_argument("response_type", type=str,required=True,
                                  choices=["token", "code", "id_token token", "id_token", "code id_token"])
    aparser.add_argument("client_id", type=str, default='', required=True)
    aparser.add_argument("redirect_uri", type=str, default='', required=True)
    aparser.add_argument("state", type=str, default='', required=False)
    aparser.add_argument("response_mode", type=str,  required=False)
    aparser.add_argument("nonce", type=str, required=False)
    aparser.add_argument("display", type=str, required=False, choices=['page','popup','touch','page','wap'])
    aparser.add_argument("prompt", type=str, required=False)
    aparser.add_argument("max_age", type=int, default='', required=False)
    aparser.add_argument("ui_locales", type=str, default='', required=False)
    aparser.add_argument("id_token_hint", type=str, default='', required=False)
    aparser.add_argument("login_hint", type=str, default='', required=False)
    aparser.add_argument("acr_values", type=str, default='', required=False)

    def get(self):

        """

        https://openid.net/specs/openid-connect-core-1_0.html#CodeFlowSteps


        """
        try:
          user_id = get_session_uid()
          args = parser.parse_args()
          (response_type, client_id, redirect_uri, state, response_mode,
           nonce, display, prompt, max_age, ui_locales, id_token_hint, login_hint,
           acr_values
           ) = validator.check_openid_authorize_args(args)
          response_params=handle_oauth_authorize(response_type, user_id, client_id,
                             redirect_uri, ['openid',], state)
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
        except Exception as e0:
            return {
                'error': 'Internal error',
                'error_description': str(e0)
            }



@ns.route('/userinfo')
class UserInfoClass(Resource):

    @resource('user')
    @ns.marshal_with(UserInfo)
    def get(self):
        """
        UserInfo 

        https://openid.net/specs/openid-connect-core-1_0.html#UserInfo

        Przyklad pytania:
          GET /userinfo HTTP/1.1
  Host: server.example.com
  Authorization: Bearer SlAV32hkKG
        Przyklad odpowiedzi:
        HTTP/1.1 200 OK
  Content-Type: application/json

  {
   "sub": "248289761001",
   "name": "Jane Doe",
   "given_name": "Jane",
   "family_name": "Doe",
   "preferred_username": "j.doe",
   "email": "janedoe@example.com",
   "picture": "http://example.com/janedoe/me.jpg"
  }

  Przyklad bedu:
   HTTP/1.1 401 Unauthorized
  WWW-Authenticate: error="invalid_token",
    error_description="The Access Token expired"

        """
        try:
          user_id = get_session_uid()
          user=get_user(user_id)
          if user:
            return {
              'sub': str(user.id),
              'name': user.name,
              'email': user.email
            }
          else:
            return {
              'error': 'unknown',
              'error_description': 'User not found in database'
            }

        except Exception as e:
          return {
            'error': 'system',
            'error_description': str(e)
          }

