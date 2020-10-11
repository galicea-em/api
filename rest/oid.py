# -*- coding: utf-8 -*-
# authors: Jerzy Wawro, Maciej Wawro
# (C) Galicea 2020

from datetime import datetime

LOGIN_TIMEOUT = 24*60*60 # seconds

RESPONSE_TYPES_SUPPORTED = [
    'code',
    'token',
#    'id_token token',
    'id_token'
]

class OAuthException(Exception):
    INVALID_REQUEST = 'invalid_request'
    INVALID_CLIENT = 'invalid_client'
    UNSUPPORTED_RESPONSE_TYPE = 'unsupported_response_type'
    INVALID_GRANT = 'invalid_grant'
    UNSUPPORTED_GRANT_TYPE = 'unsupported_grant_type'

    def __init__(self, message, type):
        super(Exception, self).__init__(message)
        self.type = type

# Python 3: datetime.now().timestamp() etc
def datetime_to_timestamp(dt):
    return (dt - datetime(1970, 1, 1)).total_seconds()

def time_to_now(ts):
    return int(datetime_to_timestamp(datetime.now())- ts)