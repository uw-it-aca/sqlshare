from django.conf import settings
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404

from sqlshare_web.utils import oauth_access_token
from sqlshare_web.utils import get_or_create_user, OAuthNeededException
from sqlshare_web.utils import get_file_path
from sqlshare_web.dao import get_datasets, get_dataset, get_parser_values
from sqlshare_web.dao import update_parser_values, append_upload_file
from sqlshare_web.dao import finalize_upload, save_dataset_from_query
from sqlshare_web.dao import enqueue_sql_statement, get_query_data
from sqlshare_web.dao import get_upload_status, update_dataset_sql
from sqlshare_web.dao import update_dataset_description
from sqlshare_web.dao import update_dataset_public_state, delete_dataset
from sqlshare_web.dao import get_user_search_results
from sqlshare_web.dao import update_dataset_permissions
from sqlshare_web.dao import get_dataset_permissions

import datetime
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

    if not dataset:
        raise Http404("Dataset Not Found")

    data = {
        "dataset": dataset,
        "user": user,
        "derive_dataset_sql": "SELECT * FROM %s" % (dataset["qualified_name"]),
        "snapshot_url": reverse("make_dataset_snapshot",
                                kwargs={"owner": owner, "name": name}),
    }

    return render_to_response('sqlshare_web/detail.html',
                              data,
                              context_instance=RequestContext(request))


def dataset_snapshot(request, owner, name):
    try:
        user = get_or_create_user(request)
    except OAuthNeededException as ex:
        return ex.redirect

    dataset = get_dataset(request, owner, name)

    if not dataset:
        raise Http404("Dataset Not Found")

    default_name = "Snapshot of %s" % name
    date = datetime.date.today().strftime("%B %-d, %Y")
    default_description = "Snapshot of %s on %s" % (dataset["sql_code"], date)

    is_public = False
    if "is_public" in request.POST:
        is_public = True
    else:
        if not request.POST:
            # Default to being public
            is_public = True
    data = {
        "dataset": dataset,
        "name": request.POST.get("name", default_name),
        "description": request.POST.get("description", default_description),
        "is_public": is_public,
        "user": user,
    }

    return render_to_response('sqlshare_web/snapshot.html',
                              data,
                              context_instance=RequestContext(request))


def dataset_upload(request):
    try:
        user = get_or_create_user(request)
    except OAuthNeededException as ex:
        return ex.redirect
    return render_to_response('sqlshare_web/upload.html',
                              {"user": user},
                              context_instance=RequestContext(request))


def finalize_process(request, filename):
    try:
        user = get_or_create_user(request)
    except OAuthNeededException as ex:
        return ex.redirect

    if request.META['REQUEST_METHOD'] == "GET":
        return _get_finalize_status(request, filename, user)

    else:
        return _update_finalize_process(request, filename, user)


def _get_finalize_status(request, filename, user):
    status = get_upload_status(request, filename)
    if status == 202:
        return HttpResponse("finalizing")

    elif status == 201:
        key1 = "ss_file_id_%s" % filename
        key2 = "ss_max_chunk_%s" % filename

        max_chunks = request.session[key2]
        for i in range(1, int(max_chunks)+1):
            file_path = get_file_path(user["username"],
                                      filename,
                                      "%s" % i,
                                      )

            os.remove(file_path)

        del request.session[key1]
        del request.session[key2]

        response = HttpResponse("Done")
        return response
    else:
        print "S: ", status


def _update_finalize_process(request, filename, user):
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

        response = HttpResponse("finalizing")
        return response


def upload_finalize(request, filename):
    try:
        user = get_or_create_user(request)
    except OAuthNeededException as ex:
        return ex.redirect

    session_key = "ss_max_chunk_%s" % filename
    chunk_count = request.session.get(session_key, 0)
    context = {
        "filename": filename,
        "file_chunk_count": chunk_count,
        "user": user,
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

    try:
        parser_values = get_parser_values(request, user, filename)

        parser_values["user"] = user
        return render_to_response('sqlshare_web/parser.html',
                                  parser_values,
                                  context_instance=RequestContext(request))
    except IOError:
        raise Http404("")


def dataset_upload_chunk(request):
    try:
        user = get_or_create_user(request)
    except OAuthNeededException as ex:
        return ex.redirect

    if request.META['REQUEST_METHOD'] == "GET":
        return _check_upload_chunk(request, user)

    return _save_upload_chunk(request, user)


def _save_upload_chunk(request, user):
    file_name = request.POST['resumableFilename']
    chunk_number = request.POST['resumableChunkNumber']
    file_path = get_file_path(user["username"],
                              file_name,
                              chunk_number,
                              )

    session_key = "ss_max_chunk_%s" % file_name
    current = request.session.get(session_key, 0)

    if chunk_number > current:
        request.session[session_key] = chunk_number

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
        raise Http404("")

    return response


def new_query(request):
    try:
        user = get_or_create_user(request)
    except OAuthNeededException as ex:
        return ex.redirect

    if "save" in request.POST:
        return _save_query(request, user)
    elif "sql" in request.POST and "show_initial" not in request.POST:
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

    if "sql" in request.POST:
        data["sql"] = request.POST["sql"]

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


def patch_dataset_sql(request, owner, name):
    try:
        user = get_or_create_user(request)
    except OAuthNeededException as ex:
        return ex.redirect

    dataset = get_dataset(request, owner, name)

    if not dataset:
        raise Http404("Dataset Not Found")

    sql = request.POST["dataset_sql"]
    update_dataset_sql(request, dataset, sql)

    return HttpResponse("")


def patch_dataset_description(request, owner, name):
    try:
        user = get_or_create_user(request)
    except OAuthNeededException as ex:
        return ex.redirect

    dataset = get_dataset(request, owner, name)

    if not dataset:
        raise Http404("Dataset Not Found")

    description = request.POST["description"]
    update_dataset_description(request, dataset, description)

    return HttpResponse("")


def dataset_permissions(request, owner, name):
    try:
        user = get_or_create_user(request)
    except OAuthNeededException as ex:
        return ex.redirect

    dataset = get_dataset(request, owner, name)

    if not dataset:
        raise Http404("Dataset Not Found")

    if request.META["REQUEST_METHOD"] == "POST":
        if "accounts[]" in request.POST:
            accounts = request.POST["accounts[]"]
        else:
            accounts = []
        update_dataset_permissions(request, dataset,
                                   request.POST.getlist("accounts[]"))

    data = get_dataset_permissions(request, dataset)
    return HttpResponse(json.dumps(data), content_type="application/json")


def patch_dataset_public(request, owner, name):
    try:
        user = get_or_create_user(request)
    except OAuthNeededException as ex:
        return ex.redirect

    dataset = get_dataset(request, owner, name)

    if not dataset:
        raise Http404("Dataset Not Found")

    is_public = request.POST["is_public"]

    if is_public == "0":
        is_public = False
    else:
        is_public = True

    update_dataset_public_state(request, dataset, is_public)

    return HttpResponse("")


def run_delete_dataset(request, owner, name):
    try:
        user = get_or_create_user(request)
    except OAuthNeededException as ex:
        return ex.redirect

    dataset = get_dataset(request, owner, name)

    if not dataset:
        raise Http404("Dataset Not Found")

    if request.META["REQUEST_METHOD"] != "POST":
        return HttpResponse("")

    delete_dataset(request, dataset)

    return HttpResponse("")


def user_search(request, term):
    try:
        user = get_or_create_user(request)
    except OAuthNeededException as ex:
        return ex.redirect

    results = get_user_search_results(request, term)

    return HttpResponse(json.dumps(results["users"]))
