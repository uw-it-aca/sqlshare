from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse

from sqlshare_web.utils import oauth_access_token
from sqlshare_web.utils import get_or_create_user, OAuthNeededException
from sqlshare_web.utils import get_file_path
from sqlshare_web.dao import get_datasets, get_dataset, get_parser_values
from sqlshare_web.dao import update_parser_values

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
    try:
        user = get_or_create_user(request)
    except OAuthNeededException as ex:
        return ex.redirect
    return render_to_response('sqlshare_web/upload.html',
                              context_instance=RequestContext(request))


def upload_finalize(request, filename):
    context = {
        "filename": filename,
    }
    return render_to_response('sqlshare_web/upload_finalize.html',
                              context,
                              context_instance=RequestContext(request))


def upload_parser(request, filename):
    try:
        user = get_or_create_user(request)
    except OAuthNeededException as ex:
        return ex.redirect

    if request.META['REQUEST_METHOD'] == "POST":
        has_header_row = request.POST.get("has_header", False)
        delimiter = request.POST["delimiter"]
        if delimiter == "TAB":
            delimiter = "\t"
        update_parser_values(request, user, filename, delimiter,
                             has_header_row)

        if request.POST["update_preview"] == "0":
            return redirect("upload_finalize", filename=filename)

    parser_values = get_parser_values(request, user, filename)
    return render_to_response('sqlshare_web/parser.html',
                              parser_values,
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
    file_path = get_file_path(user["username"],
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


def _check_upload_chunk(request, user):
    file_path = get_file_path(user["username"],
                              request.GET['resumableFilename'],
                              request.GET['resumableChunkNumber'],
                              )

    response = HttpResponse("")
    if not os.path.exists(file_path):
        response.status_code = 404

    return response


def oauth_return(request):
    return oauth_access_token(request)
