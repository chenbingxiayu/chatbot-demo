# -*- coding: utf-8 -*-
from __future__ import unicode_literals, annotations
import logging

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()


class StaffStatus(models.Model):
    class Role(models.TextChoices):
        ONLINETRIAGE = 'online_triage', _('Online Triage')
        DO = 'do', _('DO')
        COUNSELLOR = 'counsellor', _('Counsellor')
        SUPERVISOR = 'supervisor', _('Supervisor')
        ADMIN = 'admin', _('Admin')

    class ChatStatus(models.TextChoices):
        AVAILABLE = 'available', _('Available'),
        AWAY = 'away', _('Away'),
        ASSIGNED = 'assigned', _('Assigned'),
        CHATTING = 'chatting', _('Chatting'),
        OFFLINE = 'offline', _('Offline')

    staff_name = models.CharField(max_length=64)
    staff_netid = models.CharField(max_length=64, unique=True)
    staff_role = models.CharField(max_length=32, choices=Role.choices)
    staff_chat_status = models.CharField(max_length=32, choices=ChatStatus.choices)
    status_change_time = models.DateTimeField()

    def __str__(self):
        return f"Staff({self.staff_netid}: {self.staff_role})"

    @classmethod
    def get_random_staff_by_role(cls, role: StaffStatus.Role):
        staff = cls.objects \
            .filter(staff_chat_status=cls.ChatStatus.AVAILABLE,
                    staff_role=role) \
            .order_by('?') \
            .first()

        return staff

    def assign_to(self, student: StudentChatStatus):
        student.assigned_counsellor_id = self
        student.student_chat_status = StudentChatStatus.ChatStatus.ASSIGNED
        self.staff_chat_status = StaffStatus.ChatStatus.ASSIGNED
        self.status_change_time = timezone.now()
        student.save()
        self.save()
        logger.info(f"{self} assigned to {student}")
        self.notify_assignment(student_pk=student.pk)

    def notify_assignment(self, student_pk: str):
        logger.info("notify staff")
        async_to_sync(channel_layer.group_send)(
            f'staff_{self.staff_netid}', {
                'type': 'send_assignment_alert',
                'content': {
                    'type': 'assignment',
                    'student_pk': student_pk
                }
            })


class StudentChatStatus(models.Model):
    class ChatStatus(models.TextChoices):
        WAITING = 'waiting', _('Waiting'),
        CHATTING = 'chatting', _('Chatting'),
        ASSIGNED = 'assigned', _('Assigned'),
        END = 'end', _('End')

    student_netid = models.CharField(max_length=64, unique=True)
    chat_request_time = models.DateTimeField(auto_now=True, null=True)
    student_chat_status = models.CharField(max_length=32, choices=ChatStatus.choices, null=True)
    chat_start_time = models.DateTimeField(default=None, null=True)
    chat_end_time = models.DateTimeField(default=None, null=True)
    assigned_counsellor = models.ForeignKey(StaffStatus, null=True, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f"Student({self.student_netid})"

    def add_to_queue(self):
        self.student_chat_status = StudentChatStatus.ChatStatus.WAITING
        self.save()


STAFF_ORDER = [StaffStatus.Role.ONLINETRIAGE,
               StaffStatus.Role.DO,
               StaffStatus.Role.COUNSELLOR]
