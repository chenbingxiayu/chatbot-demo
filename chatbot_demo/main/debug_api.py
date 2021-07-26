import json
import logging
from datetime import timedelta

import requests
from django.core import serializers
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict

from main.models import (
    StaffStatus,
    StudentChatStatus,
    StudentChatHistory,
    ChatBotSession,
    ROLE_RANKING
)
from main.utils import hk_time
from tasks.tasks import reassign_counsellor, dequeue_student

logger = logging.getLogger('django')


@csrf_exempt
@require_http_methods(['GET'])
def getseq(request):
    """
    Get the waiting queue of online chatting service, only return the students in status Waiting

    :param request:
    :return:
    """

    res = StudentChatStatus.objects \
        .filter(student_chat_status=StudentChatStatus.ChatStatus.WAITING) \
        .order_by('chat_request_time')
    serialized_data = serializers.serialize('python', res)

    return JsonResponse(serialized_data, safe=False, status=200)


@csrf_exempt
@require_http_methods(['POST'])
def addstud(request):
    """
    Add student into the waiting queue and set one's status as Waiting
    Convert letters in the strings of NetID to capitalized

    :param request:
    :return:
    """
    student_netid = request.POST.get('student_netid')
    status = request.POST.get('status')
    if not student_netid:
        return JsonResponse({"error": "Invalid student ID"}, status=400)

    student, created = StudentChatStatus.objects \
        .get_or_create(student_netid=student_netid.upper(),
                       defaults={'chat_request_time': timezone.now()})
    msg = f"{student} is {'created' if created else 'updated'}"
    if status:
        student.add_to_queue()
    return JsonResponse({'status': 'success', 'message': msg}, status=201)


@csrf_exempt
@require_http_methods(['GET'])
def getstud(request):
    """
    Get the info (netid and waiting time) of first student in the queue.
    Get a student if student_netid is specified.

    :param request:
    :param student_netid:
    :return:
    """
    student_netid = request.GET.get('student_netid')
    if student_netid:
        try:
            student = StudentChatStatus.objects.get(student_netid=student_netid)
            student_data = model_to_dict(student)
        except StudentChatStatus.DoesNotExist as e:
            logger.warning(e)
            student_data = dict()

        return JsonResponse(student_data, status=200)
    else:
        res = StudentChatStatus.objects \
                  .filter(student_chat_status=StudentChatStatus.ChatStatus.WAITING) \
                  .order_by('chat_request_time') \
                  .all()[:1]
        serialized_data = serializers.serialize('python', res)
        return JsonResponse(serialized_data[:1], safe=False, status=200)


@csrf_exempt
@require_http_methods(['POST'])
def deletestud(request):
    """
    Remove a student from the waiting queue or change one's status to End

    :param request:
    :return:
    """
    student_netid = request.POST.get('student_netid')
    now = timezone.now()
    with transaction.atomic():
        try:
            student = StudentChatStatus.objects \
                .get(student_netid=student_netid)
            StudentChatHistory.append_end_chat(student, now)
            student.delete()
        except Exception as e:
            logger.warning(e)
            return JsonResponse({'status': 'fail', 'error': str(e)}, status=400)

    return JsonResponse({'status': 'success'}, status=200)


@csrf_exempt
@require_http_methods(['POST'])
def updatestud(request):
    """
    Update a student’s status

    :param request:
    :return:
    """
    student_netid = request.POST.get('student_netid')
    new_status = request.POST.get('new_status')
    if new_status not in StudentChatStatus.ChatStatus:
        return JsonResponse({'status': 'fail', 'error': 'status value is in status choices.'}, status=400)
    student = StudentChatStatus.objects.get(student_netid=student_netid)
    student.student_chat_status = new_status
    student.chat_end_time = timezone.now()
    student.save()

    return JsonResponse({'status': 'success'}, status=200)


@csrf_exempt
@require_http_methods(['GET'])
def getstafflist(request):
    """
    Get the netid and roles of all the available staffs

    :param request:
    :return:
    """
    res = StaffStatus.objects \
        .filter(staff_chat_status=StaffStatus.ChatStatus.AVAILABLE) \
        .values('staff_netid', 'staff_role', 'status_change_time')
    return JsonResponse(list(res), safe=False, status=200)


@csrf_exempt
@require_http_methods(['GET'])
def getstaff(request):
    """
    Get the netid of an available staff playing specific role randomly

    :param request:
    :return:
    """
    role = request.GET.get('role')
    qset = StaffStatus.objects.filter(staff_chat_status=StaffStatus.ChatStatus.AVAILABLE)
    if role:
        qset = qset.filter(staff_role=role)
    res = qset.values('staff_netid').order_by('?').first()  # select randomly

    return JsonResponse(res, safe=False, status=200)


@csrf_exempt
@require_http_methods(['POST'])
def updatestaff(request):
    """
    Update a staff’s staff_chat_status and status_change_time in Staff_Status

    :param request:
    :return:
    """
    staff_netid = request.POST.get('staff_netid')
    new_status = request.POST.get('staff_chat_status')
    if new_status not in StaffStatus.ChatStatus:
        return JsonResponse({'status': 'fail', 'error': 'status value is in status choices.'}, status=400)
    staff = StaffStatus.objects.get(staff_netid=staff_netid)
    staff.staff_chat_status = new_status
    staff.status_change_time = timezone.now()
    staff.save()

    return JsonResponse({'status': 'success'}, status=200)


@csrf_exempt
@require_http_methods(['POST'])
def addstaff(request):
    """
    Add a staff convert letters in the strings of NetID to capitalized

    :param request:
    :return:
    """
    staff_netid = request.POST.get('staff_netid')
    if not staff_netid:
        return JsonResponse({"error": "Invalid staff ID"}, status=400)

    now = timezone.now()
    staff_status = StaffStatus(
        staff_name=request.POST.get('staff_name'),
        staff_netid=staff_netid.upper(),
        staff_role=request.POST.get('staff_role'),
        staff_chat_status=request.POST.get('staff_chat_status'),
        status_change_time=now
    )
    try:
        staff_status.save()
    except IntegrityError as e:
        return JsonResponse({'status': 'fail', 'error': str(e)}, status=400)
    return JsonResponse({'status': 'success'}, status=201)


@csrf_exempt
@require_http_methods(['POST'])
def deletestaff(request):
    """
    Remove a staff or change her/his status to Offline

    :param request:
    :return:
    """
    staff_netid = request.POST.get('staff_netid')
    delete = request.POST.get('delete')
    try:
        staff = StaffStatus.objects.get(staff_netid=staff_netid)
    except StaffStatus.DoesNotExist:
        logger.warning("Staff does not exist.")
        return JsonResponse({'status': 'fail'}, status=400)

    if delete:
        staff.delete()
    else:
        staff.staff_chat_status = StaffStatus.ChatStatus.OFFLINE
        staff.save()

    return JsonResponse({'status': 'success'}, status=200)


@csrf_exempt
@require_http_methods(['POST'])
def assignstaff(request):
    """
    Assign a staff for a student waiting for online chatting.

    :param request:
    :return:
    """
    student_netid = request.POST.get('student_netid')
    now = timezone.now()
    with transaction.atomic():
        try:
            staff = StaffStatus.objects.select_for_update() \
                .filter(staff_chat_status=StaffStatus.ChatStatus.AVAILABLE,
                        staff_role__in=ROLE_RANKING) \
                .order_by('?') \
                .first()
            student = StudentChatStatus.objects \
                .get(student_netid=student_netid.upper())
            staff.assign_to(student)
        except Exception as e:
            logger.warning(e)
            return JsonResponse({'status': 'fail', 'assignment': f'fail. {e}'}, status=200)

    return JsonResponse({'status': 'success', 'assignment': 'success'}, status=200)


@csrf_exempt
@require_http_methods(['POST'])
def startchat(request):
    """
    Change the status of the staff and the student to Chatting

    :param request:
    :return:
    """
    student_netid = request.POST.get('student_netid')
    staff_netid = request.POST.get('staff_netid')
    now = timezone.now()

    with transaction.atomic():
        try:
            staff = StaffStatus.objects.select_for_update().get(staff_netid=staff_netid.upper())
            student = StudentChatStatus.objects.select_for_update().get(student_netid=student_netid.upper())

            student.chat_start_time = now
            student.student_chat_status = StudentChatStatus.ChatStatus.CHATTING
            staff.staff_chat_status = StaffStatus.ChatStatus.CHATTING
            staff.status_change_time = now
            student.save()
            staff.save()
        except Exception as e:
            logger.warning(e)
            return JsonResponse({'status': 'success', 'error': str(e)}, status=400)

    return JsonResponse({'status': 'success'}, status=200)


@csrf_exempt
@require_http_methods(['POST'])
def endchat(request):
    """
    Change the status of the staff to Available and that of the student to End

    :param request:
    :return:
    """
    student_netid = request.POST.get('student_netid')
    staff_netid = request.POST.get('staff_netid')
    now = timezone.now()

    with transaction.atomic():
        try:
            staff = StaffStatus.objects.select_for_update().get(staff_netid=staff_netid.upper())
            student = StudentChatStatus.objects.select_for_update().get(student_netid=student_netid.upper())

            StudentChatHistory.append_end_chat(student, now)
            staff.staff_chat_status = StaffStatus.ChatStatus.AVAILABLE
            staff.status_change_time = now
            student.delete()
            staff.save()
        except Exception as e:
            logger.warning(e)
            return JsonResponse({'status': 'success', 'error': str(e)}, status=400)

    return JsonResponse({'status': 'success'}, status=200)


@csrf_exempt
@require_http_methods(['GET'])
def reassign_task(request):
    reassign_counsellor()
    return JsonResponse({'status': 'success'}, status=200)


@csrf_exempt
@require_http_methods(['GET'])
def dequeue_task(request):
    dequeue_student()
    return JsonResponse({'status': 'success'}, status=200)


@csrf_exempt
@require_http_methods(['POST'])
def add_survey_data(request):
    survey_data = json.loads(request.body.decode('utf-8'))
    now = timezone.now().astimezone(hk_time) - timedelta(days=1)
    today = now.date()
    ChatBotSession(
        date=today,
        start_time=now.time(),
        end_time=(now + timedelta(seconds=15 * 60)).time(),
        is_ployu_student=survey_data['is_ployu_student'],
        student_netid=survey_data['student_netid'],
        language=survey_data['language'],
        q1_academic=survey_data['q1_academic'],
        q1_interpersonal_relationship=survey_data['q1_interpersonal_relationship'],
        q1_career=survey_data['q1_career'],
        q1_family=survey_data['q1_family'],
        q1_mental_health=survey_data['q1_mental_health'],
        q1_others=survey_data['q1_others'],
        q2=survey_data['q2'],
        q3=survey_data['q3'],
        q4=survey_data['q4'],
        q5=survey_data['q5'],
        q6_1=survey_data['q6_1'],
        q6_2=survey_data['q6_2'],
        score=survey_data['score'],
        first_option=survey_data['first_option'],
        feedback_rating=survey_data['feedback_rating']
    ).save()

    return JsonResponse({'status': 'success'}, status=201)


@csrf_exempt
@require_http_methods(['GET'])
def export_statistics(request):
    from_date = timezone.now().date() - timedelta(days=1)
    to_date = timezone.now().date()

    ChatBotSession.statis_overview(from_date, to_date)
    return JsonResponse({'status': 'success'}, status=200)


@csrf_exempt
@require_http_methods(['GET'])
def get_red_route(request):
    from_date = timezone.now().astimezone(hk_time).date() - timedelta(days=7)

    ChatBotSession.get_red_route(from_date)
    return JsonResponse({'status': 'success'}, status=200)


@csrf_exempt
@require_http_methods(['GET'])
def export_red_route(request):
    from_date = timezone.now().astimezone(hk_time).date() - timedelta(days=7)

    ChatBotSession.get_red_route_to_excel(from_date)
    return JsonResponse({'status': 'success'}, status=200)
