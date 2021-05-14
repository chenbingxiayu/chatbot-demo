# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

ROLE = [
    ('online_triage', 'Online Triage'),
    ('do', 'DO'),
    ('counsellor', 'Counsellor'),
    ('supervisor', 'Supervisor'),
    ('admin', 'Admin')
]

STAFF_STATUS = [
    ('available', 'Available'),
    ('chatting', 'Chatting'),
    ('offline', 'Offline')
]

CHAT_STATUS = [
    ('waiting', 'Waiting'),
    ('chatting', 'Chatting'),
    ('end', 'End')
]


class StaffStatus(models.Model):
    staff_name = models.CharField(max_length=64)
    staff_net_id = models.CharField(max_length=64, unique=True)
    staff_role = models.CharField(max_length=32, choices=ROLE)
    staff_chat_status = models.CharField(max_length=32, choices=STAFF_STATUS)
    status_change_time = models.DateTimeField()

    def __str__(self):
        return f"Staff({self.staff_net_id}: {self.staff_role})"


class StudentChatStatus(models.Model):
    student_netid = models.CharField(max_length=64)
    chat_request_time = models.DateTimeField(default=None, null=True)
    student_chat_status = models.CharField(max_length=32, choices=CHAT_STATUS)
    chat_start_time = models.DateTimeField(default=None, null=True)
    chat_end_time = models.DateTimeField(default=None, null=True)
    assigned_counsellor_id = models.ForeignKey(StaffStatus, null=True, on_delete=models.DO_NOTHING)
