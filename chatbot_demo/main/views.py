# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
import os


def index(request):
    return render(request, 'main/index.html')



@csrf_exempt
def auto_response(request):
    template = loader.get_template('main/index.html')
    post = request.POST['post']

    post_to_be_send = 'python3 ../../cakechat/tools/test_api.py -c' + '\''+ post + '\''
    print post_to_be_send
    autoresponse = os.system(post_to_be_send)
    print autoresponse['response']

    return HttpResponse(autoresponse['response'])
