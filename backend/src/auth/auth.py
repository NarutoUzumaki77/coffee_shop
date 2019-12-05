import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen
from src.logger import logging


AUTH0_DOMAIN = 'dev-b1cng-y2.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'http://127.0.0.1:5000/drinks'


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Todo it should raise an AuthError if the header is malformed
def get_token_auth_header():
    """
    Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get('Authorization', None)
    if not auth:
        logging.info('authorization_header_missing')
        logging.info('Authorization header is expected.')
        return abort(401)

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        logging.info('invalid_header')
        logging.info('Authorization header must start with "Bearer".')
        return abort(401)

    elif len(parts) == 1:
        logging.info('invalid_header')
        logging.info('Token not found.')
        return abort(401)

    elif len(parts) > 2:
        logging.info('invalid_header')
        logging.info('Authorization header must be bearer token.')
        abort(401)

    token = parts[1]
    return token


def check_permission(permission, payload):
    if 'permissions' not in payload:
        abort(403)
    if permission not in payload['permissions']:
        abort(403)
    return True


def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        logging.info('invalid_header')
        logging.info('Authorization malformed.')
        return abort(401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            logging.info('token_expired')
            logging.info('Token expired.')
            return abort(401)

        except jwt.JWTClaimsError:
            logging.info('invalid_claims')
            logging.info('Incorrect claims. Please, check the audience '
                         'and issuer.')
            return abort(401)
        except Exception:
            logging.info('invalid_header')
            logging.info('Unable to parse authentication token.')
            return abort(401)
    logging.info('invalid_header')
    logging.info('Unable to find the appropriate key.')
    return abort(400)


def requires_auth(permission=''):
    def require_auth_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)
            except:
                abort(401)

            check_permission(permission, payload)

            return func(payload, *args, **kwargs)

        return wrapper

    return require_auth_decorator
