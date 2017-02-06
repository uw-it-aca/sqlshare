from django.test import TestCase
from django.core.urlresolvers import reverse
from sqlshare_web.test.view import run_view_tests, login
import unittest
import calendar
import time
import re
from django.test import Client


@unittest.skipUnless(run_view_tests(), "Requires ENV")
class TestQueryView(TestCase):
    def setUp(self):
        self.client = Client()
        login(self.client, "new_query_user")

    def test_login_required(self):
        response = self.client.get(reverse("new_query"))

        view_context = response.context[-1]
        self.assertEquals(view_context["user"]["username"], "new_query_user")
        self.assertEquals(response.templates[0].name, "sqlshare_web/query/run.html")


    def test_save_query_flow(self):
        response = self.client.post(reverse("new_query"),
                                    { "sql": "select (1)" })


        view_context = response.context[-1]
        self.assertEquals(view_context["user"]["username"], "new_query_user")
        self.assertEquals(view_context["sql"], "select (1)")
        self.assertEquals(view_context["errors"], {})
        self.assertEquals(response.templates[0].name, "sqlshare_web/query/name.html")

        response = self.client.post(reverse("new_query"),
                                    { "sql": "select (1)",
                                      "save": "1",
                                    })

        view_context = response.context[-1]
        self.assertTrue(view_context["errors"]["name"])

        response = self.client.post(reverse("new_query"),
                                    { "save": "1"})

        view_context = response.context[-1]
        self.assertFalse(view_context["is_public"])


        response = self.client.post(reverse("new_query"),
                                    { "save": "1",
                                      "is_public": "1"})

        view_context = response.context[-1]
        self.assertTrue(view_context["is_public"])
        self.assertTrue(view_context["errors"]["name"])
        self.assertTrue(view_context["errors"]["sql"])

        name = "test_save_%s" % calendar.timegm(time.gmtime())

        response = self.client.post(reverse("new_query"),
                                    { "save": "1",
                                      "name": name,
                                      "sql": "SELECT (1)",
                                      "description": "Testing creation"})

        self.assertRedirects(response, reverse("dataset_detail", kwargs={"owner": "new_query_user", "name": name }))

    def test_running_query(self):
        response = self.client.post(reverse("run_query"),
                                    {"sql": "select (22)" })

        location = response["Location"]
        self.assertTrue(re.match(".*/query/[\d]+$", location))

        time.sleep(1)
        response = self.client.get(location)

        self.assertEquals(response.templates[0].name, "sqlshare_web/query/results.html")


        response = self.client.post(reverse("run_query"),
                                    {"sql": "select SLEEP(2)" })

        location = response["Location"]
        self.assertTrue(re.match(".*/query/[\d]+$", location))

        time.sleep(1)
        response = self.client.get(location)
        self.assertEquals(response.status_code, 202)

        # Make sure we have a location, even if our user-agent automatically redirects
        self.assertEquals(response["Location"], location)

        time.sleep(3)
        response = self.client.get(location)
        self.assertEquals(response.status_code, 200)

        response = self.client.post(reverse("run_query"),
                                    {"sql": "select (22" })

        location = response["Location"]
        self.assertTrue(re.match(".*/query/[\d]+$", location))

        time.sleep(1)
        response = self.client.get(location)

        self.assertEquals(response.templates[0].name, "sqlshare_web/query/error.html")

