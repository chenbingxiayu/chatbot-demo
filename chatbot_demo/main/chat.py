import json
from .zulip.zulip import ZulipClient
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required


config_file = './.zuliprc'
client = ZulipClient(config_file=config_file)
email_suffix = settings.ZULIP['EMAIL_SUBFFIX']


def _construct_stream_name(staff_netid: str):
    return f"{staff_netid}_chatroom"

@login_required
def student(request):
    try:
        student_netid = request.GET.get('student_netid', '21')
        student_email = student_netid + email_suffix
        staff_netid = request.GET.get('staff_netid', '10')
        staff_email = staff_netid + email_suffix
        stream_name = _construct_stream_name(staff_netid)

        users = client.get_users()
        
        student = next(
            (user for user in users['members'] if user['email'] == student_email), None)
        if student is None:
            client.create_user(student_email, student_netid)
        key = client.fetch_user_api_key(student_email, student_email)
        page_info = {
            'key': key,
            'student_email': student_email,
            'student_netid': student_netid,
            'stream_name': stream_name,
            'staff_netid': staff_netid,
            'staff_email': staff_email,
        }

        return render(request, 'chat/chat_student.html', page_info)
    except Exception as e:
        print(e)

@login_required
def counsellor(request):
    try:
        staff_netid = request.GET.get('staff_netid', '10')
        student_netid = request.GET.get('student_netid', '21')
        student_email = student_netid + email_suffix
        staff_email = staff_netid + email_suffix

        users = client.get_users()

        staff = next(
            (user for user in users['members'] if user['email'] == staff_email), None)
        if staff is None:
            client.create_user(staff_email, staff_netid)

        # We will use `${staff_email}` to construct the stream name.
        stream_name = _construct_stream_name(
            staff_netid=staff_netid)

        stream_id = client.get_stream_id(stream_name)

        if stream_id is None:
            client.create_stream(stream_name=stream_name, user_ids=[
                student_email, staff_email])
            stream_id = client.get_stream_id(stream_name)
        else:
            client.subscribe_stream(stream_name=stream_name,
                                    subscribers=[staff_email, student_email])

        key = client.fetch_user_api_key(staff_email, staff_email)

        page_info = {
            'key': key,
            'staff_email': staff_email,
            'staff_netid': staff_netid,
            'stream_name': stream_name,
            'student_email': student_email,
            'student_netid': student_netid,
            'stream_id': stream_id,
        }

        return render(request, 'chat/chat_counsellor.html', page_info)
    except Exception as e:
        print(e)


@csrf_exempt
@require_http_methods(['POST'])
def subscribe_stream(request):
    request_data = json.loads(request.body)
    staff_netid = request_data['staff_netid']
    # student_netid = request_data['student_netid']
    subscribers = request_data['subscribers_netid']

    staff_email = staff_netid + email_suffix
    # student_email = student_netid + email_suffix
    # subscribers = [item + email_suffix for item in subscribers]

    users = client.get_users()
    subscribers_email = []
    for subscriber_netid in subscribers:
        subscriber_email = subscriber_netid + email_suffix

        is_exist = next(
            (user for user in users['members'] if user['email'] == subscriber_email), None)
        if is_exist is None:
            print("subsriber isn't exist, create a new one")
            client.create_user(username=subscriber_email,
                               name=subscriber_netid)

        subscribers_email.append(subscriber_email)

    stream_name = _construct_stream_name(
        staff_netid=staff_netid
    )

    try:
        response = client.subscribe_stream(stream_name=stream_name,
                                           subscribers=subscribers_email)

        if response['result'] == 'error':
            return JsonResponse({
                'status': 'success',
                'content': {
                    'result': response
                }
            })
        else:
            return JsonResponse({
                'status': 'success',
                'content': {
                    'stream_name': stream_name
                }
            })
    except Exception as e:
        return JsonResponse({'status': "error", "error": str(e)})


@csrf_exempt
@require_http_methods(['POST'])
def unsubscribe_stream(request):
    
    request_data = json.loads(request.body)
    staff_netid = request_data['staff_netid']
    # student_netid = request_data['student_netid']
    unsubscribers = request_data['unsubscribers_netid']

    staff_email = staff_netid + email_suffix
    # student_email = student_netid + email_suffix

    users = client.get_users()
    subscribers_email = []
    for subscriber_netid in unsubscribers:
        subscriber_email = subscriber_netid + email_suffix

        is_exist = next(
            (user for user in users['members'] if user['email'] == subscriber_email), None)
        if is_exist is None:
            continue

        subscribers_email.append(subscriber_email)

    stream_name = _construct_stream_name(
        staff_netid=staff_netid,
    )

    try:
        response = client.unsubscribe_stream(
            stream_name=stream_name, unsubscribers=subscribers_email)

        if response['result'] == 'error':
            return JsonResponse({
                'status': 'error',
                'content': {
                    'result': response
                }
            })
        else:
            return JsonResponse({
                'status': 'success',
                'content': {
                    'stream_name': stream_name
                }
            })
    except Exception as e:
        return JsonResponse({'status': "error", "error": str(e)})


@csrf_exempt
@require_http_methods(['POST'])
def delete_stream(request):
    request_data = json.loads(request.body)
    staff_netid = request_data['staff_netid']
    staff_email = staff_netid + email_suffix

    stream_name = _construct_stream_name(
        staff_netid=staff_netid
    )

    try:
        stream_id = client.get_stream_id(stream_name=stream_name)
        result = client.delete_stream(stream_id=stream_id)

        if result['result'] == 'success':
            return JsonResponse({
                'status': 'success',
                'content': {
                    'stream_name': stream_name
                }
            })
        else:
            return JsonResponse({
                'status': 'error',
                'content': {
                    'result': result
                }
            })
    except Exception as e:
        return JsonResponse({'status': "error", "error": str(e)})

@login_required
@require_http_methods(['GET'])
def stream_room(request):
    try:
        staff_netid = request.GET.get('staff_netid', None)
        supervisor_netid = request.GET.get('supervisor_netid', None)

        if staff_netid is None or supervisor_netid is None:
            raise('Please provide both stream name and supervisor email.')

        staff_email = staff_netid + email_suffix

        stream_name = _construct_stream_name(
            staff_netid=staff_netid
        )

        stream_id = client.get_stream_id(stream_name)
        supervisor_email = supervisor_netid + email_suffix

        users = client.get_users()
        supervisor = next(
            (user for user in users['members'] if user['email'] == supervisor_email), None)
        if supervisor is None:
            client.create_user(supervisor_email, supervisor_netid)

        client.subscribe_stream(stream_name=stream_name,
                                subscribers=[supervisor_email])
        key = client.fetch_user_api_key(supervisor_email, supervisor_email)
        page_info = {
            'key': key,
            'stream_name': stream_name,
            'supervisor_email': supervisor_email,
            'supervisor_netid': supervisor_netid,
            'stream_id': stream_id,
            'staff_netid': staff_netid,
            'staff_email': staff_email,
        }

        return render(request, 'chat/chat_stream_room.html', page_info)

    except Exception as e:
        return e


@csrf_exempt
@require_http_methods(['POST'])
def delete_stream_in_topic(request):
    request_data = json.loads(request.body)
    staff_netid = request_data['staff_netid']
    staff_email = staff_netid + email_suffix

    stream_name = _construct_stream_name(
        staff_netid=staff_netid
    )

    try:
        stream_id = client.get_stream_id(stream_name=stream_name)
        result = client.delete_stream_in_topic(stream_id=stream_id, topic='chat')

        if result['result'] == 'success':
            return JsonResponse({
                'status': 'success',
                'content': {
                    'stream_name': stream_name,
                    'topic': 'chat'
                }
            })
        else:
            return JsonResponse({
                'status': 'error',
                'content': {
                    'result': result
                }
            })
    except Exception as e:
        return JsonResponse({'status': "error", "error": str(e)})