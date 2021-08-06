from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.utils import timezone

from main.models import StaffStatus, StudentChatStatus, User
from main.views import updatestaff, logout_view


class ScheduledTaskTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user_list = []

        for i, status in enumerate(StaffStatus.ChatStatus):
            staff_netid = f"staff_id{i:02}"

            user = User.objects.create(netid=staff_netid)
            staff = StaffStatus.objects.create(
                staff_netid=staff_netid,
                staff_role=StaffStatus.Role.COUNSELLOR,
                staff_chat_status=status,
                status_change_time=timezone.localtime(),
            )
            self.user_list.append(user)

            if staff.staff_chat_status == StaffStatus.ChatStatus.ASSIGNED:
                StudentChatStatus.objects.create(
                    student_netid=f"100000{i:02}A",
                    student_chat_status=StudentChatStatus.ChatStatus.ASSIGNED,
                    chat_request_time=timezone.localtime() - timedelta(minutes=10),
                    last_assign_time=timezone.localtime(),
                    assigned_counsellor=staff
                )

        self.assertEqual(len(StudentChatStatus.objects
                             .filter(student_chat_status=StaffStatus.ChatStatus.ASSIGNED)
                             .all()), 1)
        self.assertEqual(len(StudentChatStatus.objects
                             .filter(assigned_counsellor__isnull=False)
                             .all()), 1)

    def test_updatestaff(self):

        for user in self.user_list:
            request = self.factory.post(reverse('updatestaff'),
                                        data={
                                            "status": StaffStatus.ChatStatus.AVAILABLE
                                        })

            request.user = user
            updatestaff(request)
        self.assertEqual(len(StudentChatStatus.objects
                             .filter(student_chat_status=StudentChatStatus.ChatStatus.ASSIGNED)
                             .all()), 1)
        self.assertEqual(len(StudentChatStatus.objects
                             .filter(assigned_counsellor__isnull=False)
                             .all()), 1)
        self.assertEqual(len(StaffStatus.objects
                             .filter(staff_chat_status=StaffStatus.ChatStatus.ASSIGNED)
                             .all()), 0)

        self.tearDown()
        self.setUp()

        for user in self.user_list:
            request = self.factory.post(reverse('updatestaff'),
                                        data={
                                            "status": StaffStatus.ChatStatus.AWAY
                                        })
            request.user = user
            updatestaff(request)

        self.assertEqual(len(StudentChatStatus.objects
                             .filter(student_chat_status=StudentChatStatus.ChatStatus.ASSIGNED)
                             .all()), 0)
        self.assertEqual(len(StudentChatStatus.objects
                             .filter(assigned_counsellor__isnull=False)
                             .all()), 0)
        self.assertEqual(len(StaffStatus.objects
                             .filter(staff_chat_status=StaffStatus.ChatStatus.ASSIGNED)
                             .all()), 0)

    @patch('main.views.logout')
    def test_logout(self, mock_logout):

        for user in self.user_list:
            request = self.factory.get(reverse('logout_view'),
                                       data={
                                           "status": StaffStatus.ChatStatus.AWAY
                                       })
            request.user = user
            logout_view(request)

        self.assertEqual(len(StudentChatStatus.objects
                             .filter(student_chat_status=StudentChatStatus.ChatStatus.ASSIGNED)
                             .all()), 0)
        self.assertEqual(len(StudentChatStatus.objects
                             .filter(assigned_counsellor__isnull=False)
                             .all()), 0)

    def tearDown(self):
        User.objects.all().delete()
        StudentChatStatus.objects.all().delete()
        StaffStatus.objects.all().delete()
