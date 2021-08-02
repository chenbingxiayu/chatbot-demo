import os
from typing import Dict

import jwt
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class AuthBackend(ModelBackend):
    """Log in to Django without providing a password.
    """

    def authenticate(self, request, username: str = None):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None


class SSOAuth:
    __secret: str = os.getenv('SSO_SECRET')
    __aud: str = os.getenv('SSO_AUD')
    __algorithm: str = os.getenv('SSO_ALGORITHM')
    __destination: str = os.getenv('SSO_DESTINATION')

    @property
    def secret(self) -> str:
        return self.__secret

    @property
    def aud(self) -> str:
        return self.__aud

    @property
    def algorithm(self) -> str:
        return self.__algorithm

    @property
    def destination(self) -> str:
        return self.__destination

    def decode(self, token: str) -> Dict:
        decoded_jwt = jwt.decode(token, self.secret, audience=self.aud, algorithms=[self.algorithm])
        return decoded_jwt

    def encode(self, data: Dict) -> str:
        encoded_jwt = jwt.encode(data, self.secret, algorithm=self.algorithm)
        return encoded_jwt


sso_auth = SSOAuth()
