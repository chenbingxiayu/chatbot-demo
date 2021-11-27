import random
from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from main.models import StudentChatStatus, StaffStatus, ROLE_RANKING
from tasks.tasks import reassign_counsellor, WAIT_LIMIT, dequeue_student, assign_staff


class ScheduledTaskTestCase(TestCase):

    def setUp(self):

        over_waiting_limit = WAIT_LIMIT + 1

        # generate 15 staff and 3 assigned student
        # 15 staff with all combination of counsellor role and status
        i = 0
        for role in ROLE_RANKING:
            for status in StaffStatus.ChatStatus:
                staff = StaffStatus.objects.create(
                    staff_netid=f"staff_id{i:02}",
                    staff_role=role,
                    staff_chat_status=status,
                    status_change_time=timezone.localtime(),
                )

                if status == StaffStatus.ChatStatus.ASSIGNED:
                    StudentChatStatus.objects.create(
                        student_netid=f"100000{i:02}A",
                        student_chat_status=StudentChatStatus.ChatStatus.ASSIGNED,
                        chat_request_time=timezone.localtime() - timedelta(minutes=10),
                        last_assign_time=timezone.localtime() - timedelta(minutes=over_waiting_limit,
                                                                          seconds=random.randint(0, 10)),
                        assigned_counsellor=staff
                    )

                i += 1

        # generate 5 more unassigned students
        for j in range(i, i + 5):
            StudentChatStatus.objects.create(
                student_netid=f"100000{j:02}A",
                student_chat_status=StudentChatStatus.ChatStatus.WAITING,
                chat_request_time=timezone.localtime() - timedelta(minutes=10)
            )

        self.assertEqual(len(StaffStatus.objects.all()), 15)
        self.assertEqual(len(StaffStatus.objects
                             .filter(staff_chat_status=StaffStatus.ChatStatus.AVAILABLE)
                             .all()), 3)
        self.assertEqual(len(StaffStatus.objects
                             .filter(staff_chat_status=StaffStatus.ChatStatus.ASSIGNED)
                             .all()), 3)

        self.assertEqual(len(StudentChatStatus.objects.all()), 3 + 5)
        self.assertEqual(len(StudentChatStatus.objects
                             .filter(assigned_counsellor__isnull=True)
                             .all()), 5)

    @patch('main.models.StaffStatus.notify_assignment')
    def test_reassign_counsellor(self, mock_notify_assignment):
        reassign_counsellor()

        # staff
        self.assertEqual(len(StaffStatus.objects
                             .filter(staff_chat_status=StaffStatus.ChatStatus.ASSIGNED)
                             .all()), 3)
        self.assertEqual(len(StaffStatus.objects
                             .filter(staff_chat_status=StaffStatus.ChatStatus.AVAILABLE,
                                     staff_role=StaffStatus.Role.ONLINE_TRIAGE)
                             .all()), 2)
        self.assertEqual(len(StaffStatus.objects
                             .filter(staff_chat_status=StaffStatus.ChatStatus.AVAILABLE,
                                     staff_role=StaffStatus.Role.DO)
                             .all()), 1)
        self.assertEqual(len(StaffStatus.objects
                             .filter(staff_chat_status=StaffStatus.ChatStatus.AVAILABLE,
                                     staff_role=StaffStatus.Role.COUNSELLOR)
                             .all()), 0)
        # students
        self.assertEqual(len(StudentChatStatus.objects
                             .filter(student_chat_status=StudentChatStatus.ChatStatus.ASSIGNED)
                             .all()), 3)

    @patch('main.models.StaffStatus.notify_assignment')
    def test_assign_staff(self, mock_notify_assignment):

        students = StudentChatStatus.objects \
            .filter(student_chat_status=StudentChatStatus.ChatStatus.WAITING) \
            .all()

        results = [assign_staff(student) for student in students]

        self.assertListEqual(results, [True, True, True, False, False])

    @patch('main.models.StaffStatus.notify_assignment')
    def test_dequeue_student(self, mock_notify_assignment):
        dequeue_student()

        # staff
        self.assertEqual(len(StaffStatus.objects
                             .filter(staff_chat_status=StaffStatus.ChatStatus.ASSIGNED)
                             .all()), 6)
        self.assertEqual(len(StaffStatus.objects
                             .filter(staff_chat_status=StaffStatus.ChatStatus.ASSIGNED,
                                     staff_role=StaffStatus.Role.ONLINE_TRIAGE)
                             .all()), 2)
        self.assertEqual(len(StaffStatus.objects
                             .filter(staff_chat_status=StaffStatus.ChatStatus.ASSIGNED,
                                     staff_role=StaffStatus.Role.DO)
                             .all()), 2)
        self.assertEqual(len(StaffStatus.objects
                             .filter(staff_chat_status=StaffStatus.ChatStatus.ASSIGNED,
                                     staff_role=StaffStatus.Role.COUNSELLOR)
                             .all()), 2)

        # students
        self.assertEqual(len(StudentChatStatus.objects
                             .filter(student_chat_status=StudentChatStatus.ChatStatus.ASSIGNED)
                             .all()), 6)

    def tearDown(self):
        StudentChatStatus.objects.all().delete()
        StaffStatus.objects.all().delete()
