from datetime import timedelta
from django.utils import timezone
from django.db.models import Q
from celery import shared_task
from celery.utils.log import get_task_logger

from main.models import StaffStatus, StudentChatStatus, STAFF_ORDER

logger = get_task_logger(__name__)


@shared_task
def dequeue_student():
    """
    Check if any available staff. If yes, assign the staff to a student in the waiting queue

    :return:
    """
    now = timezone.now()

    students = StudentChatStatus.objects \
        .filter(student_chat_status=StudentChatStatus.ChatStatus.WAITING,
                chat_request_time__lt=now - timedelta(minutes=5)) \
        .order_by('chat_request_time') \
        .values_list('id', flat=True)

    for student in students:
        for role in STAFF_ORDER:
            staff = StaffStatus.get_random_staff_by_role(role)
            if staff:
                staff.assign_to(student)


@shared_task
def reassign_counsellor():
    """
     Re-assign counsellor if the student has waited to long

    :return:
    """
    now = timezone.now()
    staff_order = STAFF_ORDER + [None]

    students = StudentChatStatus.objects \
        .filter(student_chat_status=StudentChatStatus.ChatStatus.ASSIGNED,
                chat_request_time__lt=now - timedelta(minutes=5)) \
        .order_by('chat_request_time') \
        .all()

    for student in students:
        assigned_staff = student.assigned_counsellor
        role = assigned_staff.staff_role
        escalated_role = staff_order[staff_order.index(role) + 1]
        if escalated_role:
            staff = StaffStatus.get_random_staff_by_role(escalated_role)
            if staff:
                staff.assign_to(student)
