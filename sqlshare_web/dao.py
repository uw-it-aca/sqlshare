from sqlshare_web.utils import send_request
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
