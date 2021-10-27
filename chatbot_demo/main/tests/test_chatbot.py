import random
from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase, Client
from django.urls import reverse

from main.models import User, ChatBotSession, StudentChatStatus, StudentChatHistory
from main.utils import *


class ChatbotTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        student_netid = '12345678A'
        self.student = User.objects.create_user(netid=student_netid, is_active=True)
        self.staff = User.objects.create_user(netid='staff_01', is_active=True)
        self.client.login(netid=student_netid)

    def _get_session_id(self, ) -> uuid.UUID:
        # create a login session and retrieve the
        chatbot_session = ChatBotSession.usage_chatbot_connect(
            student_netid='12345678A',
            is_ployu_student=True
        )
        return chatbot_session.session_id

    def test_create_chatbot_session(self):
        session = self.client.session

        chatbot_session = ChatBotSession.usage_chatbot_connect(
            student_netid='12345678A',
            is_ployu_student=True
        )
        session['session_id'] = chatbot_session.session_id

        retrieved_session = ChatBotSession.objects.get(session_id=session['session_id'])

        self.assertEqual(chatbot_session.session_id, retrieved_session.session_id)

    def test_submit_survey(self):
        session = self.client.session
        session['session_id'] = uuid2str(self._get_session_id())
        session.save()

        response = self.client.post(reverse('submitsurvey'),
                                    {
                                        'language': ChatBotSession.Language.en_us,
                                        'q1_academic': 'true',
                                        'q1_interpersonal_relationship': 'true',
                                        'q1_career': 'true',
                                        'q1_family': 'true',
                                        'q1_mental_health': 'true',
                                        'q1_others': 'true',
                                        'q2': 'true',
                                        'q3': ChatBotSession.FrequencyScale.often,
                                        'q4': ChatBotSession.FrequencyScale.often,
                                        'q5': 'false',
                                        'q6_1': 'false',
                                        'q6_2': 'null',
                                        'score': 12,
                                    })

        self.assertEqual(response.status_code, 200)

        self.assertTrue(ChatBotSession.objects.get(session_id=str2uuid(session['session_id'])))
        with self.assertRaises(ChatBotSession.DoesNotExist):
            ChatBotSession.objects.get(session_id=uuid.uuid4())

    def test_end_chatbot(self):
        session = self.client.session
        session['session_id'] = uuid2str(self._get_session_id())
        session.save()

        response = self.client.post(reverse('endchatbot'),
                                    {
                                        'first_option': ChatBotSession.RecommendOptions.opt1,
                                        'feedback_rating': 3
                                    })

        self.assertEqual(response.status_code, 200)

        session = self.client.session
        session['session_id'] = '60b67b7a-498a-4ad3-86c2-7dc7f947f20d'
        session.save()

        response = self.client.post(reverse('endchatbot'),
                                    {
                                        'first_option': ChatBotSession.RecommendOptions.opt3,
                                        'feedback_rating': 3
                                    })

        self.assertEqual(response.status_code, 404)


class StatisticTestCase(TestCase):
    def setUp(self):
        print(f'Setting up {self.__class__.__name__}...')
        self.days = [1, 2, 3, 4, 5, 6, 7]
        self.hours = [0, 4, 7, 10, 11, 13, 15, 17, 20, 23]
        # Will generate 70 chatbot sessions
        dt = datetime(2021, 8, 1, 0, 0, 0).astimezone(hk_time)

        bool_val = random.choices([True, False], k=len(self.days) * len(self.hours))
        no_true = sum(bool_val)

        i = 0
        for d in self.days:
            for h in self.hours:
                start_time = dt.replace(day=d, hour=h, minute=10)
                end_time = start_time + timedelta(minutes=15)
                ChatBotSession.objects.create(
                    student_netid=f"123456{i:02d}A",
                    start_time=start_time,
                    end_time=end_time,
                    is_ployu_student=i % 2,
                    language=random.choices(ChatBotSession.Language.values)[0],
                    q1_academic=bool_val[i],
                    q1_interpersonal_relationship=bool_val[i],
                    q1_career=bool_val[i],
                    q1_family=bool_val[i],
                    q1_mental_health=bool_val[i],
                    q1_others=bool_val[i],
                    q2=bool_val[i],
                    q3=random.choices(ChatBotSession.FrequencyScale.values)[0],
                    q4=random.choices(ChatBotSession.FrequencyScale.values)[0],
                    q5=bool_val[i],
                    q6_1=bool_val[i],
                    q6_2=bool_val[i],
                    score=i % 14,
                    first_option=ChatBotSession.RecommendOptions.values[i % 6],
                    feedback_rating=i % 5 + 1,
                )

                i += 1
                if 9 <= start_time.hour <= 19 and start_time.weekday() < 5:
                    StudentChatHistory.objects.create(
                        student_netid=f"123456{i:02d}A",
                        student_chat_status=StudentChatStatus.ChatStatus.values[i % 4],
                        chat_request_time=start_time,
                        is_no_show=i % 2,
                    )

        print(f"Generated {i} sessions.")

        #### Export Data
        # from django.core.serializers.json import DjangoJSONEncoder
        # import json
        # from django.core import serializers
        # qs = ChatBotSession.objects.all()
        # data = serializers.serialize('python', qs)
        # with open('session_data.json', 'w') as f:
        #     json.dump(data, f, cls=DjangoJSONEncoder)
        #
        # qs = StudentChatHistory.objects.all()
        # data = serializers.serialize('python', qs)
        # with open('history_data.json', 'w') as f:
        #     json.dump(data, f, cls=DjangoJSONEncoder)

    @patch('main.models.DB_NAME', f"test_{settings.DATABASES['default']['NAME']}")
    def test_statis_overview(self):
        start_date = timezone.localtime().replace(day=self.days[0], hour=0, minute=0, second=0)
        end_date = timezone.localtime().replace(day=self.days[-1], hour=23, minute=59, second=59)
        res = dict()
        res.update(ChatBotSession.statis_overview(start_date, end_date))
        res.update(StudentChatHistory.statis_overview(start_date, end_date))

        print('Overview:')
        print(res)
        self.assertEqual(res['total_access_count'], 70)
        self.assertEqual(res['access_office_hr_count'], 27)
        self.assertEqual(res['polyu_student_count'], 70 / 2)
        self.assertEqual(res['non_polyu_student_count'], 70 / 2)
        self.assertListEqual(list(res.keys()), [
            'total_access_count',
            'access_office_hr_count',
            'polyu_student_count',
            'non_polyu_student_count',
            'score_green_count',
            'score_yellow_count',
            'score_red_count',
            'mh101_access_count',
            'poss_access_count',
            'online_chat_access_count',
            'successful_chat_count'
        ])
        self.assertEqual(res['score_green_count'] + res['score_yellow_count'] + res['score_red_count'],
                         70)

    @patch('main.models.DB_NAME', f"test_{settings.DATABASES['default']['NAME']}")
    def test_get_red_route(self):
        # 1 Aug is Sun and 7 Aug is Sat
        start_date = date(2021, 8, 4)
        start_dt = datetime.combine(start_date, datetime.min.time())
        res = ChatBotSession.get_red_route(start_dt)
        self.assertEqual(len(res), 40)
        self.assertListEqual(list(res[0].keys()), [
            'student_netid',
            'datetime',
            'date',
            'start_time',
            'end_time'
        ])
