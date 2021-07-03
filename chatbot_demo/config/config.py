import os
from types import MappingProxyType


_config = {
    "sso": {
        "secret": os.getenv("SSO_SECRET"),
        "algorithm": os.getenv("SSO_ALGORITHM"),
        "aud": os.getenv("SSO_AUD"),
        "destination": os.getenv("SSO_DESTINATION"),
    }
}

config = MappingProxyType(_config)