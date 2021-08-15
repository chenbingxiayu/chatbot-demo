import uuid
from datetime import datetime

import pendulum
from typing import Optional

from django.utils import timezone
from django.conf import settings

hk_time = pendulum.timezone(settings.TIME_ZONE)
utc_time = pendulum.timezone('utc')
tz_offset = 8


def today_start() -> datetime:
    """
    Y-m-D 00:00:00T+0800

    :return:
    """
    return timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)


def uuid2str(obj: uuid.UUID) -> str:
    return str(obj)


def str2uuid(string: str) -> uuid.UUID:
    return uuid.UUID(string)
