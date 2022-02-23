# -*- coding: utf-8 -*-
from __future__ import unicode_literals, annotations

import io
import logging
import threading
import uuid
from datetime import datetime, timedelta
from typing import Dict, List

import xlsxwriter
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, connection
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from marshmallow import ValidationError

from main.email_service import email_service
from main.exceptions import UnauthorizedException, NotFound
from main.utils import hk_time, utc_time, tz_offset, day_start, get_duration
from main.validation import business_calendar_schema

logger = logging.getLogger('django')
channel_layer = get_channel_layer()
DB_NAME = settings.DATABASES['default']['NAME']
service_begin_hour = 9 - tz_offset
service_close_weekday_hour = 19 - tz_offset
service_clsoe_sat_hour = 12 - tz_offset


def dictfetchone(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, cursor.fetchone()))


def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def delete_student_user(student_netid: str):
    try:
        student_user = User.objects.get(netid=student_netid)
        student_user.delete()
    except User.DoesNotExist:
        logger.warning('student_user not exist.')


def write_chatbot_stat(data: List[ChatBotSession]) -> io.BytesIO:
    logger.info('Composing chatbot stat file...')
    output = io.BytesIO()
    wb = xlsxwriter.Workbook(output)
    ws = wb.add_worksheet('ChatBOT statistics')

    col_list = ChatBotSession.chatbot_stat_col_name_list
    for idx, col_name in enumerate(col_list):
        ws.write(0, idx, col_name)

    for row_idx, row in enumerate(data, 1):
        end_time = row.end_time.astimezone(hk_time).strftime('%H:%M') if row.end_time else ''
        ws.write(row_idx, 0, row.start_time.astimezone(hk_time).strftime('%d/%m/%Y'))
        ws.write(row_idx, 1, row.start_time.astimezone(hk_time).strftime('%H:%M'))
        ws.write(row_idx, 2, end_time)
        ws.write(row_idx, 3, 'Y' if row.is_ployu_student else 'N')
        ws.write(row_idx, 4, row.student_netid)
        ws.write(row_idx, 5, row.get_language_display())
        ws.write(row_idx, 6, 'Y' if row.q1_academic else 'N')
        ws.write(row_idx, 7, 'Y' if row.q1_interpersonal_relationship else 'N')
        ws.write(row_idx, 8, 'Y' if row.q1_career else 'N')
        ws.write(row_idx, 9, 'Y' if row.q1_family else 'N')
        ws.write(row_idx, 10, 'Y' if row.q1_mental_health else 'N')
        ws.write(row_idx, 11, 'Y' if row.q1_others else 'N')
        ws.write(row_idx, 12, 'Y' if row.q2 else 'N')
        ws.write(row_idx, 13, row.get_q3_display())
        ws.write(row_idx, 14, row.get_q4_display())
        ws.write(row_idx, 15, 'Y' if row.q5 else 'N')
        ws.write(row_idx, 16, 'Y' if row.q6_1 else 'N')
        ws.write(row_idx, 17, 'Y' if row.q6_2 else 'N')
        ws.write(row_idx, 18, row.score)
        ws.write(row_idx, 19, row.first_option)
        ws.write(row_idx, 20, row.feedback_rating)

    wb.close()
    output.seek(0)
    return output


def write_online_chat_stat(data: List[StudentChatHistory]) -> io.BytesIO:
    logger.info('Composing online chat stat file...')
    output = io.BytesIO()
    wb = xlsxwriter.Workbook(output)
    ws = wb.add_worksheet('Online Chat')

    col_list = StudentChatHistory.chat_hist_col_name_list
    for idx, col_name in enumerate(col_list):
        ws.write(0, idx, col_name)

    for row_idx, row in enumerate(data, 1):
        start_time = row.chat_start_time.astimezone(hk_time).strftime('%H:%M') if row.chat_start_time else ''
        end_time = row.chat_end_time.astimezone(hk_time).strftime('%H:%M') if row.chat_end_time else ''
        request_time = row.chat_request_time.astimezone(hk_time).strftime('%H:%M') if row.chat_request_time else ''
        chat_duration = None
        wait_duration = None
        if row.chat_request_time and row.chat_start_time:
            wait_duration = get_duration(row.chat_start_time - row.chat_request_time)
            chat_duration = get_duration(row.chat_end_time - row.chat_start_time)

        staff_netid = None
        if row.assigned_counsellor and row.assigned_counsellor.staff_netid:
            staff_netid = row.assigned_counsellor.staff_netid

        ws.write(row_idx, 0, row.student_netid)
        ws.write(row_idx, 1, row.chat_request_time.astimezone(hk_time).strftime('%d/%m/%Y'))
        ws.write(row_idx, 2, 'Y' if row.q1 else 'N')
        ws.write(row_idx, 3, 'Y' if row.q2 else 'N')
        ws.write(row_idx, 4, request_time)
        ws.write(row_idx, 5, wait_duration)
        ws.write(row_idx, 6, start_time)
        ws.write(row_idx, 7, end_time)
        ws.write(row_idx, 8, chat_duration)
        ws.write(row_idx, 9, staff_netid)
        ws.write(row_idx, 10, 'Y' if row.is_supervisor_join else 'N')
        ws.write(row_idx, 11, 'Y' if row.is_no_show else 'N')

    wb.close()
    output.seek(0)
    return output


def write_overall_stat(data, from_date, to_date) -> io.BytesIO:
    logger.info('Composing overall stat file...')
    output = io.BytesIO()
    wb = xlsxwriter.Workbook(output)
    ws = wb.add_worksheet('Statistics Overview')

    ws.write(0, 0, 'Date')
    ws.write(1, 0, f"{from_date.strftime('%Y/%m/%d')} - {to_date.strftime('%Y/%m/%d')}")

    col_name = ChatBotSession.statis_overview_col_name_map

    for col_idx, (key, val) in enumerate(col_name.items(), 1):
        ws.write(0, col_idx, key)
        ws.write(1, col_idx, data[val])

    wb.close()
    output.seek(0)
    return output


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, netid, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not netid:
            raise ValueError('The given netid must be set')
        user = self.model(netid=netid, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, netid, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(netid, **extra_fields)

    def create_superuser(self, netid, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(netid, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    netid = models.CharField(_('polyU Net ID'), max_length=30, unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    is_staff = models.BooleanField(
        _('app admin'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'netid'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'auth_user'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def get_groups(self) -> str:
        groups = self.groups.all()
        if groups:
            return groups[0].name
        else:
            raise UnauthorizedException(f'Staff({self.netid}) does not belong to any user group in this application.')


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
        ONLINE_TRIAGE = 'online_triage', _('Online Triage')
        DO = 'do', _('DO')
        COUNSELLOR = 'counsellor', _('Counsellor')
        SUPERVISOR = 'supervisor', _('Supervisor')
        ADMIN = 'admin', _('Administrator')

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
    status_change_time = models.DateTimeField(auto_now_add=True)
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
            original_assign_staff.save()  # noqa

        student.assigned_counsellor = self
        student.student_chat_status = StudentChatStatus.ChatStatus.ASSIGNED
        student.last_assign_time = now
        student.last_state_change = now
        self.staff_chat_status = StaffStatus.ChatStatus.ASSIGNED
        self.status_change_time = now
        student.save()
        self.save()

    def notify_assignment(self, student_netid):
        logger.info("notify staff")
        # async_to_sync(channel_layer.group_send)(
        #     f'staff_{cls.staff_netid}', {
        #         'type': 'send_assignment_alert',
        #         'content': {
        #             'type': 'assignment'
        #         }
        #     })

        # send email asynchronously
        template_data = {'student_netid': student_netid}  # noqa
        t = threading.Thread(target=email_service.send, args=('new_assignment', self.staff_netid, template_data))
        t.start()


class StudentChatStatus(models.Model):
    """
    Student's info will temporary store in this table when they use the online service.
    This info will move to the StudentChatHistory table when the student left this service.

    Attributes
        id:                         Primary key of this table
        student_netid:              Student's net ID, unique in this table
        student_chat_status:        Student's chat status
        chat_request_time:          The time that this student make the chat request
        q1:
        q2:
        personal_contact_number:    Contact number of the student
        emergency_contact_name:     Emergency contact of the student
        relationship:               The relationship between contact person and the student
        emergency_contact_number:   Contact number of the emergency contact person
        last_assign_time:           The time that assign a staff to this student
        chat_start_time:            The time that the chat start
        assigned_counsellor:        The counsellor assigned to this student
        is_supervisor_join:         Whether a supervisory joined or not
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
    chat_request_time = models.DateTimeField(default=timezone.localtime, null=True)
    q1 = models.BooleanField(null=True)
    q2 = models.BooleanField(null=True)
    personal_contact_number = models.CharField(max_length=32, null=True)
    emergency_contact_name = models.CharField(max_length=32, null=True)
    relationship = models.CharField(max_length=32, null=True)
    emergency_contact_number = models.CharField(max_length=32, null=True)
    last_assign_time = models.DateTimeField(default=None, null=True)
    chat_start_time = models.DateTimeField(default=None, null=True)
    last_state_change = models.DateTimeField(default=None, null=True)
    assigned_counsellor = models.OneToOneField(StaffStatus, null=True, on_delete=models.DO_NOTHING)
    is_supervisor_join = models.BooleanField(default=False)

    def __str__(self):
        return f"Student({self.student_netid})"

    def add_to_queue(self):
        self.student_chat_status = StudentChatStatus.ChatStatus.WAITING
        self.save()

    @classmethod
    def unassign_from(cls, staff: StaffStatus):
        student = cls.objects \
            .filter(student_chat_status=cls.ChatStatus.ASSIGNED,
                    assigned_counsellor=staff) \
            .first()
        if student:
            student.assigned_counsellor = None
            student.last_state_change = student.chat_request_time
            student.add_to_queue()
            logger.info(f'Unassigned {student}')


class StudentChatHistory(models.Model):
    """
    Attributes
        id:                         Primary key of this a chat record
        student_netid:              Student's net ID
        student_chat_status:        Student's chat status
        chat_request_time:          The time that this student make the chat request
        chat_start_time:            The time that the chat starts
        chat_end_time:              The time that the chat ends
        assigned_counsellor:        The counsellor assigned to this student
        is_supervisor_join:         Whether a supervisory joined or not
        is_no_show:                 Whether the student is no show
        personal_contact_number:    Contact number of the student
        emergency_contact_name:     Emergency contact of the student
        relationship:               The relationship between contact person and the student
        emergency_contact_number:   Contact number of the emergency contact person
    """

    class Meta:
        db_table = 'student-chat-history'

    id = models.AutoField(primary_key=True)
    student_netid = models.CharField(max_length=64)
    student_chat_status = models.CharField(max_length=32, choices=StudentChatStatus.ChatStatus.choices, null=True)
    chat_request_time = models.DateTimeField(null=True)
    chat_start_time = models.DateTimeField(default=None, null=True)
    chat_end_time = models.DateTimeField(default=None, null=True)
    assigned_counsellor = models.ForeignKey(StaffStatus, null=True, on_delete=models.DO_NOTHING)
    is_supervisor_join = models.BooleanField(default=False)
    is_no_show = models.BooleanField(null=True)
    q1 = models.BooleanField(null=True)
    q2 = models.BooleanField(null=True)
    personal_contact_number = models.CharField(max_length=32, null=True)
    emergency_contact_name = models.CharField(max_length=32, null=True)
    relationship = models.CharField(max_length=32, null=True)
    emergency_contact_number = models.CharField(max_length=32, null=True)

    chat_hist_col_name_list = [
        'Student ID',
        'Date',
        'Q1 (received counselling service)',
        'Q2 (mental health history)',
        'Request Time',
        'Waiting Duration',
        'Chat Start Time',
        'Chat End Time',
        'Chat Duration',
        'Counsellor',
        'Supervisor join',
        'No show'
    ]

    def __str__(self):
        return f"ChatHistory({self.student_netid})"

    @classmethod
    def append_end_chat(cls, student: StudentChatStatus, time: datetime, is_no_show: bool = None, endchat=False):
        cls(student_netid=student.student_netid,
            student_chat_status=StudentChatStatus.ChatStatus.END if endchat else student.student_chat_status,
            chat_request_time=student.chat_request_time,
            chat_start_time=student.chat_start_time,
            chat_end_time=time,
            assigned_counsellor=student.assigned_counsellor,
            is_supervisor_join=student.is_supervisor_join,
            is_no_show=is_no_show,
            q1=student.q1,
            q2=student.q2,
            personal_contact_number=student.personal_contact_number,
            emergency_contact_name=student.emergency_contact_name,
            relationship=student.relationship,
            emergency_contact_number=student.emergency_contact_number).save()

    @classmethod
    def statis_overview(cls, start: datetime, end: datetime) -> Dict:
        # Convert all time value to in utc
        start_time = start.astimezone(utc_time)
        end_time = end.astimezone(utc_time)

        query = f"""
            WITH
                selected_table AS  (
                SELECT
                    *
                FROM
                    `{DB_NAME}`.`{cls._meta.db_table}`
                WHERE
                    `{DB_NAME}`.`{cls._meta.db_table}`.`chat_request_time` BETWEEN '{start_time}' AND '{end_time}'
            )
            SELECT
             (SELECT count(*) FROM selected_table) AS online_chat_access_count,
             (SELECT count(*) FROM selected_table WHERE student_chat_status='{StudentChatStatus.ChatStatus.END}'
                AND is_no_show=FALSE) AS successful_chat_count
        """

        logger.info(query)
        with connection.cursor() as cursor:
            cursor.execute(query)
            res = dictfetchone(cursor)

        return res


class ChatBotSession(models.Model):
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
        db_table = 'chatbot-session'  # noqa

    class Language(models.TextChoices):
        en_us = 'en-us', _('English')
        zh_hk = 'zh-hk', _('繁體中文')
        zh_cn = 'zh-cn', _('简体中文')

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

    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student_netid = models.CharField(max_length=32, null=True)  # noqa
    start_time = models.DateTimeField(default=timezone.localtime)
    end_time = models.DateTimeField(null=True)
    is_ployu_student = models.BooleanField(default=False)  # noqa
    language = models.CharField(max_length=16, choices=Language.choices, null=True)
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

    chatbot_stat_col_name_list = [
        'Date',
        'Start Time',
        'End Time',
        'PolyU Student',
        'Student ID',
        'Language',
        'Q1 (academic)',
        'Q1 (Interpersonal Relationship)',
        'Q1 (Career)',
        'Q1 (Family)',
        'Q1 (Mental Health)',
        'Q1 (Others)',
        'Q2',
        'Q3',
        'Q4',
        'Q5',
        'Q6.1',
        'Q6.2',
        'Score',
        '1st option after recommendation',
        'Feedback rating'
    ]

    statis_overview_col_name_map = {
        'No. of access': 'total_access_count',
        'No. of office hour access': 'access_office_hr_count',
        'No. of non-office hour access': 'non_office_hr_access_count',
        'No. of PolyU student': 'polyu_student_count',  # noqa
        'No. of non-student': 'non_polyu_student_count',  # noqa
        'No. of green': 'score_green_count',
        'No. of yellow': 'score_yellow_count',
        'No. of red': 'score_red_count',
        'No. of access to POSS': 'poss_access_count',
        'No. of access to Mental Health 101': 'mh101_access_count',
        'No. of access to Online Chat Service': 'online_chat_access_count',
        'No. of successful chat with counsellor': 'successful_chat_count'
    }

    @classmethod
    def get_high_risk_student(cls):
        five_days_ago = timezone.localdate() - timedelta(days=5)
        return cls.objects.filter(score__gte=11, start_time__gte=day_start(five_days_ago)) \
            .order_by('-start_time') \
            .values('student_netid', 'start_time')

    @classmethod
    def usage_chatbot_connect(cls, student_netid: str = None,
                              is_ployu_student: bool = False) -> ChatBotSession:
        session = cls.objects.create(student_netid=student_netid,
                                     start_time=timezone.localtime(),
                                     is_ployu_student=is_ployu_student)

        return session

    @classmethod
    def statis_overview(cls, start: datetime, end: datetime) -> Dict:
        # Convert all time value to in utc
        start_time = start.astimezone(utc_time).replace(tzinfo=None)
        end_time = end.astimezone(utc_time).replace(tzinfo=None)

        query = f"""
            WITH
                session_table AS  (
                SELECT
                    *
                FROM
                    `{DB_NAME}`.`{cls._meta.db_table}`
                WHERE
                    `{DB_NAME}`.`{cls._meta.db_table}`.`start_time` BETWEEN '{start_time}' AND '{end_time}'
            )
            SELECT
             (SELECT count(*) FROM session_table) AS total_access_count,
             (SELECT count(*) FROM session_table
                WHERE (HOUR(start_time) >= {service_begin_hour} AND HOUR(start_time) <= {service_close_weekday_hour} AND weekday(start_time) IN (0, 1, 2, 3, 4))
                OR (HOUR(start_time) >= {service_begin_hour} AND HOUR(start_time) <= {service_clsoe_sat_hour} AND weekday(start_time)=5)) AS access_office_hr_count,
             (select total_access_count - access_office_hr_count) AS non_office_hr_access_count, 
             (SELECT count(*) FROM session_table WHERE is_ployu_student=TRUE ) AS polyu_student_count,
             (SELECT count(*) FROM session_table WHERE is_ployu_student=FALSE ) AS non_polyu_student_count,
             (SELECT count(*) FROM session_table WHERE score<=6 ) AS score_green_count,
             (SELECT count(*) FROM session_table WHERE score>=7 AND score<=10 ) AS score_yellow_count,
             (SELECT count(*) FROM session_table WHERE score>=11 AND score<=13 ) AS score_red_count,
             (SELECT count(*) FROM session_table WHERE first_option='{cls.RecommendOptions.opt1}' ) AS mh101_access_count,
             (SELECT count(*) FROM session_table WHERE first_option='{cls.RecommendOptions.opt2}' ) AS poss_access_count
            """

        logger.info(query)
        with connection.cursor() as cursor:
            cursor.execute(query)
            res = dictfetchone(cursor)

        return res

    @classmethod
    def get_red_route(cls, start_dt: datetime, end_dt: datetime) -> List[Dict]:
        query = f"""
            SELECT
                `{cls._meta.db_table}`.`student_netid`,
                DATE_ADD(`{cls._meta.db_table}`.`start_time`, INTERVAL 8 HOUR) AS `datetime`, #  full datetime, used to sort the results
                CAST(DATE_ADD(`{cls._meta.db_table}`.`start_time`, INTERVAL 8 HOUR) AS DATE) AS `date`,
                CAST(DATE_ADD(`{cls._meta.db_table}`.`start_time`, INTERVAL 8 HOUR) AS TIME) AS `start_time`,
                CAST(DATE_ADD(`{cls._meta.db_table}`.`end_time`, INTERVAL 8 HOUR) AS TIME) AS `end_time`
            FROM
                `{DB_NAME}`.`{cls._meta.db_table}`
            WHERE
                `{cls._meta.db_table}`.`start_time` > '{start_dt.astimezone(utc_time).replace(tzinfo=None)}'
                AND `{cls._meta.db_table}`.`start_time` < '{end_dt.astimezone(utc_time).replace(tzinfo=None)}'
                AND `{cls._meta.db_table}`.`score` >= 11
            ORDER BY `{cls._meta.db_table}`.`start_time` ASC
        """

        logger.info(query)
        with connection.cursor() as cursor:
            cursor.execute(query)
            res = dictfetchall(cursor)
        return res

    @classmethod
    def from_red_route_to_excel(cls, data: Dict) -> io.BytesIO:
        output = io.BytesIO()
        wb = xlsxwriter.Workbook(output)
        ws = wb.add_worksheet('Red Route')

        # Sheet header, first row
        columns = ['Student ID', 'Date', 'Start Time', 'End Time']
        for col_num in range(len(columns)):
            ws.write(0, col_num, columns[col_num])

        for row_num, row in enumerate(data, 1):
            ws.write(row_num, 0, row['student_netid'])  # noqa
            ws.write(row_num, 1, row['date'].strftime("%Y/%m/%d"))
            ws.write(row_num, 2, row['start_time'].strftime('%H:%M'))
            end_time = row.get('end_time')
            if end_time:
                ws.write(row_num, 3, end_time.strftime('%H:%M'))
            else:
                ws.write(row_num, 3, None)

        wb.close()
        output.seek(0)

        return output


class BusinessCalendar(models.Model):
    class Meta:
        db_table = 'business-calendar'

    date = models.CharField(primary_key=True, unique=True, max_length=10)
    is_working_day = models.BooleanField()
    office_hr_begin = models.CharField(null=True, max_length=16)
    office_hr_end = models.CharField(null=True, max_length=16)
    chatting_office_hr_begin = models.CharField(null=True, max_length=16)
    chatting_office_hr_end = models.CharField(null=True, max_length=16)

    field_names = [
        'date',
        'day',
        'office_hr_begin',
        'office_hr_end',
        'chatting_office_hr_begin',
        'chatting_office_hr_end'
    ]

    date_format_in_csv = '%d/%m/%Y'
    date_format_in_db = '%Y-%m-%d'
    time_format_in_db = '%H:%M:%S'
    lunch_break = ('12:00:00', '14:00:00')

    def __str__(self):
        return f"{self.__class__.__name__}(date={self.date}, is_working_day={self.is_working_day}, " \
               f"office_hr_end={self.office_hr_end}, chatting_office_hr_end={self.chatting_office_hr_end})"

    @classmethod
    def update_items_from_csv(cls, calendar_dates: List[Dict[str, str]]):
        """No null value, can be empty string
        """
        logger.info("Validating and putting into DB.")
        for row_idx, row in enumerate(calendar_dates, 1):  # 1 here refers to row in csv file
            try:
                cleaned_date = business_calendar_schema.load(row)
                cls(**cleaned_date).save()
            # cls.objects.update_or_create(**cleaned_date)  # noqa
            except ValidationError as e:
                logger.error(f"{e}")
                logger.error(f"Format invalid in row {row_idx}\n{row}")

    @classmethod
    def get_date(cls, date_: str):
        try:
            calendar_date = cls.objects.get(date=date_)  # noqa
            logger.info(calendar_date)
        except BusinessCalendar.DoesNotExist as e:  # noqa
            logger.warning(e)
            raise NotFound(f'date: {date_} not found.')
        return calendar_date

    @classmethod
    def is_working_hour(cls) -> bool:
        today = timezone.localdate()
        calendar_date = cls.get_date(today)

        if calendar_date.office_hr_begin and calendar_date.office_hr_end:
            time_now_str = timezone.localtime().strftime(cls.time_format_in_db)
            if calendar_date.office_hr_begin <= time_now_str <= calendar_date.office_hr_end:
                return True
        return False

    @classmethod
    def is_lunch_time(cls, time_now: str) -> bool:
        return cls.lunch_break[0] <= time_now <= cls.lunch_break[1]

    @classmethod
    def is_chatting_working_hour(cls):
        today = timezone.localdate()
        calendar_date = cls.get_date(today)

        if calendar_date.chatting_office_hr_begin and calendar_date.chatting_office_hr_end:
            time_now_str = timezone.localtime().strftime(cls.time_format_in_db)
            if calendar_date.chatting_office_hr_begin <= time_now_str <= calendar_date.chatting_office_hr_end and \
                    not cls.is_lunch_time(time_now_str):
                return True
        return False

    @classmethod
    def get_prev_working_day(cls) -> datetime:
        today = timezone.localdate().strftime(cls.date_format_in_db)
        prev_working_day = cls.objects \
            .filter(is_working_day=True, date__lt=today) \
            .order_by('-date') \
            .first()

        if prev_working_day:
            prev_working_day = prev_working_day.strptime(cls.date_format_in_db)
        else:
            prev_working_day = timezone.localdate() - timedelta(days=1)

        return prev_working_day


ROLE_RANKING = [StaffStatus.Role.ONLINE_TRIAGE,
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
