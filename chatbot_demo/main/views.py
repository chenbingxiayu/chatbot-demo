# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import requests

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import IntegrityError
from django.core import serializers
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse

from main.models import StaffStatus, StudentChatStatus, STAFF_ORDER
from main.forms import LoginForm

logger = logging.getLogger(__name__)
COOKIE_MAX_AGE = 8 * 60 * 60


def index(request):
    return render(request, 'main/index.html')


@csrf_exempt
def auto_response(request):
    template = loader.get_template('main/index.html')
    post = request.POST['post']
    print(post)
    '''
    addr = '127.0.0.1'
    port = '8080'
    emotion = 'joy'
    url = 'http://%s:%s/cakechat_api/v1/actions/get_response' % (addr, port)
    body = {'context': [post], 'emotion': emotion}
    response = requests.post(url, json=body)
    print(response.json())
    '''

    response = 'I got your msg ' + post

    return HttpResponse(response)


@csrf_exempt
def response_api(request):
    template = loader.get_template('main/index.html')
    post = request.POST['info']
    print(post)
    addr = '127.0.0.1'
    port = '8080'
    emotion = 'joy'
    url = 'http://%s:%s/cakechat_api/v1/actions/get_response' % (addr, port)
    body = {'context': [post], 'emotion': emotion}

    response = requests.post(url, json=body)
    print(response.json())
    # print response.json()['response']

    return HttpResponse(response.json()['response'])


@require_http_methods(['GET', 'POST'])
def login_page(request):
    if request.method == "GET":
        form = LoginForm(auto_id=True)
        return render(request, 'main/login.html', {'form': form})
    elif request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            staff = form.cleaned_data['netid']  # this return StaffStatus object
            password = form.cleaned_data['password']
            role = form.cleaned_data['role']
            status = form.cleaned_data['status']

            if staff.staff_role in ('online_triage', 'do', 'counsellor'):
                staff.staff_role = role
            staff.status = status
            staff.save()

        else:
            return render(request, 'main/login.html', {'form': form})

        if staff.staff_role in ('online_triage', 'do', 'counsellor'):
            response = redirect('counsellor')
        elif staff.staff_role == 'supervisor':
            response = redirect('supervisor')
        else:
            response = redirect('administrator')
        response.set_cookie("staff_netid", staff.staff_netid, max_age=COOKIE_MAX_AGE)
        return response


@require_http_methods(['GET'])
def counsellor(request):
    staff_netid = request.COOKIES.get('staff_netid')
    now = timezone.now()
    today = now.date()
    offset = request.GET.get('offset', 0)
    limit = request.GET.get('limit', 20)

    try:
        staff = StaffStatus.objects.get(staff_netid=staff_netid)
    except StaffStatus.DoesNotExist as e:
        logger.warning(f"Staff {staff_netid} does not exist.")
        logger.warning(e)
        return render(request, 'main/404.html')

    students = StudentChatStatus.objects \
                   .filter(chat_request_time__date=today) \
                   .filter(Q(student_chat_status=StudentChatStatus.ChatStatus.WAITING) |
                           Q(assigned_counsellor=staff)) \
                   .order_by('chat_request_time')[offset:offset + limit]  # need to load timezone table for mysql
    return render(request, 'main/counsellor.html',
                  {'staff': staff, 'students': students, 'now': now})


@require_http_methods(['GET'])
def supervisor(request):
    staff_netid = request.COOKIES.get('staff_netid')
    now = timezone.now()
    today = now.date()
    offset = request.GET.get('offset', 0)
    limit = request.GET.get('limit', 20)

    try:
        staff = StaffStatus.objects.get(staff_netid=staff_netid)
    except StaffStatus.DoesNotExist as e:
        logger.warning(f"Staff {staff_netid} does not exist.")
        logger.warning(e)
        return render(request, 'main/404.html')

    students = StudentChatStatus.objects \
                   .filter(chat_request_time__date=today) \
                   .order_by('chat_request_time')[offset:offset + limit]
    return render(request, 'main/supervisor.html',
                  {'staff': staff, 'students': students, 'now': now})


@require_http_methods(['GET'])
def administrator(request):
    staff_netid = request.COOKIES.get('staff_netid')
    now = timezone.now()
    today = now.date()
    offset = request.GET.get('offset', 0)
    limit = request.GET.get('limit', 20)

    try:
        staff = StaffStatus.objects.get(staff_netid=staff_netid)
    except StaffStatus.DoesNotExist as e:
        logger.warning(f"Staff {staff_netid} does not exist.")
        logger.warning(e)
        return render(request, 'main/404.html')

    students = StudentChatStatus.objects \
                   .filter(chat_request_time__date=today) \
                   .order_by('chat_request_time')[offset:offset + limit]
    return render(request, 'main/administrator.html',
                  {'staff': staff, 'students': students, 'now': now})


@csrf_exempt
@require_http_methods(['GET'])
def staffstatus(request):
    staff_netid = request.COOKIES.get('staff_netid')
    offset = request.GET.get('offset', 0)
    limit = request.GET.get('limit', 20)
    try:
        staff = StaffStatus.objects.get(staff_netid=staff_netid)
    except StaffStatus.DoesNotExist as e:
        return JsonResponse({"error": f"staff_netid: {staff_netid} does not exist"}, status=400)

    staff_list = StaffStatus.objects.all()[offset:offset + limit]
    now = timezone.now()
    return render(request, 'main/staffstatus.html',
                  {'staff': staff, 'staff_list': staff_list, 'now': now})


@csrf_exempt
@require_http_methods(['GET'])
def getseq(request):
    res = StudentChatStatus.objects \
        .filter(student_chat_status=StudentChatStatus.ChatStatus.WAITING) \
        .order_by('-chat_request_time')
    serialized_data = serializers.serialize('python', res)

    return JsonResponse(serialized_data, safe=False, status=200)


@csrf_exempt
@require_http_methods(['POST'])
def addstud(request):
    student_netid = request.POST.get('student_netid')
    if not student_netid:
        return JsonResponse({"error": "Invalid student ID"}, status=400)

    student_status = StudentChatStatus(
        student_netid=student_netid.upper(),
    )
    try:
        student_status.save()
    except IntegrityError as e:
        return JsonResponse({'status': 'fail', 'error': str(e)}, status=400)
    return JsonResponse({'status': 'success'}, status=201)


@csrf_exempt
@require_http_methods(['GET'])
def getstud(request):
    res = StudentChatStatus.objects \
        .filter(student_chat_status=StudentChatStatus.ChatStatus.WAITING) \
        .order_by('-chat_request_time') \
        .first()
    serialized_data = serializers.serialize('python', [res])
    return JsonResponse(serialized_data[0], safe=False, status=200)


@csrf_exempt
@require_http_methods(['POST'])
def deletestud(request):
    """Remove a student from the waiting queue or change her/his status to “End”

    :param request:
    :return:
    """
    student_netid = request.POST.get('student_netid')
    student_status = StudentChatStatus.objects \
        .filter(student_chat_status=StudentChatStatus.ChatStatus.WAITING) \
        .get(student_netid=student_netid)
    student_status.student_chat_status = StudentChatStatus.ChatStatus.END
    student_status.save()

    return JsonResponse({'status': 'success'}, status=200)


@csrf_exempt
@require_http_methods(['POST'])
def updatestud(request):
    student_netid = request.POST.get('student_netid')
    new_status = request.POST.get('new_status')
    student = StudentChatStatus.objects.get(tudent_netid=student_netid)
    student.student_chat_status = new_status
    student.chat_end_time = timezone.now()
    student.save()

    return JsonResponse({'status': 'success'}, status=200)


@csrf_exempt
@require_http_methods(['GET'])
def getstafflist(request):
    res = StaffStatus.objects \
        .filter(staff_chat_status=StaffStatus.ChatStatus.AVAILABLE) \
        .values('staff_netid', 'staff_role', 'status_change_time')
    return JsonResponse(list(res), safe=False, status=200)


@csrf_exempt
@require_http_methods(['GET'])
def getstaff(request):
    role = request.GET.get('role')
    qset = StaffStatus.objects.filter(staff_chat_status=StaffStatus.ChatStatus.AVAILABLE)
    if role:
        qset = qset.filter(staff_role=role)
    res = qset.values('staff_netid').order_by('?').first()  # select randomly
    return JsonResponse(res, safe=False, status=200)


@csrf_exempt
@require_http_methods(['POST'])
def updatestaff(request):
    staff_netid = request.POST.get('staff_netid')
    new_status = request.POST.get('staff_chat_status')
    staff = StaffStatus.objects.get(staff_netid=staff_netid)
    staff.staff_chat_status = new_status
    staff.status_change_time = timezone.now()
    staff.save()

    return JsonResponse({'status': 'success'}, status=200)


@csrf_exempt
@require_http_methods(['POST'])
def addstaff(request):
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
    staff_netid = request.POST.get('staff_netid')
    delete = request.POST.get('delete')
    staff = StaffStatus.objects.get(staff_netid=staff_netid)
    if delete:
        staff.delete()
    else:
        staff.staff_chat_status = StaffStatus.ChatStatus.OFFLINE
        staff.save()

    return JsonResponse({'status': 'success'}, status=200)


@require_http_methods(['GET'])
def assignstaff(request):
    student_netid = request.COOKIES.get('student_netid')

    try:
        student = StudentChatStatus.objects.get(student_netid=student_netid)
    except StudentChatStatus.DoesNotExist as e:
        logger.warning(f"Student {student_netid} does not exist.")
        logger.warning(e)
        JsonResponse({'status': 'Student not found'}, status=400)

    if student.student_chat_status:
        JsonResponse({'status': f'Student is in {student.student_chat_status} status.'}, status=200)

    for role in STAFF_ORDER:
        staff = StaffStatus.get_random_staff_by_role(role)
        if staff:
            staff.assign_to(student)
            return JsonResponse({'assignment': 'success'}, status=200)

    student.add_to_queue()
    return JsonResponse(
        {'assignment': 'fail', 'message': 'No staff is available. Added student to waiting list  instead.'}, status=200)


@csrf_exempt
@require_http_methods(['POST'])
def startchat(request):
    student_netid = request.POST.get('student_netid')
    staff_netid = request.POST.get('staff_netid')
    now = timezone.now()
    staff = StaffStatus.objects.get(staff_netid=staff_netid)
    student = StudentChatStatus.objects.get(student_netid=student_netid)
    student.chat_start_time = now

    student.student_chat_status = StudentChatStatus.ChatStatus.CHATTING
    student.chat_start_time = now
    staff.staff_chat_status = StaffStatus.ChatStatus.CHATTING
    staff.status_change_time = now
    student.save()
    staff.save()

    return JsonResponse({'status': 'success'}, status=200)


@csrf_exempt
@require_http_methods(['POST'])
def endchat(request):
    student_netid = request.POST.get('student_netid')
    staff_netid = request.POST.get('staff_netid')
    now = timezone.now()
    staff = StaffStatus.objects.get(staff_netid=staff_netid)
    student = StudentChatStatus.objects.get(student_netid=student_netid)

    student.student_chat_status = StudentChatStatus.ChatStatus.END
    student.chat_end_time = now
    staff.staff_chat_status = StaffStatus.ChatStatus.AVAILABLE
    staff.status_change_time = now
    student.save()
    staff.save()

    return JsonResponse({'status': 'success'}, status=200)


@require_http_methods(['GET'])
def find_counsellor(request):
    """
    Find counsellor when the student enter the queue

    :return:
    """

    assignment_order = [StaffStatus.Role.ONLINETRIAGE,
                        StaffStatus.Role.DO,
                        StaffStatus.Role.COUNSELLOR]
    try:
        student = StudentChatStatus.objects.get(id=request.GET.get('student_netid'))
    except StudentChatStatus.DoesNotExist as e:
        logger.warning("Student does not exist.")
        return JsonResponse({'assignment': 'fail'}, status=400)

    for role in assignment_order:
        staff = StaffStatus.objects \
            .filter(staff_chat_status=StaffStatus.ChatStatus.AVAILABLE,
                    staff_role=role) \
            .order_by('?') \
            .first()
        if staff:
            staff.assign_to(student)
            assignment.send(sender=staff)
            return JsonResponse({'assignment': 'success'}, status=200)

    student.add_to_queue()

    return JsonResponse({'assignment': 'fail'}, status=400)
