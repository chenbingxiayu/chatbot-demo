from datetime import timedelta

from celery import shared_task
from celery.utils.log import get_task_logger
from django.db import transaction
from django.db.transaction import TransactionManagementError
from django.utils import timezone

from main.models import StaffStatus, StudentChatStatus, ROLE_RANKING, StudentChatHistory, User
from main.signals import update_queue

logger = get_task_logger(__name__)
WAIT_LIMIT = 3  # in minutes


def reassign_counsellor():
    """Re-assign counsellor if the student has waited too long

    :return:
    """
    logger.info("Run re-assignment task")
    now = timezone.localtime()

    students = StudentChatStatus.objects \
        .filter(student_chat_status=StudentChatStatus.ChatStatus.ASSIGNED,
                last_assign_time__lt=now - timedelta(minutes=WAIT_LIMIT)) \
        .order_by('chat_request_time') \
        .all()

    successful_count = 0
    for student in students:
        success = False
        with transaction.atomic():
            try:
                assigned_staff = student.assigned_counsellor
                role = assigned_staff.staff_role
                if role in ROLE_RANKING:
                    next_role_idx = (ROLE_RANKING.index(role) + 1) % len(ROLE_RANKING)
                    escalated_role = ROLE_RANKING[next_role_idx]
                # for abnormal cases
                else:
                    escalated_role = StaffStatus.Role.ONLINE_TRIAGE

                staff = StaffStatus.get_random_staff_by_role(escalated_role)
                if staff:
                    staff.assign_to(student)
                    logger.info(f"{staff} assigned to {student}")
                    success = True
                    successful_count += 1
            except TransactionManagementError as e:
                logger.warning(e)

        # Send email outside the transaction
        if success:
            staff.notify_assignment(student.student_netid)

    logger.info(f"{successful_count}/{len(students)} students were re-assigned.")


def assign_staff(student: StudentChatStatus) -> bool:
    """Check if any available staff.
    If yes, assign the staff to a new coming student or the students in the waiting queue.

    :param student:
    :return: whether the student is assigned to a staff
    """
    success = False
    for role in ROLE_RANKING:
        with transaction.atomic():
            try:
                staff = StaffStatus.get_random_staff_by_role(role)
                if staff:
                    staff.assign_to(student)
                    logger.info(f"{staff} assigned to {student}")
                    success = True

            except TransactionManagementError as e:
                logger.warning(e)

        if success:
            staff.notify_assignment(student.student_netid)
            return True

    return False


def dequeue_student():
    """Get the long-awaited student in the waiting queue and assign them to available staff.

    :return:
    """
    logger.info("Run dequeue task")
    students = StudentChatStatus.objects \
        .filter(student_chat_status=StudentChatStatus.ChatStatus.WAITING) \
        .order_by('chat_request_time') \
        .all()

    successful_count = 0
    for student in students:
        if not assign_staff(student):
            # there is no available staff, we can stop looping
            break

        successful_count += 1

    logger.info(f"{successful_count}/{len(students)} students have been assigned.")


@shared_task
def assignment_tasks():
    reassign_counsellor()
    dequeue_student()
    update_queue.send(sender=None)


@shared_task
def end_all_chat_task():
    logger.info("Clear up all chats.")
    now = timezone.localtime()

    logger.info("Deleting all students..")
    students = StudentChatStatus.objects.all()
    for student in students:
        student_user = None
        try:
            student_user = User.objects.get(netid=student.student_netid)
        except User.DoesNotExist as e:
            logger.warning(e)

        is_end_chat = (student.student_chat_status == StudentChatStatus.ChatStatus.CHATTING)
        is_no_show = False if student.student_chat_status == StudentChatStatus.ChatStatus.CHATTING else None
        StudentChatHistory.append_end_chat(student, now, is_no_show, endchat=is_end_chat)
        student.delete()
        if student_user:
            student_user.delete()
    logger.info("Complete deleting all students.")

    logger.info("Setting all staff to offline..")
    all_staff = StaffStatus.objects.all()
    for staff in all_staff:
        staff.staff_chat_status = StaffStatus.ChatStatus.OFFLINE
        staff.status_change_time = now
        staff.staff_stream_id = None
        staff.save()
    logger.info("Complete setting all staff to offline.")
