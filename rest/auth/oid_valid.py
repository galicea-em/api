# -*- coding: utf-8 -*-
# authors: Jerzy Wawro, Maciej Wawro
# (C) Galicea 2020


from .oid_base import get_client, int_client_id, ext_client_id, int_user_id, ext_client_id
from .oid import OAuthException, RESPONSE_TYPES_SUPPORTED


###

class OAuthValidator():

    def valid_response_type(self, response_type):
        if response_type not in RESPONSE_TYPES_SUPPORTED:
          raise OAuthException(
            'The only supported response_types are: {}'.format(', '.join(RESPONSE_TYPES_SUPPORTED)),
            OAuthException.UNSUPPORTED_RESPONSE_TYPE,
          )
        return response_type

    def validate_client(self, client_id):
        app = get_client(int(client_id))
        if not app:
            raise OAuthException(
                'client_id param is invalid',
                OAuthException.INVALID_CLIENT,
            )
        return app

    def validate_redirect_uri(self, app, redirect_uri):
        if app.auth_redirect_uri != redirect_uri:
            raise OAuthException(
                'redirect_uri param doesn\'t match the pre-configured redirect URI',
                OAuthException.INVALID_GRANT,
            )
        return redirect_uri

    def validate_client_secret(self, app, client_secret):
        if (not client_secret) or client_secret != app.secret:
            raise OAuthException(
                'client_secret param is not valid',
                OAuthException.INVALID_CLIENT,
            )

    def valid_response_mode(self, response_mode, response_type):
        if not response_mode:
          return 'query' if response_type == 'code' else 'fragment'
        elif response_mode not in ['query', 'fragment']:
          raise OAuthException(
          'The only supported response_modes are \'query\' and \'fragment\'',
          OAuthException.INVALID_REQUEST
          )
        return response_mode

    def arg_or_null(self, args, id):
      return args[id] if id in args else None

    def check_oauth_authorize_args(self, args):
        response_type = self.valid_response_type(args['response_type'])
        if 'client_id' not in args:
          raise OAuthException(
            'client_id param is missing',
            OAuthException.INVALID_CLIENT,
          )
        client_id = int_client_id(args['client_id'])
        if 'redirect_uri' not in args:
          raise OAuthException(
            'redirect_uri param is missing',
            OAuthException.INVALID_GRANT,
          )
        redirect_uri = args['redirect_uri']
        scopes = args.get('scope').split(' ') if args.get('scope') else []
        response_mode=args.get('response_mode')
        if not response_mode:
          response_mode= 'query' if response_type == 'code' else 'fragment'
        return (response_type,
                client_id,
                redirect_uri,
                scopes,
                self.arg_or_null(args, 'state'),
                response_mode,
                self.arg_or_null(args, 'code_challenge'),
                self.arg_or_null(args, 'code_challenge_method')
                )

    def check_grant_type_authorization_args(self, args):
      if 'client_id' not in args:
        raise OAuthException(
          'client_id param is missing',
          OAuthException.INVALID_CLIENT,
        )
      return (
        int_client_id(args['client_id']),
        args['redirect_uri'],
        self.arg_or_null(args, 'client_secret'),
        self.arg_or_null(args, 'code'),
        self.arg_or_null(args, 'scope')
      )


    def check_grant_type_client_args(self, args):
      if 'client_id' not in args:
        raise OAuthException(
          'client_id param is missing',
          OAuthException.INVALID_CLIENT,
        )
      return (
        int_client_id(args['client_id']),
        args['client_secret'],
        self.arg_or_null(args, 'scope')
      )

    def check_openid_authorize_args(self, args):
        if 'scope' not in args or args['scope'] != 'openid':
          raise OAuthException(
            'scope must be openid',
            OAuthException.INVALID_REQUEST,
          )
        response_type = self.valid_response_type(args['response_type'])
        if 'client_id' not in args:
          raise OAuthException(
            'client_id param is missing',
            OAuthException.INVALID_CLIENT,
          )
        client_id = int_client_id(args['client_id'])
        if 'redirect_uri' not in args:
          raise OAuthException(
            'redirect_uri param is missing',
            OAuthException.INVALID_GRANT,
          )
        max_age = int(args['max_age']) if ('max_age' in args and args['max_age']) else 0

        return (response_type,
                client_id,
                self.arg_or_null(args, 'redirect_uri'),
                self.arg_or_null(args, 'state'),
                self.arg_or_null(args, 'response_mode'),
                self.arg_or_null(args, 'nonce'),
                self.arg_or_null(args, 'display'),
                self.arg_or_null(args, 'prompt'),
                max_age,
                self.arg_or_null(args, 'ui_locales'),
                self.arg_or_null(args, 'id_token_hint'),
                self.arg_or_null(args, 'login_hint'),
                self.arg_or_null(args, 'acr_values')
                )


validator = OAuthValidator()