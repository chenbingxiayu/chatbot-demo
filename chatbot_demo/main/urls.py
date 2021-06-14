from django.urls import path

from main import views, debug_api

urlpatterns = [
    path('', views.index, name='index'),
    path('response', views.auto_response, name='auto_response'),
    path('response_api', views.response_api, name='response_api'),
    path('login/staff/', views.login_page, name='login_page'),
    path('page/counsellor/', views.counsellor, name='counsellor'),
    path('page/supervisor/', views.supervisor, name='supervisor'),
    path('page/administrator/', views.administrator, name='administrator'),
    path('page/staffstatus/', views.staffstatus, name='staffstatus'),
    path('api/findstaff/', views.findstaff, name='findstaff'),
    path('api/updatestaff/', views.updatestaff, name='updatestaff'),
    path('api/addstud/', views.addstud, name='addstud')
]

debug_urls = [
    path('debug/getseq/', debug_api.getseq, name='debug_getseq'),
    path('debug/addstud/', debug_api.addstud, name='debug_addstud'),
    path('debug/getstud/', debug_api.getstud, name='debug_getstud'),
    path('debug/deletestud/', debug_api.deletestud, name='debug_deletestud'),
    path('debug/updatestud/', debug_api.updatestud, name='debug_updatestud'),
    path('debug/getstafflist/', debug_api.getstafflist, name='debug_getstafflist'),
    path('debug/getstaff/', debug_api.getstaff, name='debug_getstaff'),
    path('debug/addstaff/', debug_api.addstaff, name='debug_addstaff'),
    path('debug/updatestaff/', debug_api.updatestaff, name='debug_updatestaff'),
    path('debug/deletestaff/', debug_api.deletestaff, name='debug_deletestaff'),
    path('debug/assignstaff/', debug_api.assignstaff, name='debug_assignstaff'),
    path('debug/startchat/', debug_api.startchat, name='debug_stratchat'),
    path('debug/endchat/', debug_api.endchat, name='debug_endchat'),
    path('debug/reassign_counsellor/', debug_api.reassign_task, name='reassign_counsellor'),
    path('debug/dequeue_student/', debug_api.dequeue_task, name='dequeue_student'),
]

urlpatterns += debug_urls
