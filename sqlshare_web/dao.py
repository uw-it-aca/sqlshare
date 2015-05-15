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
