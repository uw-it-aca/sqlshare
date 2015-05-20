from django.conf import settings
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect

from sqlshare_web.utils import oauth_access_token
from sqlshare_web.utils import get_or_create_user, OAuthNeededException
from sqlshare_web.utils import get_file_path
from sqlshare_web.dao import get_datasets, get_dataset, get_parser_values
from sqlshare_web.dao import update_parser_values, append_upload_file
from sqlshare_web.dao import finalize_upload, save_dataset_from_query
from sqlshare_web.dao import enqueue_sql_statement, get_query_data

import urllib
import json
import os
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
    try:
        user = get_or_create_user(request)
    except OAuthNeededException as ex:
        return ex.redirect
    return render_to_response('sqlshare_web/upload.html',
                              context_instance=RequestContext(request))


def finalize_process(request, filename):
    try:
        user = get_or_create_user(request)
    except OAuthNeededException as ex:
        return ex.redirect

    if "chunk" in request.POST:
        chunk = request.POST["chunk"]
        file_path = get_file_path(user["username"],
                                  filename,
                                  chunk,
                                  )

        if not os.path.exists(file_path):
            return HttpResponse("upload_complete")
        else:
            append_upload_file(request, user, filename, chunk)
            return HttpResponse("next_chunk")

    if "finalize" in request.POST:
        name = request.POST["dataset_name"]
        description = request.POST["dataset_description"]
        is_public = request.POST["is_public"]

        finalize_upload(request, filename, name, description)

    return HttpResponse("OK")


def upload_finalize(request, filename):
    context = {
        "filename": filename,
        "file_chunk_count": 30,
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
