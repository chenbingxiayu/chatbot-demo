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


# Create your models here.

class CounsellorStatus(models.Model):
    net_id = models.CharField(max_length=64, unique=True)
    role = models.CharField(max_length=32, choices=ROLE)
    status = models.CharField(max_length=32, choices=STATUS)
    last_update = models.DateTimeField()

    def to_dict(self):
        return {
            "net_id": self.net_id,
            "role": self.role,
            "status": self.status,
            "last_update": str(self.last_update)
        }
