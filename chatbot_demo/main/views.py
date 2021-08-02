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
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required

from main.exceptions import UnauthorizedException
from main.models import StaffStatus, StudentChatStatus, StudentChatHistory, SELECTABLE_STATUS
from main.forms import StaffLoginForm
from main.utils import today_start
from main.signals import update_queue
from tasks.tasks import assign_staff
from main.auth import sso_auth

logger = logging.getLogger('django')
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


@login_required
@require_http_methods(['GET'])
def login_page(request):
    if request.method == "GET":
        form = StaffLoginForm(auto_id=True)
        return render(request, 'main/login_staff.html', {'form': form})


@login_required
@require_http_methods(['GET'])
def logout_view(request):
    logout(request)

    return redirect('login')


@login_required
@require_http_methods(['POST', 'GET'])
def chat_console(request):
    staff_netid = request.user.netid
    user_group = request.session['user_group']
    try:
        staff = StaffStatus.objects.get(staff_netid=staff_netid)
    except StaffStatus.DoesNotExist:
        staff = StaffStatus(staff_netid=staff_netid)

    if request.method == 'POST':
        # check which user group does the user belongs to
        if user_group == 'counsellor':
            staff.staff_role = request.POST.get('role')
        elif user_group == 'app_admin':
            staff.staff_role = StaffStatus.Role.SUPERVISOR

        staff.staff_chat_status = request.POST.get('status')
        staff.status_change_time = timezone.localtime()
        staff.save()
        staff.refresh_from_db()

    if staff.staff_role in ('online_triage', 'do', 'counsellor'):
        return redirect('counsellor')
    elif staff.staff_role == 'supervisor':
        return redirect('supervisor')
    elif staff.staff_role == 'administrator':
        return redirect('administrator')
    else:
        return redirect('login_page')


@login_required
@require_http_methods(['GET'])
def counsellor(request):
    staff_netid = request.user.netid
    now = timezone.localtime()

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
                   'selectable_status': SELECTABLE_STATUS})


@login_required
@require_http_methods(['GET'])
def supervisor(request):
    staff_netid = request.user.netid
    now = timezone.localtime()

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
                   'selectable_status': SELECTABLE_STATUS})


@login_required
@require_http_methods(['GET'])
def administrator(request):
    staff_netid = request.user.netid
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
    return render(request, 'main/administrator.html',
                  {'staff': staff,
                   'students': students,
                   'histories': histories,
                   'now': now,
                   'selectable_status': SELECTABLE_STATUS})


@login_required
@permission_required('main.view_staffstatus', raise_exception=True)
@require_http_methods(['GET'])
def staffstatus(request):
    staff_netid = request.user.netid
    try:
        staff = StaffStatus.objects.get(staff_netid=staff_netid)
    except StaffStatus.DoesNotExist as e:
        return JsonResponse({"error": f"staff_netid: {staff_netid} does not exist"}, status=400)

    staff_list = StaffStatus.objects.all()
    now = timezone.now()
    return render(request, 'main/staffstatus.html',
                  {'staff': staff, 'staff_list': staff_list, 'now': now,
                   'selectable_status': SELECTABLE_STATUS})


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
        student = StudentChatStatus.objects.get(student_netid=request.GET.get('student_netid'))
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
            staff.notify_assignment()
            return JsonResponse({'assignment': 'success'}, status=200)

    student.add_to_queue()

    return JsonResponse({'assignment': 'fail'}, status=400)


@login_required
@require_http_methods(['POST'])
def updatestaff(request):
    """
    Staff can change their status between Availabe <-> Away.
    If staff's status now is Assigned, the assignment will lose for both the staff and the student.

    :param request:
    :return:
    """
    new_status = request.POST.get('status')
    staff_netid = request.user.netid
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

    return JsonResponse({"status": "update success"}, status=200)


@csrf_exempt
@require_http_methods(['POST'])
def addstud(request):
    """
    Assign staff to new coming student.
    Or add student to waiting queue.

    :param request:
    :return:
    """
    student_netid = request.POST.get('student_netid')

    # TODO validate studentID
    if not student_netid:
        return JsonResponse({"error": "Invalid student ID"}, status=400)

    student, created = StudentChatStatus.objects \
        .update_or_create(student_netid=student_netid.upper(),
                          defaults={"student_chat_status": None,
                                    "chat_request_time": timezone.now(),
                                    "last_assign_time": None,
                                    "chat_start_time": None,
                                    "assigned_counsellor": None})
    msg = f"Student is {'created' if created else 'updated'}."

    if assign_staff(student):
        msg += f" Student is assigned to a staff."
        return JsonResponse({'status': 'success', 'message': msg}, status=201)
    else:
        student.add_to_queue()
        update_queue.send(sender=None)
        msg += f" No staff available, added student to queue."
        return JsonResponse({'status': 'success', 'message': msg}, status=201)


def login_all(request):
    return render(request, 'main/login_sso.html')


@csrf_exempt
def login_sso(request):
    # redirect to rapid connect server
    response = redirect(sso_auth.destination)
    return response


@csrf_exempt
@require_http_methods(['POST', 'GET'])
def login_sso_callback(request):
    try:
        encoded_jwt = request.POST.get('data')
        if not encoded_jwt:
            return render(request, 'main/login_sso.html', {
                'error_message': "Cannot get JWT"
            })
        decoded_jwt = sso_auth.decode(encoded_jwt)

        if decoded_jwt['polyuUserType'] == 'Student':
            return render(request, 'main/login_sso.html', {
                'decoded_jwt': decoded_jwt
            })

        elif decoded_jwt['polyuUserType'] == 'Staff':
            staff_netid = decoded_jwt['cn']
            user = authenticate(requests, netid=staff_netid)
            user_group = user.get_groups()
            request.session['user_group'] = user_group
            login(request, user)
            return redirect('login_staff')

    except (Exception, UnauthorizedException) as e:
        logger.warning(e)
        return redirect('login')
