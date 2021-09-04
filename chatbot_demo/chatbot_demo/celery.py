import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chatbot_demo.settings")
app = Celery("chatbot_demo")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.enable_utc = False
app.autodiscover_tasks()
