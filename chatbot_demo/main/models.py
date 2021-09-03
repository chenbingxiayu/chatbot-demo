# -*- coding: utf-8 -*-
from __future__ import unicode_literals, annotations
import io
import logging
import uuid
from datetime import datetime, date, time, timedelta
from typing import Dict, List

import pendulum
import xlsxwriter
from django.db import models, connection, transaction
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from main.email_service import email_service
from main.exceptions import UnauthorizedException
from main.utils import hk_time, utc_time, tz_offset, day_start

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
        ONLINETRIAGE = 'online_triage', _('Online Triage')
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
        # async_to_sync(channel_layer.group_send)(
        #     f'staff_{self.staff_netid}', {
        #         'type': 'send_assignment_alert',
        #         'content': {
        #             'type': 'assignment'
        #         }
        #     })

        email_service.send('new_assignment', self.staff_netid)


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
            student.add_to_queue()
            logger.info(f'Unassigned {student}')

    def usage_online_chatting_connect(self):
        pass


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
        db_table = 'chatbot-session'

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
    student_netid = models.CharField(max_length=32, null=True)
    start_time = models.DateTimeField(default=timezone.localtime)
    end_time = models.DateTimeField(null=True)
    is_ployu_student = models.BooleanField(default=False)
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

    @classmethod
    def get_high_risk_student(cls):
        five_days_ago = timezone.localdate() - timedelta(days=5)
        return cls.objects.filter(score__gte=11, start_time__gte=day_start(five_days_ago)) \
            .values('student_netid', 'start_time', 'end_time')

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
    def get_red_route(cls, start_dt: datetime) -> Dict:
        query = f"""
            SELECT
                `{cls._meta.db_table}`.`student_netid`,
                `{cls._meta.db_table}`.`start_time` AS `datetime`, #  full datetime, used to sort the results
                CAST(`{cls._meta.db_table}`.`start_time` AS DATE) AS `date`,
                CAST(`{cls._meta.db_table}`.`start_time` AS TIME) AS `start_time`,
                CAST(`{cls._meta.db_table}`.`end_time` AS TIME) AS `end_time`
            FROM
                `{DB_NAME}`.`{cls._meta.db_table}`
            WHERE
                `{cls._meta.db_table}`.`start_time` > '{start_dt.astimezone(utc_time).replace(tzinfo=None)}'
            ORDER BY `{cls._meta.db_table}`.`start_time` ASC
        """

        logger.info(query)
        with connection.cursor() as cursor:
            cursor.execute(query)
            res = dictfetchall(cursor)
        return res

    @classmethod
    def get_red_route_to_excel(cls, start_dt: datetime) -> io.BytesIO:
        data = cls.get_red_route(start_dt)

        output = io.BytesIO()
        wb = xlsxwriter.Workbook(output)
        ws = wb.add_worksheet('Red Route')

        # Sheet header, first row
        columns = ['Student ID', 'Date', 'Start Time', 'End Time']
        for col_num in range(len(columns)):
            ws.write(0, col_num, columns[col_num])

        for row_num, row in enumerate(data, 1):
            ws.write(row_num, 0, row['student_netid'])
            ws.write(row_num, 1, row['date'].strftime("%Y/%m/%d"))
            ws.write(row_num, 2, row['start_time'].strftime('%H:%M'))
            ws.write(row_num, 3, row['end_time'].strftime('%H:%M'))

        wb.close()
        output.seek(0)

        return output


class BusinessCalendar(models.Model):
    class Meta:
        db_table = 'business-calendar'

    date = models.CharField(primary_key=True, max_length=10)
    is_working_day = models.BooleanField()
    office_hr_end = models.CharField(null=True, max_length=5)

    office_hr_begin = '09:00'

    @classmethod
    def update_items(cls, calendar_dates: List[List[str]]):
        """
        calendar_dates: .e.g [['Y-m-d', 'H:M'], ['Y-m-d', '']]
        """
        with transaction.atomic():
            for date_, office_hr_end in calendar_dates:
                business_date = cls(date=date_,
                                    is_working_day=office_hr_end != '',
                                    office_hr_end=office_hr_end)
                business_date.save()

    @classmethod
    def is_working_day_(cls, date_: str):
        try:
            calendar_date = cls.objects.get(date=date_)
        except BusinessCalendar.DoesNotExist as e:
            logger.warning(e)
            raise ValueError(f'date: {date_} not found.')

        return calendar_date.is_working_day

    @classmethod
    def get_prev_working_day(cls) -> datetime:

        today = timezone.localdate().strftime('%Y-%m-%d')
        prev_working_day = cls.objects \
            .filter(is_working_day=True, date__lt=today) \
            .order_by('-date') \
            .first()

        if prev_working_day:
            prev_working_day = prev_working_day.strptime('%Y-%m-%d')
        else:
            prev_working_day = timezone.localdate() - timedelta(days=1)

        return prev_working_day


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
