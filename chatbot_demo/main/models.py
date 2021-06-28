# -*- coding: utf-8 -*-
from __future__ import unicode_literals, annotations
import logging
from datetime import datetime

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from main.email_service import email_service

logger = logging.getLogger('django')
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
        AVAILABLE = 'available', _('Available')
        AWAY = 'away', _('Away')
        ASSIGNED = 'assigned', _('Assigned')
        CHATTING = 'chatting', _('Chatting')
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

        email_service.send('new_assignment', self.staff_netid)


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
        is_supervisor_join:     Whether a supervisory joined or not
    """

    class Meta:
        db_table = 'student-chat-status'

    class ChatStatus(models.TextChoices):
        WAITING = 'waiting', _('Waiting')
        CHATTING = 'chatting', _('Chatting')
        ASSIGNED = 'assigned', _('Assigned')
        END = 'end', _('End')

    id = models.AutoField(primary_key=True)
    student_netid = models.CharField(max_length=64, unique=True)
    student_chat_status = models.CharField(max_length=32, choices=ChatStatus.choices, null=True)
    chat_request_time = models.DateTimeField(default=timezone.now, null=True)
    last_assign_time = models.DateTimeField(default=None, null=True)
    chat_start_time = models.DateTimeField(default=None, null=True)
    assigned_counsellor = models.OneToOneField(StaffStatus, null=True, on_delete=models.DO_NOTHING)
    is_supervisor_join = models.BooleanField(default=False)

    def __str__(self):
        return f"Student({self.student_netid})"

    def add_to_queue(self):
        self.student_chat_status = StudentChatStatus.ChatStatus.WAITING
        self.save()


class StudentChatHistory(models.Model):
    """
    Attributes
        session_id:                     Primary key of this table
        student_netid:          Student's net ID
        student_chat_status:    Student's chat status
        chat_request_time:      The time that this student make the chat request
        chat_start_time:        The time that the chat starts
        chat_end_time:          The time that the chat ends
        assigned_counsellor:    The counsellor assigned to this student
        is_supervisor_join:     Whether a supervisory joined or not
        is_no_show:             Whether the student is no show
    """

    class Meta:
        db_table = 'student-chat-history'

    session_id = models.AutoField(primary_key=True)  # This can be session id
    student_netid = models.CharField(max_length=64)
    student_chat_status = models.CharField(max_length=32, choices=StudentChatStatus.ChatStatus.choices, null=True)
    chat_request_time = models.DateTimeField(default=timezone.now, null=True)
    chat_start_time = models.DateTimeField(default=None, null=True)
    chat_end_time = models.DateTimeField(default=None, null=True)
    assigned_counsellor = models.ForeignKey(StaffStatus, null=True, on_delete=models.DO_NOTHING)
    is_supervisor_join = models.BooleanField(default=False)
    is_no_show = models.BooleanField(default=False)

    def __str__(self):
        return f"ChatHistory({self.student_netid})"

    @classmethod
    def append_end_chat(cls, student: StudentChatStatus, time: datetime):
        cls(student_netid=student.student_netid,
            student_chat_status=StudentChatStatus.ChatStatus.END,
            chat_request_time=student.chat_request_time,
            chat_start_time=student.chat_start_time,
            chat_end_time=time,
            assigned_counsellor=student.assigned_counsellor).save()


class CounsellingServiceSession(models.Model):
    """
    Attributes
        session_id:                     Id of this counselling service session. UUID.hex format
        student_netid:                  student_netid
        start_time:                     The time of login to this system
        end_time:                       The time of session close
        is_ployu_student:               Whether the user is a PolyU's student
        language:                       Language preference
        q1_academic:                    Choice/Answer of the chatbot survey
        q1_interpersonal_relationship:  Choice/Answer of the chatbot survey
        q1_career:                      Choice/Answer of the chatbot survey
        q1_family:                      Choice/Answer of the chatbot survey
        q1_mental_health:               Choice/Answer of the chatbot survey
        q1_others:                      Choice/Answer of the chatbot survey
        q2:                             Choice/Answer of the chatbot survey
        q3:                             Choice/Answer of the chatbot survey
        q4:                             Choice/Answer of the chatbot survey
        q5:                             Choice/Answer of the chatbot survey
        q6_1:                           Choice/Answer of the chatbot survey
        q6_2:                           Choice/Answer of the chatbot survey
        score:                          Score of the survey
        first_option:                   First selection after the survey
        feedback_rating:                Feedback rating of the counselling service
        chat_record:                    Refer to the chat history in the same session
    """

    class Meta:
        db_table = 'counselling-service-session'

    class Language(models.TextChoices):
        en_us = 'en-us', _('English')
        zh_hk = 'zh-hk', _('繁體中文')

    class FrequencyScale(models.TextChoices):
        rarely = 'rarely', _('Rarely')
        seldom = 'seldom', _('Seldom')
        sometimes = 'sometimes', _('Sometimes')
        often = 'often', _('Often')
        always = 'always', _('Always')

    class RecommendOptions(models.TextChoices):
        opt1 = 'mental_health_101', _('Mental Health 101')
        opt2 = 'make_appointment_with_sao_counsellors', _('Make appointment with SAO counsellors')
        opt3 = 'immediate_contact_with_sao_counsellors', _('Immediate contact with SAO counsellors')
        opt4 = 'immediate_contact_with_polyu_line', _('Immediate contact with PolyU line')
        opt5 = 'online_chat_service', _('Online Chat Service')
        opt6 = 'community_helpline', _('Community Helpline')

    session_id = models.CharField(max_length=32, primary_key=True)
    student_netid = models.CharField(max_length=32, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    is_ployu_student = models.BooleanField()
    language = models.CharField(max_length=8, choices=Language.choices, null=True)
    q1_academic = models.BooleanField(null=True)
    q1_interpersonal_relationship = models.BooleanField(null=True)
    q1_career = models.BooleanField(null=True)
    q1_family = models.BooleanField(null=True)
    q1_mental_health = models.BooleanField(null=True)
    q1_others = models.BooleanField(null=True)
    q2 = models.BooleanField(null=True)
    q3 = models.CharField(max_length=32, choices=FrequencyScale.choices, null=True)
    q4 = models.CharField(max_length=32, choices=FrequencyScale.choices, null=True)
    q5 = models.BooleanField(null=True)
    q6_1 = models.BooleanField(null=True)
    q6_2 = models.BooleanField(null=True)
    score = models.IntegerField(null=True, validators=[MinValueValidator(0), MaxValueValidator(13)])
    first_option = models.CharField(max_length=128, choices=RecommendOptions.choices, null=True)
    feedback_rating = models.IntegerField(null=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    chat_record = models.ForeignKey(StudentChatHistory, null=True, on_delete=models.DO_NOTHING)

    @classmethod
    def statis_overview(cls, start: datetime, end: datetime):
        # No. of non-office hour access = no_of_access - access_office_hr_count
        # No. of non-student = no_of_access - polyu_student_count
        res = cls.objects.raw(f"""
            WITH 
                selected_table AS  (
                SELECT 
                    *
                FROM
                    chatbot.`chat-survey-data`
                WHERE
                    chatbot.`chat-survey-data`.`date` BETWEEN '{start}' AND '{end}')
            SELECT 
             (SELECT count(*) FROM selected_table) AS no_of_access,
             (SELECT count(*) FROM selected_table WHERE start_time > '09:00:00' AND start_time < '19:00:00' AND weekday(start_time) IN (0, 1, 2, 3, 4) 
                                                        OR start_time > '09:00:00' AND start_time < '12:00:00' AND weekday(start_time)=5) AS access_office_hr_count,
             (SELECT count(*) FROM selected_table WHERE is_ployu_student=1 ) AS polyu_student_count,
             (SELECT count(*) FROM selected_table WHERE score<=6 ) AS score_green_count,
             (SELECT count(*) FROM selected_table WHERE score>=7 AND score<=10 ) AS score_yellow_count,
             (SELECT count(*) FROM selected_table WHERE score>=11 AND score<=13 ) AS score_red_count,
             (SELECT count(*) FROM selected_table WHERE first_option='mental_health_101' ) AS first_option,
             (SELECT count(*) FROM selected_table WHERE first_option='online_chat_service' ) AS first_option,
             (SELECT count(*) FROM selected_table LEFT JOIN chatbot.`student-chat-history` USING (session_id) WHERE student_chat_status='end' ) AS first_option
            """)

        return res

    @classmethod
    def statis_red_students(cls, start_date: datetime):
        res = cls.objects \
            .filter(date__gte=start_date, score__gte=11) \
            .values('student_netid', 'date', 'start_time', 'end_time')

        return res

    @staticmethod
    def to_excel(result):
        return


ROLE_RANKING = [StaffStatus.Role.ONLINETRIAGE,
                StaffStatus.Role.DO,
                StaffStatus.Role.COUNSELLOR]

SELECTABLE_STATUS = {
    StaffStatus.ChatStatus.AVAILABLE: [
        StaffStatus.ChatStatus.AVAILABLE,
        StaffStatus.ChatStatus.ASSIGNED,
        StaffStatus.ChatStatus.CHATTING
    ],
    StaffStatus.ChatStatus.AWAY: [StaffStatus.ChatStatus.AWAY]
}
