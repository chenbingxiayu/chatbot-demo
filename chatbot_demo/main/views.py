from __future__ import unicode_literals

import csv
import io
import json
import logging
import os
from datetime import datetime, timedelta

import requests
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.template import loader
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from main.auth import sso_auth
from main.exceptions import UnauthorizedException, BusinessCalendarValidationError, NotFound
from main.forms import StaffLoginForm
from main.models import (
    User,
    StaffStatus,
    StudentChatStatus,
    StudentChatHistory,
    ChatBotSession,
    SELECTABLE_STATUS,
    BusinessCalendar,
    delete_student_user,
    write_overall_stat,
    write_chatbot_stat,
    write_online_chat_stat
)
from main.signals import update_queue
from main.utils import day_start, uuid2str, str2uuid, write_zip_files

logger = logging.getLogger('django')
response_json = {'status': 'success'}


@require_http_methods(['GET'])
def health(request):
    return JsonResponse({}, status=200)


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
    if os.getenv('ENV') == 'dev':
        request.path = '/main/user/login-sso/callback/'
        request.method = 'POST'
        request.POST = request.GET.copy()
        jwt_obj = {
            'aud': os.getenv('SSO_AUD'),
            'polyuUserType': os.getenv('POLYU_USER_TYPE'),
            'cn': os.getenv('CN'),
            'sub': os.getenv('SUB')
        }
        request.POST['data'] = sso_auth.encode(jwt_obj)
        return login_sso_callback(request)
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
    # To prevent a staff been deleted by accident
    try:
        if request.user.is_superuser:  # Prevent superuser admin been deleted
            is_stud = False
        else:
            is_stud = not request.user.get_groups()
    except UnauthorizedException:
        is_stud = True
    student_netid = request.user.netid
    logout(request)

    if is_stud:
        delete_student_user(student_netid)

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

    if staff.staff_role in (StaffStatus.Role.ONLINE_TRIAGE,
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
        .filter(chat_request_time__gte=day_start()) \
        .filter(Q(student_chat_status=StudentChatStatus.ChatStatus.WAITING) |
                Q(assigned_counsellor=staff)) \
        .order_by('chat_request_time')

    histories = StudentChatHistory.objects \
        .filter(chat_request_time__gte=day_start()) \
        .filter(Q(assigned_counsellor=staff)) \
        .order_by('chat_request_time')

    high_risk_students = ChatBotSession.get_high_risk_student()

    return render(request, 'main/counsellor.html',
                  {'staff': staff,
                   'students': students,
                   'histories': histories,
                   'high_risk_students': high_risk_students,
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
        .filter(chat_request_time__gte=day_start()) \
        .order_by('chat_request_time')

    histories = StudentChatHistory.objects \
        .filter(chat_request_time__gte=day_start()) \
        .order_by('chat_request_time')

    high_risk_students = ChatBotSession.get_high_risk_student()

    return render(request, 'main/supervisor.html',
                  {'staff': staff,
                   'students': students,
                   'histories': histories,
                   'high_risk_students': high_risk_students,
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
        .filter(chat_request_time__gte=day_start()) \
        .order_by('chat_request_time')

    histories = StudentChatHistory.objects \
        .filter(chat_request_time__gte=day_start()) \
        .order_by('chat_request_time')

    high_risk_students = ChatBotSession.get_high_risk_student()

    return render(request, 'main/administrator.html',
                  {'staff': staff,
                   'students': students,
                   'histories': histories,
                   'high_risk_students': high_risk_students,
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

    return render(request,
                  'main/statistics.html',
                  {'staff': staff,
                   'selectable_status': SELECTABLE_STATUS})


@login_required
@permission_required('main.view_user', raise_exception=True)
@require_http_methods(['GET', 'POST'])
def calendar_page(request):
    staff_netid = request.user.netid
    try:
        staff = StaffStatus.objects.get(staff_netid=staff_netid)
    except StaffStatus.DoesNotExist as e:
        return JsonResponse({"error": f"staff_netid: {staff_netid} does not exist"}, status=404)

    start_date = BusinessCalendar.objects.order_by('date').first()
    end_date = BusinessCalendar.objects.order_by('-date').first()

    return render(request, 'main/calendar.html',
                  {'staff': staff,
                   'start_date': start_date.date if start_date else None,
                   'end_date': end_date.date if end_date else None,
                   'selectable_status': SELECTABLE_STATUS})


@require_http_methods(['GET'])
def findstaff(request):
    """
    Find counsellor when the student enter the queue.
    Follow the staff ranking order

    :return:
    """

    assignment_order = [StaffStatus.Role.ONLINE_TRIAGE,
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
                                    "student_chat_status": StudentChatStatus.ChatStatus.WAITING,
                                    "chat_request_time": timezone.localtime(),
                                    "last_assign_time": None,
                                    "chat_start_time": None,
                                    "assigned_counsellor": None})
    msg = f"Student is {'created' if created else 'updated'}."

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

    template_data = {
        'appointment_date': '2020-06-25',
        'appointment_time': '09:00',
        'requester_name': 'Chris Wong'
    }
    email_service.send('appointment_request', '12345678A', template_data)

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
@require_http_methods(['GET'])
def count_student_in_queue(request):
    count = StudentChatStatus.objects.count()
    return JsonResponse({'student_count': count}, status=200)


@login_required
@require_http_methods(['POST'])
def get_statistics(request):
    data = json.loads(request.body)
    from_date = data.get('fromDate')
    to_date = data.get('toDate')

    f = datetime.strptime(from_date, '%Y-%m-%d')
    t = datetime.strptime(to_date, '%Y-%m-%d')

    res = {
        **ChatBotSession.statis_overview(f, t),
        **StudentChatHistory.statis_overview(f, t)
    }

    return JsonResponse(res, status=200)


@login_required
@require_http_methods(['POST'])
def export_statistics(request):
    data = json.loads(request.body)
    from_date = data.get('fromDate')
    to_date = data.get('toDate')

    f = datetime.strptime(from_date, '%Y-%m-%d')
    t = datetime.strptime(to_date, '%Y-%m-%d')

    logger.info('Query from corresponding tables.')
    chatbot_stat_data = ChatBotSession.objects \
        .filter(start_time__range=[f, t]) \
        .order_by('start_time') \
        .all()

    online_chat_stat_data = StudentChatHistory.objects \
        .filter(chat_request_time__range=[f, t]) \
        .order_by('chat_request_time') \
        .all()

    overall_stat = {
        **ChatBotSession.statis_overview(f, t),
        **StudentChatHistory.statis_overview(f, t)
    }

    chatbot_stat_file = write_chatbot_stat(list(chatbot_stat_data))
    online_chat_stat_file = write_online_chat_stat(list(online_chat_stat_data))
    overall_stat_file = write_overall_stat(overall_stat, f, t)

    logger.info('Zip all files.')
    output = write_zip_files({
        'chatbot_statistics.xlsx': chatbot_stat_file,
        'online_chat_statistics.xlsx': online_chat_stat_file,
        'overall_statistics.xlsx': overall_stat_file
    })
    response = HttpResponse(output,
                            content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="statistics.zip"'

    return response


@login_required
@require_http_methods(['POST'])
def get_red_route(request):
    data = json.loads(request.body)
    before_date = data.get('beforeDate')
    from_date = datetime.strptime(before_date, '%Y-%m-%d') - timedelta(days=7)
    to_date = datetime.strptime(before_date, '%Y-%m-%d')

    res = ChatBotSession.get_red_route(from_date, to_date)

    return JsonResponse(res, safe=False, status=200)


@login_required
@require_http_methods(['POST'])
def export_red_route(request):
    data = json.loads(request.body)
    before_date = data.get('beforeDate')
    if before_date is None:
        to_date = timezone.localtime()
    else:
        to_date = datetime.strptime(before_date, '%Y-%m-%d')
    from_date = to_date - timedelta(days=7)
    data = ChatBotSession.get_red_route(from_date, to_date)
    output = ChatBotSession.from_red_route_to_excel(data)

    response = HttpResponse(output,
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="red_route.xlsx"'
    return response


@login_required
@require_http_methods(['POST'])
def update_calendar(request):
    file = request.FILES.get('file')
    if not file:
        msg = 'No file uploaded'
        logger.warning(msg)
        response_json['status'] = 'fail'
        response_json['message'] = msg
        return JsonResponse(response_json, status=400)

    logger.info("Reading file...")
    decoded_file = file.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded_file), delimiter=',')
    calendar_dates = [line for line in reader]

    try:
        if reader.fieldnames != BusinessCalendar.field_names:
            raise BusinessCalendarValidationError(f"Field name invalid. Expecting {BusinessCalendar.field_names}, "
                                                  f"but got {reader.fieldnames}")

        BusinessCalendar.update_items_from_csv(calendar_dates)
        logger.info("Successfully updated.")
    except BusinessCalendarValidationError as e:
        msg = str(e)
        logger.error(msg)
        response_json['status'] = 'fail'
        response_json['message'] = msg
        return JsonResponse(response_json, status=400)
    except Exception as e:
        msg = str(e)
        logger.error(msg)
        response_json['status'] = 'fail'
        response_json['message'] = msg
        return JsonResponse(response_json, status=500)

    return JsonResponse(response_json, status=200)


@login_required
@require_http_methods(['GET'])
def is_working_day(request, date: str):
    try:
        calendar_date = BusinessCalendar.get_date(date)
    except NotFound as e:
        msg = str(e)
        logger.warning(msg)
        response_json['status'] = 'fail'
        response_json['message'] = msg
        return JsonResponse(response_json, status=404)

    return JsonResponse({'is_working_day': calendar_date.is_working_day}, status=200)


@login_required
@require_http_methods(['GET'])
def is_working_hour(request):
    try:
        res = BusinessCalendar.is_working_hour()
    except NotFound as e:
        msg = str(e)
        logger.warning(msg)
        response_json['status'] = 'fail'
        response_json['message'] = msg
        return JsonResponse(response_json, status=404)

    return JsonResponse({'is_working_hour': res}, status=200)


@login_required
@require_http_methods(['GET'])
def is_chatting_working_hour(request):
    try:
        res = BusinessCalendar.is_chatting_working_hour()
    except NotFound as e:
        msg = str(e)
        logger.warning(msg)
        response_json['status'] = 'fail'
        response_json['message'] = msg
        return JsonResponse(response_json, status=404)

    return JsonResponse({'is_chatting_working_hour': res}, status=200)
