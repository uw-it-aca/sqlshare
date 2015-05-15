from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse

from sqlshare_web.utils import oauth_access_token
from sqlshare_web.utils import get_or_create_user, OAuthNeededException
from sqlshare_web.dao import get_datasets, get_dataset

import hashlib
import urllib
import json
import os


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


def upload_parser(request, filename):
    return render_to_response('sqlshare_web/parser.html',
                              context_instance=RequestContext(request))


def dataset_upload_chunk(request):
    try:
        user = get_or_create_user(request)
    except OAuthNeededException as ex:
        return ex.redirect

    if request.META['REQUEST_METHOD'] == "GET":
        return _check_upload_chunk(request, user)

    return _save_upload_chunk(request, user)


def _save_upload_chunk(request, user):
    file_path = _get_file_path(user["username"],
                               request.POST['resumableFilename'],
                               request.POST['resumableChunkNumber'],
                               )

    if not os.path.exists(os.path.dirname(file_path)):
        try:
            os.makedirs(os.path.dirname(file_path))
        except OSError:
            # Hopefully this is just a race condition with another process
            # making the directory...
            pass

    with open(file_path, 'wb+') as destination:
        for chunk in request.FILES['file'].chunks():
            destination.write(chunk)

    return HttpResponse("")


def _get_file_path(username, file_name, chunk):
    return os.path.join(settings.SQLSHARE_FILE_CHUNK_PATH,
                        username,
                        hashlib.md5(file_name).hexdigest(),
                        chunk)


def _check_upload_chunk(request, user):
    file_path = _get_file_path(user["username"],
                               request.GET['resumableFilename'],
                               request.GET['resumableChunkNumber'],
                               )

    response = HttpResponse("")
    if not os.path.exists(file_path):
        response.status_code = 404

    return response


def oauth_return(request):
    return oauth_access_token(request)
