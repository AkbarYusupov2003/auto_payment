import jwt
from django.conf import settings


def get_data_from_token(token):
    return jwt.decode(token[7:], key=settings.SPLAY_JWT_KEY, algorithms=("HS256",), options={"verify_signature": True})
