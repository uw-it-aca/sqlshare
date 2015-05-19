import os
from django.core.urlresolvers import reverse
import base64
import re

import six

if six.PY2:
    from urllib2 import HTTPError
if six.PY3:
    from urllib.error import HTTPError


def run_view_tests():
    return os.environ.get("RUN_SQLSHARE_VIEW_TESTS", False)


def login(client, username):
    if 'sqlshare_access_token' in client.session:
        del client.session['sqlshare_access_token']

    if 'sqlshare_refresh_access_token' in client.session:
        del client.session['sqlshare_refresh_access_token']

    response = client.get(reverse('dataset_list'))

    location = response["Location"]

    import mechanize

    browser = mechanize.Browser()
    browser.set_handle_robots(False)
    base64string = base64.encodestring('%s:%s' % (username, "ok"))
    browser.add_password(location, username, "ok", "Development")

    browser.open(location)

    browser.select_form(nr=0)
    browser.set_handle_redirect(False)
    try:
        browser.submit(label="Authorize")
    except HTTPError as ex:
        location = ex.hdrs["Location"]
        print("Location: %s", location)

        local = re.match(".*(/oauth.*)", location).groups()[0]

        response = client.get(local)

        if response.status_code == 301:
            location = response["Location"]
            response = client.get(location)
