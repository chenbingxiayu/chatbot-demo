# -*- coding: utf-8 -*-
from __future__ import unicode_literals, annotations
import logging
from datetime import datetime

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()


class StaffStatus(models.Model):
    """
    Attributes
        staff_netid:            Staff' net ID
        staff_name:             Staff's name
        staff_role:             Staff's role
        staff_chat_status:      Staff's chat status
        status_change_time:     Last status changing time
        staff_stream_id:        Chatroom id
    """

    class Meta:
        db_table = 'staff-status'

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

    staff_netid = models.CharField(max_length=64, primary_key=True)
    staff_name = models.CharField(max_length=64)
    staff_role = models.CharField(max_length=32, choices=Role.choices)
    staff_chat_status = models.CharField(max_length=32, choices=ChatStatus.choices)
    status_change_time = models.DateTimeField()
    staff_stream_id = models.CharField(max_length=32, null=True)

    def __str__(self):
        return f"Staff({self.staff_netid}: {self.staff_role})"

    @classmethod
    def get_random_staff_by_role(cls, role: StaffStatus.Role) -> StaffStatus:
        staff = cls.objects \
            .select_for_update() \
            .filter(staff_chat_status=cls.ChatStatus.AVAILABLE,
                    staff_role=role) \
            .order_by('?') \
            .first()

        return staff

    def assign_to(self, student: StudentChatStatus):
        now = timezone.now()

        # change original assigned staff back to available
        original_assign_staff = student.assigned_counsellor
        if original_assign_staff:  # when re-assigning counsellor
            if original_assign_staff.staff_chat_status == StaffStatus.ChatStatus.ASSIGNED:
                original_assign_staff.staff_chat_status = StaffStatus.ChatStatus.AVAILABLE
            original_assign_staff.save()

        student.assigned_counsellor = self
        student.student_chat_status = StudentChatStatus.ChatStatus.ASSIGNED
        student.last_assign_time = now
        self.staff_chat_status = StaffStatus.ChatStatus.ASSIGNED
        self.status_change_time = now
        student.save()
        self.save()

    def notify_assignment(self):
        logger.info("notify staff")
        async_to_sync(channel_layer.group_send)(
            f'staff_{self.staff_netid}', {
                'type': 'send_assignment_alert',
                'content': {
                    'type': 'assignment'
                }
            })
        # TODO: send email


class StudentChatStatus(models.Model):
    """
    Attributes
        id:                     Primary key of this table
        student_netid:          Student's net ID
        student_chat_status:    Student's chat status
        chat_request_time:      The time that this student make the chat request
        last_assign_time:       The time that assign a staff to this student
        chat_start_time:        The time that the chat start
        assigned_counsellor:    The counsellor assigned to this student
    """

    class Meta:
        db_table = 'student-chat-status'

    class ChatStatus(models.TextChoices):
        WAITING = 'waiting', _('Waiting'),
        CHATTING = 'chatting', _('Chatting'),
        ASSIGNED = 'assigned', _('Assigned')

    id = models.AutoField(primary_key=True)
    student_netid = models.CharField(max_length=64, unique=True)
    student_chat_status = models.CharField(max_length=32, choices=ChatStatus.choices, null=True)
    chat_request_time = models.DateTimeField(default=timezone.now, null=True)
    last_assign_time = models.DateTimeField(default=None, null=True)
    chat_start_time = models.DateTimeField(default=None, null=True)
    assigned_counsellor = models.OneToOneField(StaffStatus, null=True, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f"Student({self.student_netid})"

    def add_to_queue(self):
        self.student_chat_status = StudentChatStatus.ChatStatus.WAITING
        self.save()


class StudentChatHistory(models.Model):
    """
    Attributes
        id:                     Primary key of this table
        student_netid:          Student's net ID
        student_chat_status:    Student's chat status
        chat_request_time:      The time that this student make the chat request
        chat_start_time:        The time that the chat starts
        chat_end_time:          The time that the chat ends
        assigned_counsellor:    The counsellor assigned to this student
    """

    class Meta:
        db_table = 'student-chat-history'

    id = models.AutoField(primary_key=True)
    student_netid = models.CharField(max_length=64)
    student_chat_status = models.CharField(max_length=32, choices=StudentChatStatus.ChatStatus.choices, null=True)
    chat_request_time = models.DateTimeField(default=timezone.now, null=True)
    chat_start_time = models.DateTimeField(default=None, null=True)
    chat_end_time = models.DateTimeField(default=None, null=True)
    assigned_counsellor = models.ForeignKey(StaffStatus, null=True, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f"ChatHistory({self.student_netid})"

    @classmethod
    def append_end_chat(cls, student: StudentChatStatus, time: datetime):
        cls(student_netid=student.student_netid,
            student_chat_status=student.student_chat_status,
            chat_request_time=student.chat_request_time,
            chat_start_time=student.chat_start_time,
            chat_end_time=time,
            assigned_counsellor=student.assigned_counsellor).save()


ROLE_RANKING = [StaffStatus.Role.ONLINETRIAGE,
                StaffStatus.Role.DO,
                StaffStatus.Role.COUNSELLOR]


