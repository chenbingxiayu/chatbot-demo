from django.urls import path, include
from django.views.i18n import JavaScriptCatalog

from main import views, debug_api, chat

urlpatterns = [
    path('', views.index, name='index'),
    path('response', views.auto_response, name='auto_response'),
    path('response_api', views.response_api, name='response_api'),

    # web pages
    path('login/staff/', views.login_page, name='login_staff'),
    path('page/chatconsole/', views.chat_console, name='chat_console'),
    path('page/counsellor/', views.counsellor, name='counsellor'),
    path('page/supervisor/', views.supervisor, name='supervisor'),
    path('page/administrator/', views.administrator, name='administrator'),
    path('page/staffstatus/', views.staffstatus, name='staffstatus'),
    path('page/statistics/', views.statistics_page, name='statispage'),
    path('page/calendar/', views.calendar_page, name='calendarpage'),

    # APIs
    path('api/logout/', views.logout_staff, name='logout_staff'),
    path('api/findstaff/', views.findstaff, name='findstaff'),
    path('api/updatestaff/', views.updatestaff, name='updatestaff'),
    path('api/addstud/', views.addstud, name='addstud'),
    path('api/appointstaff/', views.appointstaff, name='appointstaff'),
    path('api/supervisorjoin/', views.supervisor_join, name='supervisorjoin'),
    path('api/submitsurvey/', views.submit_survey, name='submitsurvey'),
    path('api/endchatbot/', views.end_chatbot, name='endchatbot'),
    path('api/get_statistics/', views.get_statistics, name='get_statistics'),
    path('api/export_statistics/', views.export_statistics, name='export_statistics'),
    path('api/get_red_route/', views.get_red_route, name='get_red_route'),
    path('api/export_red_route/', views.export_red_route, name='export_red_route'),
    path('api/update_calendar/', views.update_calendar, name='update_calendar'),
    path('api/working_day/<str:date>/', views.is_working_day, name='working_day'),
    path('api/working_hour/', views.is_working_hour, name='working_hour'),
    path('user/login/', views.login_all, name='login'),
    path('user/login-sso/', views.login_sso, name='login_sso'),
    path('user/login-sso/callback/', views.login_sso_callback, name='login_sso_callback'),
    path('user/logout/student/', views.student_logout, name='student_logout'),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('i18n/', include('django.conf.urls.i18n'))
]

debug_urls = [
    path('debug/getseq/', debug_api.getseq, name='debug_getseq'),
    # path('debug/addstud/', debug_api.addstud, name='debug_addstud'),
    path('debug/getstud/', debug_api.getstud, name='debug_getstud'),
    path('debug/deletestud/', debug_api.deletestud, name='debug_deletestud'),
    # path('debug/updatestud/', debug_api.updatestud, name='debug_updatestud'),
    # path('debug/getstafflist/', debug_api.getstafflist, name='debug_getstafflist'),
    # path('debug/getstaff/', debug_api.getstaff, name='debug_getstaff'),
    # path('debug/addstaff/', debug_api.addstaff, name='debug_addstaff'),
    # path('debug/updatestaff/', debug_api.updatestaff, name='debug_updatestaff'),
    # path('debug/deletestaff/', debug_api.deletestaff, name='debug_deletestaff'),
    # path('debug/assignstaff/', debug_api.assignstaff, name='debug_assignstaff'),
    path('debug/startchat/', debug_api.startchat, name='debug_stratchat'),
    path('debug/endchat/', debug_api.endchat, name='debug_endchat'),
    # path('debug/reassign_counsellor/', debug_api.reassign_task, name='reassign_counsellor'),
    # path('debug/dequeue_student/', debug_api.dequeue_task, name='dequeue_student'),
]

chat_urls = [
    path('chat/student/', chat.student, name='chat_student'),
    path('chat/counsellor/', chat.counsellor, name='chat_counsellor'),
    path('chat/subscribe_stream/', chat.subscribe_stream, name='chat_subscribe_stream'),
    path('chat/unsubscribe_stream/', chat.unsubscribe_stream, name='chat_unsubscribe_stream'),
    path('chat/delete_stream/', chat.delete_stream, name='chat_delete_stream'),
    path('chat/delete_stream_in_topic/', chat.delete_stream_in_topic, name='chat_delete_stream_in_topic'),
    path('chat/stream_room/', chat.stream_room, name='chat_stream_room'),
]

urlpatterns += debug_urls
urlpatterns += chat_urls
