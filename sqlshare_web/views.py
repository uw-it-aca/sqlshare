from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse

from sqlshare_web.utils import oauth_access_token
from sqlshare_web.utils import get_or_create_user, OAuthNeededException
from sqlshare_web.dao import get_datasets, get_dataset

import urllib
import json


def dataset_list(request):
    try:
        user = get_or_create_user(request)
    except OAuthNeededException as ex:
        return ex.redirect

    datasets = get_datasets(request)

    data = {
        "datasets": datasets,
        "user": user,
    }

    return render_to_response('sqlshare_web/list.html',
                              data,
                              context_instance=RequestContext(request))


def dataset_detail(request, owner, name):
    try:
        user = get_or_create_user(request)
    except OAuthNeededException as ex:
        return ex.redirect

    dataset = get_dataset(request, owner, name)

    print dataset

    data = {
        "dataset": dataset,
        "user": user,
    }

    return render_to_response('sqlshare_web/detail.html',
                              data,
                              context_instance=RequestContext(request))


def dataset_upload(request):
    return render_to_response('sqlshare_web/upload.html',
                              context_instance=RequestContext(request))

def new_query(request):
    return render_to_response('sqlshare_web/new.html',
                              context_instance=RequestContext(request))

def oauth_return(request):
    return oauth_access_token(request)
