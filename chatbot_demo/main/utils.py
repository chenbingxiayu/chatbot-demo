import uuid
from datetime import datetime, date, timedelta
from io import BytesIO
from typing import Dict
from zipfile import ZipFile

import pendulum
from django.conf import settings
from django.utils import timezone

hk_time = pendulum.timezone(settings.TIME_ZONE)
utc_time = pendulum.timezone('utc')
tz_offset = 8


def day_start(d: date = None) -> datetime:
    """
    Return day start of today if no args provided
    Y-m-D 00:00:00T+0800

    :return:
    """
    d = d or timezone.localdate()
    return datetime.combine(d, datetime.min.time())


def uuid2str(obj: uuid.UUID) -> str:
    return str(obj)


def str2uuid(string: str) -> uuid.UUID:
    return uuid.UUID(string)


def get_duration(t: timedelta) -> str:
    return f"{t.total_seconds() // 60}:{t.seconds}"


def write_zip_files(files: Dict[str, BytesIO]):
    """

    :param files: key: filename, value: file
    :return:
    """
    out = BytesIO()
    with ZipFile(out, 'w') as f:
        for filename, data in files.items():
            f.writestr(filename, data.getvalue())
    out.seek(0)
    return out
