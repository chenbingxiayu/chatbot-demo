from datetime import datetime
from pendulum import timezone
from django.conf import settings

hk_time = timezone(settings.TIME_ZONE)


def today_start() -> datetime:
    """
    Y-m-D 00:00:00T+0800

    :return:
    """
    return datetime.combine(datetime.today().date(), datetime.min.time()).astimezone(hk_time)
