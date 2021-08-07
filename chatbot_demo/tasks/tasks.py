from datetime import timedelta

from django.utils import timezone
from django.db import transaction
from django.db.transaction import TransactionManagementError
from celery import shared_task
from celery.utils.log import get_task_logger

from main.models import StaffStatus, StudentChatStatus, ROLE_RANKING
from main.signals import update_queue

logger = get_task_logger(__name__)
WAIT_LIMIT = 5  # in minutes


def reassign_counsellor():
    """
     Re-assign counsellor if the student has waited to long

    :return:
    """
    now = timezone.now()
    role_ranking = ROLE_RANKING + [None]

    students = StudentChatStatus.objects \
        .filter(student_chat_status=StudentChatStatus.ChatStatus.ASSIGNED,
                last_assign_time__lt=now - timedelta(minutes=WAIT_LIMIT)) \
        .order_by('chat_request_time') \
        .all()

    for student in students:
        with transaction.atomic():
            try:
                assigned_staff = student.assigned_counsellor
                role = assigned_staff.staff_role
                escalated_role = role_ranking[role_ranking.index(role) + 1] if role in role_ranking else None
                if escalated_role:
                    staff = StaffStatus.get_random_staff_by_role(escalated_role)
                    if staff:
                        staff.assign_to(student)
                        logger.info(f"{staff} assigned to {student}")
                        staff.notify_assignment()
            except TransactionManagementError as e:
                logger.warning(e)


def assign_staff(student: StudentChatStatus) -> bool:
    """
    Check if any available staff.
    If yes, assign the staff to a new coming student or the students in the waiting queue.

    :param student:
    :return: whether the student is assigned to a staff
    """
    for role in ROLE_RANKING:
        with transaction.atomic():
            try:
                staff = StaffStatus.get_random_staff_by_role(role)
                if staff:
                    staff.assign_to(student)
                    logger.info(f"{staff} assigned to {student}")
                    staff.notify_assignment()
                    return True
            except TransactionManagementError as e:
                logger.warning(e)

    return False


def dequeue_student():
    """
    Get the long-awaited student in the waiting queue and assign them to available staff.

    :return:
    """

    now = timezone.now()
    students = StudentChatStatus.objects \
        .filter(student_chat_status=StudentChatStatus.ChatStatus.WAITING,
                chat_request_time__lt=now - timedelta(minutes=WAIT_LIMIT)) \
        .order_by('chat_request_time') \
        .all()

    for student in students:
        if not assign_staff(student):
            # there is no available staff, we can stop looping
            break


@shared_task
def assignment_tasks():
    reassign_counsellor()
    dequeue_student()
    update_queue.send(sender=None)
