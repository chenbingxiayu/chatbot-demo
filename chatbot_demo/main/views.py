from __future__ import unicode_literals

import io
import logging
import uuid
import json
from datetime import datetime, timedelta

import requests
import xlsxwriter

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test

from main.exceptions import UnauthorizedException
from main.models import (
    User,
    StaffStatus,
    StudentChatStatus,
    StudentChatHistory,
    ChatBotSession,
    SELECTABLE_STATUS
)
from main.forms import StaffLoginForm
from main.utils import today_start, uuid2str, str2uuid
from main.signals import update_queue
from tasks.tasks import assign_staff
from main.auth import sso_auth

COOKIE_MAX_AGE = 8 * 60 * 60

logger = logging.getLogger('django')
response_json = {'status': 'success'}


@login_required
def index(request):
    student_netid = request.user.netid
    return render(request, 'main/index.html', {
        "student_netid": student_netid
    })


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
            try:
                student_netid = decoded_jwt.get('sub', '').upper()
                student_user = User.objects.get(netid=student_netid)
            except User.DoesNotExist:
                student_user = User.objects.create_user(netid=student_netid, is_active=True)
            authenticate(requests, netid=student_netid)
            login(request, student_user, backend='django.contrib.auth.backends.ModelBackend')

            chatbot_session = ChatBotSession.usage_chatbot_connect(
                student_netid=student_netid,
                is_ployu_student=True
            )

            request.session['session_id'] = uuid2str(chatbot_session.session_id)
            return redirect('index')

        elif decoded_jwt['polyuUserType'] == 'Staff':
            staff_netid = decoded_jwt['cn']
            user = authenticate(requests, netid=staff_netid)
            user_group = user.get_groups()
            request.session['user_group'] = user_group
            login(request, user)
            return redirect('login_staff')

        ChatBotSession.usage_chatbot_connect()

    except (Exception, UnauthorizedException) as e:
        logger.warning(e)
        return redirect('login')


@login_required
@require_http_methods(['GET'])
def student_logout(request):
    student_netid = request.user.netid
    logout(request)

    try:
        student_user = User.objects.get(netid=student_netid)
        student_user.delete()

    except User.DoesNotExist:
        return render(request, 'main/404.html')

    return redirect('login')


@login_required
@require_http_methods(['GET'])
def login_page(request):
    if request.method == "GET":
        user_group = request.session['user_group']

        form = StaffLoginForm(user_group, auto_id=True)
        return render(request, 'main/login_staff.html', {'form': form})


@login_required
@require_http_methods(['GET'])
def logout_staff(request):
    staff_netid = request.user.netid
    logout(request)

    try:
        staff = StaffStatus.objects.get(staff_netid=staff_netid)
        staff.staff_chat_status = StaffStatus.ChatStatus.OFFLINE
        staff.status_change_time = timezone.localtime()
        staff.save()

        StudentChatStatus.unassign_from(staff)
    except StaffStatus.DoesNotExist:
        return render(request, 'main/404.html')

    return redirect('login')


@login_required
@require_http_methods(['POST', 'GET'])
def chat_console(request):
    staff_netid = request.user.netid

    try:
        staff = StaffStatus.objects.get(staff_netid=staff_netid)
    except StaffStatus.DoesNotExist:
        staff = StaffStatus(staff_netid=staff_netid)

    if request.method == 'POST':
        # check which user group does the user belongs to

        staff.staff_role = request.POST.get('role')
        staff.staff_chat_status = request.POST.get('status')
        staff.status_change_time = timezone.localtime()
        staff.save()
        staff.refresh_from_db()

    if staff.staff_role in (StaffStatus.Role.ONLINETRIAGE,
                            StaffStatus.Role.DO,
                            StaffStatus.Role.COUNSELLOR):
        return redirect('counsellor')
    elif staff.staff_role == StaffStatus.Role.SUPERVISOR:
        return redirect('supervisor')
    elif staff.staff_role == StaffStatus.Role.ADMIN:
        return redirect('administrator')
    else:
        return redirect('login')


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
        return JsonResponse({"error": f"staff_netid: {staff_netid} does not exist"}, status=404)

    staff_list = StaffStatus.objects.all()
    now = timezone.now()
    return render(request, 'main/staffstatus.html',
                  {'staff': staff, 'staff_list': staff_list, 'now': now,
                   'selectable_status': SELECTABLE_STATUS})


@login_required
@permission_required('main.view_user', raise_exception=True)
@require_http_methods(['GET', 'POST'])
def statistics_page(request):
    staff_netid = request.user.netid
    try:
        staff = StaffStatus.objects.get(staff_netid=staff_netid)
    except StaffStatus.DoesNotExist as e:
        return JsonResponse({"error": f"staff_netid: {staff_netid} does not exist"}, status=404)

    now = timezone.now()
    return render(request, 'main/statistics.html',
                  {'staff': staff,
                   'now': now,
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

    if staff.staff_chat_status == StaffStatus.ChatStatus.ASSIGNED \
            and new_status == StaffStatus.ChatStatus.AWAY:
        StudentChatStatus.unassign_from(staff)
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
        .update_or_create(student_netid=student_netid,
                          defaults={"q1": request.POST.get('q1'),
                                    "q2": request.POST.get('q2'),
                                    "personal_contact_number": request.POST.get('personal_contact_number'),
                                    "emergency_contact_name": request.POST.get('emergency_contact_name'),
                                    "relationship": request.POST.get('relationship'),
                                    "emergency_contact_number": request.POST.get('emergency_contact_number'),
                                    "student_chat_status": None,
                                    "last_assign_time": None,
                                    "chat_start_time": None,
                                    "assigned_counsellor": None})
    msg = f"Student is {'created' if created else 'updated'}."

    if assign_staff(student):
        msg += f" Student is assigned to a staff."
        response_json['message'] = msg
        return JsonResponse(response_json, status=201)
    else:
        student.add_to_queue()
        update_queue.send(sender=None)
        msg += f" No staff available, added student to queue."
        response_json['message'] = msg
        return JsonResponse(response_json, status=201)


@login_required
@require_http_methods(['POST'])
def supervisor_join(request):
    student_netid = request.POST.get('student_netid')
    status_code = 200
    try:
        student = StudentChatStatus.objects.get(student_netid=student_netid)
        student.is_supervisor_join = True
        student.save()
    except StudentChatStatus.DoesNotExist:
        msg = "Student does not exit. Supervisor cannot join the chat."
        logger.warning(msg)
        response_json['status'] = 'fail'
        response_json['message'] = msg
        status_code = 404

    return JsonResponse(response_json, status=status_code)


@csrf_exempt
@require_http_methods(['GET'])
def appointstaff(request):
    from main.email_service import email_service

    email_service.send('appointment_request', '12345678A', {
        'appointment_date': '2020-06-25',
        'appointment_time': '09:00',
        'requester_name': 'Chris Wong'
    })

    return JsonResponse({'status': 'success'}, status=200)


@login_required
@require_http_methods(['POST'])
def submit_survey(request):
    try:

        session = ChatBotSession.objects.get(session_id=str2uuid(request.session['session_id']))
        session.language = request.POST.get('language')
        session.q1_academic = json.loads(request.POST.get('q1_academic'))
        session.q1_interpersonal_relationship = json.loads(request.POST.get('q1_interpersonal_relationship'))
        session.q1_career = json.loads(request.POST.get('q1_career'))
        session.q1_family = json.loads(request.POST.get('q1_family'))
        session.q1_mental_health = json.loads(request.POST.get('q1_mental_health'))
        session.q1_others = json.loads(request.POST.get('q1_others'))
        session.q2 = json.loads(request.POST.get('q2'))
        session.q3 = request.POST.get('q3')
        session.q4 = request.POST.get('q4')
        session.q5 = json.loads(request.POST.get('q5'))
        session.q6_1 = json.loads(request.POST.get('q6_1'))
        session.q6_2 = json.loads(request.POST.get('q6_2'))
        session.score = request.POST.get('score')
        session.save()
        status_code = 200
    except ChatBotSession.DoesNotExist:
        msg = "Session does not exist. Chatbot survey is not saved."
        logger.warning(msg)
        response_json['status'] = 'fail'
        response_json['message'] = msg
        status_code = 404

    return JsonResponse(response_json, status=status_code)


@login_required
@require_http_methods(['POST'])
def end_chatbot(request):
    try:
        session = ChatBotSession.objects.get(session_id=str2uuid(request.session['session_id']))
        session.first_option = request.POST.get('first_option')
        session.feedback_rating = request.POST.get('feedback_rating')
        session.end_time = timezone.localtime()
        session.save()
        status_code = 200
    except ChatBotSession.DoesNotExist:
        msg = "Session does not exist. Error occurs when ending survey."
        logger.warning(msg)
        response_json['status'] = 'fail'
        response_json['message'] = msg
        status_code = 404

    return JsonResponse(response_json, status=status_code)


@login_required
@require_http_methods(['POST'])
def get_statistics(request):
    data = json.loads(request.body)
    from_date = data.get('fromDate')
    to_date = data.get('toDate')

    res = dict()
    res.update(ChatBotSession.statis_overview(from_date, to_date))
    res.update(StudentChatHistory.statis_overview(from_date, to_date))

    return JsonResponse(res, status=200)


@login_required
@require_http_methods(['POST'])
def export_statistics(request):
    data = json.loads(request.body)
    from_date = data.get('fromDate')
    to_date = data.get('toDate')

    res = ChatBotSession.statis_overview(from_date, to_date)
    res.update(StudentChatHistory.statis_overview(from_date, to_date))

    output = io.BytesIO()
    wb = xlsxwriter.Workbook(output)
    ws = wb.add_worksheet('Statistics Overview')

    ws.write(0, 0, 'From')
    ws.write(0, 1, from_date)
    ws.write(1, 0, 'To')
    ws.write(1, 1, to_date)

    row_name = {
        'No. of access': 'total_access_count',
        'No. of office hour access': 'access_office_hr_count',
        'No. of PolyU student': 'polyu_student_count',
        'No. of non-student': 'non_polyu_student_count',
        'No. of green': 'score_green_count',
        'No. of yellow': 'score_yellow_count',
        'No. of red': 'score_red_count',
        'No. of access to POSS': 'poss_access_count',
        'No. of access to Mental Health 101': 'mh101_access_count',
        'No. of access to Online Chat Service': 'online_chat_access_count',
        'No. of successful chat with counsellor': 'successful_chat_count'
    }

    for row_idx, (key, val) in enumerate(row_name.items(), 2):
        ws.write(row_idx, 0, key)
        ws.write(row_idx, 1, res[val])

    wb.close()
    output.seek(0)
    response = HttpResponse(output,
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="statistics_overview.xlsx"'

    return response


@login_required
@require_http_methods(['POST'])
def get_red_route(request):
    data = json.loads(request.body)
    before_date = data.get('beforeDate')
    from_date = datetime.strptime(before_date, '%Y-%m-%d') - timedelta(days=7)

    res = ChatBotSession.get_red_route(from_date)

    return JsonResponse(res, safe=False, status=200)


@login_required
@require_http_methods(['POST'])
def export_red_route(request):
    data = json.loads(request.body)
    before_date = data.get('beforeDate')
    output = ChatBotSession.get_red_route_to_excel(before_date)

    response = HttpResponse(output,
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="red_route.xlsx"'
    return response
