from django.conf import settings
from sanction import Client, transport_headers
from urllib2 import urlopen, HTTPError
from django.http import HttpResponseRedirect
import hashlib
import json
import os


class MockResponse(object):
    """
    To help the transition from pre-oauth connections to the new
    urlopen approach
    """
    def __init__(self, status_code, data, headers):
        self.status = status_code
        self.content = data
        self.headers = headers

    def read(self):
        return self.content

    def getheaders(self):
        return self.headers


class OAuthNeededException(Exception):
    def __init__(self, redirect):
        self.redirect = redirect


def _get_sqlshare_host():
    full_host = 'https://rest.sqlshare.uw.edu'
    if hasattr(settings, "SQLSHARE_REST_HOST"):
        full_host = settings.SQLSHARE_REST_HOST
    return full_host


def get_or_create_user(request):
    response = send_request(request, 'GET', '/v3/user/me',
                            {"Accept": "application/json"})

    code = response.status
    content = response.read()

    data = json.loads(content)

    return data


def get_oauth_client():
    backend_host = _get_sqlshare_host()
    auth_endpoint = "%s/o/authorize/" % backend_host
    token_endpoint = "%s/o/token/" % backend_host
    resource_endpoint = "%s/v3" % backend_host

    return Client(auth_endpoint=auth_endpoint,
                  token_endpoint=token_endpoint,
                  resource_endpoint=resource_endpoint,
                  client_id=settings.SQLSHARE_OAUTH_ID,
                  client_secret=settings.SQLSHARE_OAUTH_SECRET,
                  token_transport=transport_headers)


def oauth_authorize():
    c = get_oauth_client()

    response = HttpResponseRedirect(c.auth_uri())
    return response


def oauth_access_token(request):
    c = get_oauth_client()

    redirect_uri = "%s/oauth" % settings.SQLSHARE_WEB_HOST

    token_request_data = {
        'code': request.GET['code'],
        'redirect_uri': redirect_uri,
    }

    c.request_token(**token_request_data)

    request.session['sqlshare_access_token'] = c.access_token
    request.session['sqlshare_refresh_access_token'] = c.refresh_token

    if 'sqlshare_post_oauth_redirect' in request.session:
        redirect = request.session['sqlshare_post_oauth_redirect']
        response = HttpResponseRedirect(redirect)
    else:
        response = HttpResponseRedirect("%s" % settings.SQLSHARE_WEB_HOST)

    return response


def send_request(request, method, url, headers={}, body=None,
                 is_reauth_attempt=False):
    # If we don't have an access token in our session, we need to get the
    # user to auth through the backend server
    if not request.session.get("sqlshare_access_token", None):
        raise OAuthNeededException(oauth_authorize())

    client = get_oauth_client()
    client.access_token = request.session.get("sqlshare_access_token", None)

    # sanction makes too many assumptions about what we're up to, so pulling
    # their request method's content out into here.
    backend_host = _get_sqlshare_host()
    req = client.token_transport('{0}{1}'.format(backend_host, url),
                                 client.access_token, data=body, method=method,
                                 headers=headers)

    try:
        resp = urlopen(req)
    except HTTPError as e:
        resp = e

    body = resp.read()
    if resp.getcode() == 403:
        if body.find("SQLShare: Access Denied") < 0:
            # Without the SQLShare error, assume an oauth issue.
            if not is_reauth_attempt:
                c = get_oauth_client()
                refresh = request.session["sqlshare_refresh_access_token"]

                c.request_token(grant_type='refresh_token',
                                refresh_token=refresh)

                request.session["sqlshare_access_token"] = c.access_token
                refresh = c.refresh_token
                request.session["sqlshare_refresh_access_token"] = refresh
                return send_request(request, method, url, headers, body,
                                    is_reauth_attempt=True)

    headers = {}
    all_headers = resp.info()
    for header in all_headers:
        if "set-cookie" == header:
            next
        if "vary" == header:
            next
        if "server" == header:
            next

        headers[header] = all_headers[header]

    return MockResponse(resp.getcode(), body, headers)


<<<<<<< HEAD
def build_download_url(query_id, token):
    host = getattr(settings, "SQLSHARE_REST_HOST", None)
    api_uri = getattr(settings, "SQLSHARE_DOWNLOAD_API", "/v3/db/query/")
    return host + api_uri + query_id + "/download/" + token
=======
def get_file_path(username, file_name, chunk):
    return os.path.join(settings.SQLSHARE_FILE_CHUNK_PATH,
                        username,
                        hashlib.md5(file_name).hexdigest(),
                        chunk)
>>>>>>> cce1ad95c13615070d88fb4bd0b0935ce6b2a1c3
