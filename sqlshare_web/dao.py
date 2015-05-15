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

    data = json.loads(response.content)

    return data


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


def update_parser_values(request, user, filename, delimiter, has_header_row):
    session_key = "ss_file_id_%s" % filename
    upload_id = request.session[session_key]

    parser_url = '/v3/db/file/%s/parser' % (upload_id)

    data = json.dumps({"parser": {"delimiter": delimiter,
                                  "has_column_header": has_header_row}})

    response = send_request(request, 'PUT', parser_url,
                            {"Accept": "application/json"},
                            body=data)
