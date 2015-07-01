from django.conf import settings
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404

from sqlshare_web.utils import oauth_access_token
from sqlshare_web.utils import get_or_create_user, OAuthNeededException
from sqlshare_web.utils import build_download_url
from sqlshare_web.dao import get_download_token_for_query
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
from sqlshare_web.dao import make_dataset_snapshot
from sqlshare_web.dao import get_recent_queries, cancel_query_by_id
from sqlshare_web.dao import init_sql_download
from sqlshare_web.exceptions import DataPermissionDeniedException
from sqlshare_web.exceptions import DataException

import datetime
from urllib import urlencode
import json
from sqlshare_web.dao import get_upload_status
import os
import re


def dataset_list(request, list_type):
    try:
        user = get_or_create_user(request)
    except OAuthNeededException as ex:
        return ex.redirect

    q = None
    if "q" in request.GET:
        q = request.GET["q"]

    datasets = get_datasets(request, page=1, query=q, list_type=list_type)

    if q is None:
        q = ""

    next_page = "%s?%s" % (reverse("sqlshare_web.views.dataset_list_page"),
                           urlencode({
                            "page": 2,
                            "q": q,
                            "list_type": list_type,
                           }))

    if list_type == "yours":
        is_yours = True
    data = {
        "datasets": datasets,
        "user": user,
        "current_query": q,
        "next_page_url": next_page,
        "is_yours": list_type == "yours",
        "is_shared": list_type == "shared",
        "is_all": list_type == "all",
        "is_recent": list_type == "recent",
    }

    return render_to_response('sqlshare_web/list.html',
                              data,
                              context_instance=RequestContext(request))


def recent_queries(request):
    try:
        user = get_or_create_user(request)
    except OAuthNeededException as ex:
        return ex.redirect

    if request.META["REQUEST_METHOD"] == "POST":
        query_id = request.POST["query_id"]
        cancel_query_by_id(request, query_id)

    queries = get_recent_queries(request)

    data = {
        "queries": queries,
        "user": user,
    }

    return render_to_response('sqlshare_web/query_list.html',
                              data,
                              context_instance=RequestContext(request))


def query_status_page(request, query_id):
    try:
        user = get_or_create_user(request)
    except OAuthNeededException as ex:
        return ex.redirect

    try:
        query = get_query_data(request, query_id)
    except DataException:
        raise Http404("Query not found")

    data = {
        "query": query,
        "user": user,
    }

    return render_to_response('sqlshare_web/query/status_page.html',
                              data,
                              context_instance=RequestContext(request))


def dataset_list_page(request):
    try:
        user = get_or_create_user(request)
    except OAuthNeededException as ex:
        return ex.redirect

    q = None
    if "q" in request.GET and request.GET["q"] != "":
        q = request.GET["q"]

    page = request.GET["page"]
    list_type = request.GET["list_type"]

    datasets = get_datasets(request, page=page, query=q, list_type=list_type)

    if q is None:
        q = ""
    next_page = "%s?%s" % (reverse("sqlshare_web.views.dataset_list_page"),
                           urlencode({
                            "page": int(page) + 1,
                            "q": q,
                            "list_type": list_type,
                           }))

    data = {
        "user": user,
        "datasets": datasets,
        "next_page_url": next_page,
    }

    return render_to_response('sqlshare_web/list_page.html',
                              data,
                              context_instance=RequestContext(request))


def dataset_detail(request, owner, name):
    try:
        user = get_or_create_user(request)
    except OAuthNeededException as ex:
        return ex.redirect

    try:
        dataset = get_dataset(request, owner, name)
    except DataPermissionDeniedException:
        return render_to_response('sqlshare_web/detail_no_permission.html', {})

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

    errors = {}
    if "save" in request.POST:
        name = request.POST.get("name", "")
        description = request.POST.get("description", "")
        is_public = request.POST.get("is_public", False)
        if is_public:
            is_public = True

        if not name:
            errors["name"] = True

        else:
            new_url = make_dataset_snapshot(request, dataset, name,
                                            description, is_public)
            if new_url:
                response = HttpResponseRedirect(new_url)
                return response

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
        "errors": errors,
        "dataset_url": reverse("dataset_detail",
                               kwargs={"owner": owner, "name": name}),
    }

    return render_to_response('sqlshare_web/snapshot.html',
                              data,
                              context_instance=RequestContext(request))


def dataset_upload(request):
    try:
        user = get_or_create_user(request)
    except OAuthNeededException as ex:
        return ex.redirect
    return render_to_response('sqlshare_web/upload/upload.html',
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
    data = get_upload_status(request, filename)

    status = data["status"]
    if status == 202:
        response_data = {
            "state": "finalizing",
            "rows_total": data["values"]["rows_total"],
            "rows_loaded": data["values"]["rows_loaded"],
        }
        return HttpResponse(json.dumps(response_data),
                            content_type="application/json")

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

        response = HttpResponse('{ "state": "Done"}',
                                content_type="application/json")
        return response
    else:
        print ("S: ", status)


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
            session_key = "ss_max_chunk_%s" % filename
            max_chunk = request.session.get(session_key, 0)

            append_upload_file(request, user, filename, chunk)

            json_data = {
                "state": "next_chunk",
                "max": max_chunk,
                "finished": chunk,
            }
            return HttpResponse(json.dumps(json_data),
                                content_type="application/json")

    if "finalize" in request.POST:
        name = request.POST["dataset_name"]
        description = request.POST["dataset_description"]
        is_public = request.POST["is_public"]

        if is_public == "public":
            is_public = True
        else:
            is_public = False

        finalize_upload(request, filename, name, description, is_public)

        response = HttpResponse('{ "state": "finalizing"}',
                                content_type="application/json")
        return response


def upload_parser(request, filename):
    try:
        user = get_or_create_user(request)
    except OAuthNeededException as ex:
        return ex.redirect

    key1 = "ss_file_id_%s" % filename
    if key1 not in request.session:
        return Http404()

    if request.META['REQUEST_METHOD'] == "POST":
        has_header_row = request.POST.get("has_header", False)
        delimiter = request.POST["delimiter"]
        if delimiter == "TAB":
            delimiter = "\t"
        update_parser_values(request, user, filename, delimiter,
                             has_header_row)

    try:
        parser_values = get_parser_values(request, user, filename)

        if request.META['REQUEST_METHOD'] == "POST":
            parser_values["new_name"] = request.POST["dataset_name"]
            parser_values["description"] = request.POST["dataset_description"]
            parser_values["is_public"] = request.POST["is_public"]

        if "new_name" not in parser_values or parser_values["new_name"] == "":
            parser_values["new_name"] = filename

        parser_values["user"] = user
        parser_values["filename"] = filename
        return render_to_response('sqlshare_web/upload/parser.html',
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

    if re.match('.*[\[\]/\\\?#]', name):
        errors["name_chars"] = True

    if errors:
        return _show_query_name_form(request, user, errors=errors)

    try:
        save_dataset_from_query(request, user["username"], name, sql,
                                description,
                                is_public)
    except DataException as ex:
        errors["sql"] = True
        errors["sql_syntax"] = str(ex)
        return _show_query_name_form(request, user, errors=errors)

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


def run_download(request):
    """
    This view starts a download, and returns a url that can be fetched to see
    the state or result of the download.
    """
    sql = request.POST.get("sql", "")

    if not sql:
        return

    download_url = init_sql_download(request, sql)

    response = HttpResponse()
    response.status_code = 202
    response["Location"] = download_url

    return response
