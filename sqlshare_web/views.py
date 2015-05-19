from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from sqlshare_web.utils import oauth_access_token
from sqlshare_web.utils import get_or_create_user, OAuthNeededException
from sqlshare_web.dao import get_datasets, get_dataset, save_dataset_from_query

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
    try:
        user = get_or_create_user(request)
    except OAuthNeededException as ex:
        return ex.redirect

    if "save" in request.POST:
        return _save_query(request, user)
    elif "sql" in request.POST:
        return _show_query_name_form(request, user)

    else:
        return _show_new_query_form(request, user)


def _save_query(request, user):
    sql = request.POST.get("sql", "")
    name = request.POST.get("name", "")
    description = request.POST.get("description", "")

    errors = {}
    if not sql:
        errors["sql"] = True
    if not name:
        errors["name"] = True

    if errors:
        return _show_query_name_form(request, user, errors=errors)

    is_public = False
    save_dataset_from_query(request, user["username"], name, sql, description,
                            is_public)

    return HttpResponseRedirect(reverse("dataset_detail",
                                        kwargs={"owner": user["username"],
                                                "name": name}))


def _show_query_name_form(request, user, errors={}):
    data = {
        "user": user,
        "sql": request.POST.get("sql", ""),
        "name": request.POST.get("name", ""),
        "description": request.POST.get("description", ""),
        "errors": errors,
    }

    return render_to_response('sqlshare_web/query/name.html',
                              data,
                              context_instance=RequestContext(request))


def _show_new_query_form(request, user):
    data = {
        "user": user,
    }

    return render_to_response('sqlshare_web/query/run.html',
                              data,
                              context_instance=RequestContext(request))


def oauth_return(request):
    return oauth_access_token(request)
