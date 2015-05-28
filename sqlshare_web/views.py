from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from sqlshare_web.utils import oauth_access_token
from sqlshare_web.utils import get_or_create_user, OAuthNeededException
from sqlshare_web.utils import build_download_url
from sqlshare_web.dao import get_datasets, get_dataset, save_dataset_from_query
from sqlshare_web.dao import enqueue_sql_statement, get_query_data
from sqlshare_web.dao import get_download_token_for_query

import urllib
import json
import re


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
    is_public = request.POST.get("is_public", False)
    if is_public:
        # Want this to be specificly True or False, not trueish
        is_public = True

    errors = {}
    if not sql:
        errors["sql"] = True
    if not name:
        errors["name"] = True

    if errors:
        return _show_query_name_form(request, user, errors=errors)

    save_dataset_from_query(request, user["username"], name, sql, description,
                            is_public)

    return HttpResponseRedirect(reverse("dataset_detail",
                                        kwargs={"owner": user["username"],
                                                "name": name}))


def _show_query_name_form(request, user, errors={}):
    is_public = request.POST.get("is_public", False)
    if is_public:
        # Want this to be specificly True or False, not trueish
        is_public = True

    data = {
        "user": user,
        "sql": request.POST.get("sql", ""),
        "name": request.POST.get("name", ""),
        "description": request.POST.get("description", ""),
        "errors": errors,
        "is_public": is_public,
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


def run_query(request):
    """
    This view starts a query, and returns a url that can be fetched to see
    the state or result of the query.
    """
    sql = request.POST.get("sql", "")

    if not sql:
        return

    data = enqueue_sql_statement(request, sql)

    url = data["url"]
    query_id = re.match(".*v3/db/query/([\d]+)", url).groups()[0]

    return HttpResponseRedirect(reverse("sqlshare_web.views.query_status",
                                kwargs={"query_id": query_id}))


def query_status(request, query_id):
    """
    This view returns content for a query.  The query can be in process, or it
    can be a table of data.
    """
    data = get_query_data(request, query_id)

    if data["is_finished"]:
        if data["has_error"]:
            return render_to_response('sqlshare_web/query/error.html',
                                      data,
                                      context_instance=RequestContext(request))
        else:
            return render_to_response('sqlshare_web/query/results.html',
                                      data,
                                      context_instance=RequestContext(request))

    else:
        response = HttpResponse("Running...")
        response.status_code = 202
        response["Location"] = reverse("sqlshare_web.views.query_status",
                                       kwargs={"query_id": query_id})

        return response


def run_download(request):
    """
    This view starts a download, and returns a url that can be fetched to see
    the state or result of the download.
    """
    sql = request.POST.get("sql", "")

    if not sql:
        return

    data = enqueue_sql_statement(request, sql)

    url = data["url"]
    query_id = re.match(".*v3/db/query/([\d]+)", url).groups()[0]
    token_req = get_download_token_for_query(request, query_id)

    return HttpResponseRedirect(reverse("sqlshare_web.views.download_status",
                                kwargs={"query_id": query_id,
                                        "token": token_req['token']}))


def download_status(request, query_id, token=None):
    """
    This view returns content for a download.  The download can be in process,
    or it can be a download link.
    """
    data = get_query_data(request, query_id)

    if data["is_finished"]:
        if data["has_error"]:
            return render_to_response('sqlshare_web/query/error.html',
                                      data,
                                      context_instance=RequestContext(request))
        else:
            download_uri = build_download_url(query_id, token)

            return HttpResponse(download_uri)

    else:
        response = HttpResponse("Running...")
        response.status_code = 202
        response["Location"] = reverse("sqlshare_web.views.download_status",
                                       kwargs={"query_id": query_id,
                                               "token": token})

        return response
