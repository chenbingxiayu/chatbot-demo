# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import gettext_lazy as _


class StaffStatus(models.Model):
    class Role(models.TextChoices):
        ONLINETRIAGE = 'online_triage', _('Online Triage')
        DO = 'do', _('DO')
        COUNSELLOR = 'counsellor', _('Counsellor')
        SUPERVISOR = 'supervisor', _('Supervisor')
        ADMIN = 'admin', _('Admin')

    class ChatStatus(models.TextChoices):
        AVAILABLE = 'available', _('Available'),
        CHATTING = 'chatting', _('Chatting'),
        OFFLINE = 'offline', _('Offline')

    staff_name = models.CharField(max_length=64)
    staff_netid = models.CharField(max_length=64, unique=True)
    staff_role = models.CharField(max_length=32, choices=Role.choices)
    staff_chat_status = models.CharField(max_length=32, choices=ChatStatus.choices)
    status_change_time = models.DateTimeField()

    def __str__(self):
        return f"Staff({self.staff_netid}: {self.staff_role})"


class StudentChatStatus(models.Model):
    class ChatStatus(models.TextChoices):
        WAITING = 'waiting', _('Waiting'),
        CHATTING = 'chatting', _('Chatting'),
        END = 'end', _('End')

    student_netid = models.CharField(max_length=64, unique=True)
    chat_request_time = models.DateTimeField(default=None, null=True)
    student_chat_status = models.CharField(max_length=32, choices=ChatStatus.choices)
    chat_start_time = models.DateTimeField(default=None, null=True)
    chat_end_time = models.DateTimeField(default=None, null=True)
    assigned_counsellor = models.ForeignKey(StaffStatus, null=True, on_delete=models.DO_NOTHING)
