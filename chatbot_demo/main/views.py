# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import requests

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import redirect

from main.models import StaffStatus, StudentChatStatus, StudentChatHistory
from main.forms import LoginForm
from main.utils import today_start

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

    try:
        staff = StaffStatus.objects.get(staff_netid=staff_netid)
    except StaffStatus.DoesNotExist as e:
        logger.warning(f"Staff {staff_netid} does not exist.")
        logger.warning(e)
        return render(request, 'main/404.html')

    students = StudentChatStatus.objects \
        .filter(chat_request_time__gte=today_start()) \
        .filter(Q(student_chat_status=StudentChatStatus.ChatStatus.WAITING) |
                Q(assigned_counsellor=staff)) \
        .order_by('chat_request_time')

    histories = StudentChatHistory.objects \
        .filter(chat_request_time__gte=today_start()) \
        .filter(Q(assigned_counsellor=staff)) \
        .order_by('chat_request_time')

    return render(request, 'main/counsellor.html',
                  {'staff': staff,
                   'students': students,
                   'histories': histories,
                   'now': now,
                   'selectable_status': {
                       StaffStatus.ChatStatus.AVAILABLE: [StaffStatus.ChatStatus.AVAILABLE,
                                                          StaffStatus.ChatStatus.ASSIGNED,
                                                          StaffStatus.ChatStatus.CHATTING],
                       StaffStatus.ChatStatus.AWAY: [StaffStatus.ChatStatus.AWAY]}
                   })


@require_http_methods(['GET'])
def supervisor(request):
    staff_netid = request.COOKIES.get('staff_netid')
    now = timezone.now()

    try:
        staff = StaffStatus.objects.get(staff_netid=staff_netid)
    except StaffStatus.DoesNotExist as e:
        logger.warning(f"Staff {staff_netid} does not exist.")
        logger.warning(e)
        return render(request, 'main/404.html')

    students = StudentChatStatus.objects \
        .filter(chat_request_time__gte=today_start()) \
        .filter(Q(student_chat_status=StudentChatStatus.ChatStatus.WAITING) |
                Q(assigned_counsellor=staff)) \
        .order_by('chat_request_time')

    histories = StudentChatHistory.objects \
        .filter(chat_request_time__gte=today_start()) \
        .order_by('chat_request_time')

    return render(request, 'main/supervisor.html',
                  {'staff': staff,
                   'students': students,
                   'histories': histories,
                   'now': now,
                   'selectable_status': {
                       StaffStatus.ChatStatus.AVAILABLE: [StaffStatus.ChatStatus.AVAILABLE,
                                                          StaffStatus.ChatStatus.ASSIGNED,
                                                          StaffStatus.ChatStatus.CHATTING],
                       StaffStatus.ChatStatus.AWAY: [StaffStatus.ChatStatus.AWAY]}
                   })


@require_http_methods(['GET'])
def administrator(request):
    staff_netid = request.COOKIES.get('staff_netid')
    now = timezone.now()
    offset = request.GET.get('offset', 0)
    limit = request.GET.get('limit', 20)

    try:
        staff = StaffStatus.objects.get(staff_netid=staff_netid)
    except StaffStatus.DoesNotExist as e:
        logger.warning(f"Staff {staff_netid} does not exist.")
        logger.warning(e)
        return render(request, 'main/404.html')

    students = StudentChatStatus.objects \
        .filter(chat_request_time__gte=today_start()) \
        .filter(Q(student_chat_status=StudentChatStatus.ChatStatus.WAITING) |
                Q(assigned_counsellor=staff)) \
        .order_by('chat_request_time')

    histories = StudentChatHistory.objects \
        .filter(chat_request_time__gte=today_start()) \
        .order_by('chat_request_time')
    return render(request, 'main/administrator.html',
                  {'staff': staff,
                   'students': students,
                   'histories': histories,
                   'now': now,
                   'selectable_status': {
                       StaffStatus.ChatStatus.AVAILABLE: [StaffStatus.ChatStatus.AVAILABLE,
                                                          StaffStatus.ChatStatus.ASSIGNED,
                                                          StaffStatus.ChatStatus.CHATTING],
                       StaffStatus.ChatStatus.AWAY: [StaffStatus.ChatStatus.AWAY]}
                   })


@csrf_exempt
@require_http_methods(['GET'])
def staffstatus(request):
    staff_netid = request.COOKIES.get('staff_netid')
    try:
        staff = StaffStatus.objects.get(staff_netid=staff_netid)
    except StaffStatus.DoesNotExist as e:
        return JsonResponse({"error": f"staff_netid: {staff_netid} does not exist"}, status=400)

    staff_list = StaffStatus.objects.all()
    now = timezone.now()
    return render(request, 'main/staffstatus.html',
                  {'staff': staff, 'staff_list': staff_list, 'now': now})


@require_http_methods(['GET'])
def findstaff(request):
    """
    Find counsellor when the student enter the queue.
    Follow the staff ranking order

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
            return JsonResponse({'assignment': 'success'}, status=200)

    student.add_to_queue()

    return JsonResponse({'assignment': 'fail'}, status=400)


@require_http_methods(['POST'])
def updatestaff(request):
    """
    Staff can change their status between Availabe <-> Away.
    If staff's status now is Assigned, the assignment will lose for both the staff and the student.

    :param request:
    :return:
    """
    new_status = request.POST.get('status')
    staff_netid = request.COOKIES.get('staff_netid')
    try:
        staff = StaffStatus.objects.get(staff_netid=staff_netid)
    except StaffStatus.DoesNotExist:
        logger.warning('Staff does not exist.')
        return JsonResponse({"status": "status update fail"}, status=400)

    if staff.staff_chat_status == StaffStatus.ChatStatus.ASSIGNED and new_status == StaffStatus.ChatStatus.AWAY:
        student = StudentChatStatus.objects \
            .filter(student_chat_status=StudentChatStatus.ChatStatus.ASSIGNED,
                    assigned_counsellor=staff) \
            .first()
        student.add_to_queue()
    staff.staff_chat_status = new_status
    staff.save()

    return JsonResponse({"status": "update fail success"}, status=200)
