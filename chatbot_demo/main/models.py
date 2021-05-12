# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

ROLE = [
    ('online_triage', 'ONLINE TRIAGE'),
    ('do', 'DO'),
    ('counsellor', 'COUNSELLOR'),
    ('online_triage', 'ONLINE TRIAGE')
]

STATUS = [
    ('available', 'Available'),
    ('away', 'Away'),
    ('chatting', 'Chatting')
]

CHAT_STATUS = [
    ('waiting', 'Waiting'),
    ('chatting', 'Chatting'),
    ('ended', 'Ended')
]


class User(models.Model):
    net_id = models.CharField(max_length=64, unique=True)
    role = models.CharField(max_length=32, choices=ROLE)
    status = models.CharField(max_length=32, choices=STATUS)
    last_update = models.DateTimeField()

    def __str__(self):
        return f"User({self.net_id}: {self.role})"

    def to_dict(self):
        return {
            "net_id": self.net_id,
            "role": self.role,
            "status": self.status,
            "last_update": str(self.last_update)
        }


class Chat(models.Model):
    student_netid = models.CharField(max_length=64)
    request_time = models.DateTimeField(default=None, null=True)
    chat_status = models.CharField(max_length=32, choices=CHAT_STATUS)
    start_time = models.DateTimeField(default=None, null=True)
    end_time = models.DateTimeField(default=None, null=True)
    counsellor = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    def to_dict(self):
        return {
            "student_netid": self.student_netid,
            "request_time": self.request_time,
            "chat_status": self.chat_status,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "counsellor": self.counsellor.to_dict()
        }
