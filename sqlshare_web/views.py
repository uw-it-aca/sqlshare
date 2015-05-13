from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response

import urllib
import json

# create your views here

def dataset_list(request):
    return render_to_response('sqlshare_web/list.html', context_instance=RequestContext(request))

def dataset_detail(request):
    return render_to_response('sqlshare_web/detail.html', context_instance=RequestContext(request))

def dataset_upload(request):
    return render_to_response('sqlshare_web/upload.html', context_instance=RequestContext(request))