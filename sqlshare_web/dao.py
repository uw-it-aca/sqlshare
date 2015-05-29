from sqlshare_web.utils import send_request, get_file_path
from urllib import quote
import json


def get_datasets(request):
    response = send_request(request, 'GET', '/v3/db/dataset/all',
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


def get_query_data(request, query_id):
    """
    Get the status of a running or finished query, by query id.  The query id
    comes from the data in enqueue_sql_statement.
    """
    url = '/v3/db/query/%s' % query_id

    response = send_request(request, 'GET', url)

    return json.loads(response.content)
