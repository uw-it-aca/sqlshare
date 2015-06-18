from sqlshare_web.utils import send_request, get_file_path
from urllib import quote, urlencode
import json
import re


def get_datasets(request, page=1, query=None, list_type="yours"):
    page_size = 2
    order_by = "updated"

    input_data = {"page": page,
                  "page_size": page_size,
                  "order_by": order_by
                  }

    if query:
        input_data["q"] = query

    url_suffix = ""
    if list_type == "all":
        url_suffix = "/all"
    elif list_type == "shared":
        url_suffix = "/shared"
    elif list_type == "recent":
        url_suffix = "/recent"

    params = urlencode(input_data)
    response = send_request(request, 'GET',
                            '/v3/db/dataset%s?%s' % (url_suffix, params),
                            {"Accept": "application/json"})

    data = json.loads(response.content)

    return data


def get_dataset(request, owner, name):
    url = '/v3/db/dataset/%s/%s' % (quote(owner), quote(name))
    response = send_request(request, 'GET', url,
                            {"Accept": "application/json"})

    if response.status == 200:
        data = json.loads(response.content)

        return data
    return None


def delete_dataset(request, dataset):
    url = '/v3/db/dataset/%s/%s' % (quote(dataset["owner"]),
                                    quote(dataset["name"]))
    response = send_request(request, 'DELETE', url,
                            {"Accept": "application/json"})


def update_dataset_sql(request, dataset, sql):
    url = '/v3/db/dataset/%s/%s' % (quote(dataset["owner"]),
                                    quote(dataset["name"]))
    data = json.dumps({"sql_code": sql})
    response = send_request(request, 'PATCH', url,
                            {"Accept": "application/json"}, body=data)


def update_dataset_description(request, dataset, description):
    url = '/v3/db/dataset/%s/%s' % (quote(dataset["owner"]),
                                    quote(dataset["name"]))
    data = json.dumps({"description": description})
    response = send_request(request, 'PATCH', url,
                            {"Accept": "application/json"}, body=data)


def update_dataset_public_state(request, dataset, is_public):
    url = '/v3/db/dataset/%s/%s' % (quote(dataset["owner"]),
                                    quote(dataset["name"]))
    data = json.dumps({"is_public": is_public})
    response = send_request(request, 'PATCH', url,
                            {"Accept": "application/json"}, body=data)


def make_dataset_snapshot(request, dataset, name, description, is_public):
    url = '/v3/db/dataset/%s/%s/snapshot' % (quote(dataset["owner"]),
                                             quote(dataset["name"]))
    data = json.dumps({"name": name,
                       "description": description,
                       "is_public": is_public})
    response = send_request(request, 'POST', url,
                            {"Accept": "application/json"}, body=data)

    base_location = response.headers["location"]

    segment = re.match('.*?/v3/db/dataset/(.*)', base_location).groups(1)

    return "/detail/%s" % segment


def get_parser_values(request, user, filename):
    session_key = "ss_file_id_%s" % filename
    if session_key not in request.session:
        path = get_file_path(user["username"], filename, "1")

        with open(path, 'rb') as source:
            data = source.read()

        url = '/v3/db/file/'
        response = send_request(request, 'POST', url,
                                {"Accept": "application/json",
                                 "Content-type": "text/plain",
                                 },
                                body=data)

        upload_id = json.loads(response.content)

        request.session[session_key] = upload_id

    upload_id = request.session[session_key]

    parser_url = '/v3/db/file/%s/parser' % (upload_id)

    response = send_request(request, 'GET', parser_url,
                            {"Accept": "application/json"})

    data = json.loads(response.content)

    return {
        "upload_id": upload_id,
        "parser_values": data,
    }


def append_upload_file(request, user, filename, chunk):
    session_key = "ss_file_id_%s" % filename

    upload_id = request.session[session_key]
    path = get_file_path(user["username"], filename, "%s" % chunk)

    with open(path, 'rb') as source:
        data = source.read()

    url = '/v3/db/file/%s' % (upload_id)
    response = send_request(request, 'POST', url,
                            {"Accept": "application/json",
                             "Content-type": "text/plain",
                             },
                            body=data)


def finalize_upload(request, filename, name, description):
    session_key = "ss_file_id_%s" % filename

    upload_id = request.session[session_key]
    url = '/v3/db/file/%s/finalize' % (upload_id)

    data = json.dumps({"dataset_name": name,
                       "description": description,
                       })

    response = send_request(request, 'POST', url,
                            {"Accept": "application/json",
                             "Content-type": "text/plain",
                             },
                            body=data)


def get_upload_status(request, filename):
    session_key = "ss_file_id_%s" % filename

    upload_id = request.session[session_key]
    url = '/v3/db/file/%s/finalize' % (upload_id)
    response = send_request(request, 'GET', url,
                            {"Accept": "application/json",
                             "Content-type": "text/plain",
                             },
                            )

    return response.status


def update_parser_values(request, user, filename, delimiter, has_header_row):
    session_key = "ss_file_id_%s" % filename
    upload_id = request.session[session_key]

    parser_url = '/v3/db/file/%s/parser' % (upload_id)

    data = json.dumps({"parser": {"delimiter": delimiter,
                                  "has_column_header": has_header_row}})

    response = send_request(request, 'PUT', parser_url,
                            {"Accept": "application/json"},
                            body=data)


def save_dataset_from_query(request, owner, name, sql, description, is_public):
    url = '/v3/db/dataset/%s/%s' % (quote(owner), quote(name))

    data = {
        "sql_code": sql,
        "is_public": is_public,
        "is_snapshot": False,
        "description": description,
    }

    response = send_request(request, 'PUT', url,
                            {"Accept": "application/json"},
                            json.dumps(data))

    data = json.loads(response.content)

    return data


def enqueue_sql_statement(request, sql):
    """
    Starts a query.  Asynchronous method.
    """
    url = '/v3/db/query'

    data = {
        "sql": sql,
    }

    response = send_request(request, 'POST', url,
                            {"Accept": "application/json"},
                            json.dumps(data))

    data = json.loads(response.content)

    return data


def get_recent_queries(request):
    """
    Get the list of queries for the current user
    """
    url = '/v3/db/query'

    response = send_request(request, 'GET', url)

    data = json.loads(response.content)

    for query in data:
        url = query["url"]
        query_id = re.match("/v3/db/query/([0-9]+)", url).group(1)
        query["query_id"] = query_id

    return data


def cancel_query_by_id(request, query_id):
    """ Cancel a running query """
    url = '/v3/db/query/%s' % query_id

    response = send_request(request, 'DELETE', url)


def get_query_data(request, query_id):
    """
    Get the status of a running or finished query, by query id.  The query id
    comes from the data in enqueue_sql_statement.
    """
    url = '/v3/db/query/%s' % query_id

    response = send_request(request, 'GET', url)

    data = json.loads(response.content)
    if "error" in data:
        data["sample_data_error"] = data["error"]
    return data


def get_user_search_results(request, term):
    response = send_request(request, 'GET', '/v3/users?q=%s' % (term),
                            {"Accept": "application/json"})

    data = json.loads(response.content)
    return data


def update_dataset_permissions(request, dataset, accounts):
    url = '/v3/db/dataset/%s/%s/permissions' % (quote(dataset["owner"]),
                                                quote(dataset["name"]))

    data = json.dumps({"authlist": accounts})
    response = send_request(request, 'PUT', url,
                            {"Accept": "application/json"},
                            body=data)


def get_dataset_permissions(request, dataset):
    url = '/v3/db/dataset/%s/%s/permissions' % (quote(dataset["owner"]),
                                                quote(dataset["name"]))

    response = send_request(request, 'GET', url,
                            {"Accept": "application/json"})

    data = json.loads(response.content)

    accounts = []

    for email in data["emails"]:
        accounts.append(email)

    for account in data["accounts"]:
        accounts.append(account["login"])

    accounts.sort()
    return accounts


def get_download_token_for_query(request, query_id):
    """
    Get a single use download token for a given query id
    """
    url = '/v3/db/query/%s/download' % query_id

    response = send_request(request, 'POST', url)

    return json.loads(response.content)
