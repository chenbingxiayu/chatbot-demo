# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
import os
import json
import requests

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.serializers.json import DjangoJSONEncoder
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import IntegrityError
from django.core import serializers

from main.models import StaffStatus, StudentChatStatus


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


@csrf_exempt
@require_http_methods(['GET'])
def counsellor(request):
    staff_netid = request.COOKIES.get('staff_netid')
    offset = request.GET.get('offset', 0)
    limit = request.GET.get('limit', 20)

    try:
        staff = StaffStatus.objects.get(staff_netid=staff_netid)
    except StaffStatus.DoesNotExist as e:
        return JsonResponse({"error": f"staff_netid: {staff_netid} does not exist"}, status=400)

    students = StudentChatStatus.objects.order_by('chat_request_time')[offset:offset + limit]
    now = timezone.now()
    return render(request, 'main/counsellor.html',
                  {'staff': staff, 'students': students, 'now': now})


@csrf_exempt
@require_http_methods(['GET'])
def supervisor(request):
    staff_netid = request.COOKIES.get('staff_netid')
    offset = request.GET.get('offset', 0)
    limit = request.GET.get('limit', 20)

    try:
        staff = StaffStatus.objects.get(staff_netid=staff_netid)
    except StaffStatus.DoesNotExist as e:
        return JsonResponse({"error": f"staff_netid: {staff_netid} does not exist"}, status=400)

    students = StudentChatStatus.objects.order_by('chat_request_time')[offset:offset + limit]
    now = timezone.now()
    return render(request, 'main/supervisor.html',
                  {'staff': staff, 'students': students, 'now': now})


@csrf_exempt
@require_http_methods(['GET'])
def administrator(request):
    staff_netid = request.COOKIES.get('staff_netid')
    offset = request.GET.get('offset', 0)
    limit = request.GET.get('limit', 20)

    try:
        staff = StaffStatus.objects.get(staff_netid=staff_netid)
    except StaffStatus.DoesNotExist as e:
        return JsonResponse({"error": f"staff_netid: {staff_netid} does not exist"}, status=400)

    students = StudentChatStatus.objects.order_by('chat_request_time')[offset:offset + limit]
    now = timezone.now()
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

    now = timezone.now()
    student_status = StudentChatStatus(
        student_netid=student_netid.upper(),
        chat_request_time=now,
        student_chat_status=StudentChatStatus.ChatStatus.WAITING,
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
    res = qset.values('staff_netid').first()
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


@csrf_exempt
@require_http_methods(['POST'])
def assignstaff(request):
    student_netid = request.POST.get('student_netid')
    staff_netid = request.POST.get('staff_netid')
    now = timezone.now()
    staff = StaffStatus.objects.get(staff_netid=staff_netid)
    student = StudentChatStatus.objects.get(student_netid=student_netid)

    student.student_chat_status = StudentChatStatus.ChatStatus.CHATTING
    student.chat_start_time = now
    student.assigned_counsellor_id = staff
    staff.staff_chat_status = StaffStatus.ChatStatus.CHATTING
    staff.status_change_time = now
    student.save()
    staff.save()

    return JsonResponse({'status': 'success'}, status=200)
