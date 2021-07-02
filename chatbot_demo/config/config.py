import os
from types import MappingProxyType


_config = {
    "sso": {
        "secret": os.getenv("SSO_SECRET", "joneslPRe2o0otrozlmldi9Ab15adradro5r86lthu5tiw0lspU3Hu119uSwo1ac"),
        "algorithm": os.getenv("SSO_ALGORITHM", "HS256"),
        "aud": os.getenv("SSO_AUD", 'http://10.13.46.22/main/user/login-sso/callback/'),
        "destination": os.getenv("SSO_DESTINATION", 'https://rapidauth-uat.polyu.edu.hk/polyuapp/sao/sso-login/index.php'),
    }
}

config = MappingProxyType(_config)