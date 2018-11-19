# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt


def index(request):
    return render(request, 'main/index.html')



@csrf_exempt
def auto_response(request):
    template = loader.get_template('main/index.html')
    post = request.POST['post']
    print post
    autoresponse = post + ' Yes, you are right!'
    return HttpResponse(autoresponse)
