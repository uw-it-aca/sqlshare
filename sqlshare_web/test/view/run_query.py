from django.test import TestCase
from django.core.urlresolvers import reverse
from sqlshare_web.test.view import run_view_tests, login
import unittest
import calendar
import time
from django.test import Client


@unittest.skipUnless(run_view_tests(), "Requires ENV")
class TestQueryView(TestCase):
    def setUp(self):
        self.client = Client()
        login(self.client, "new_query_user")

    def test_login_required(self):
        response = self.client.get(reverse("sqlshare_web.views.new_query"))

        view_context = response.context[-1]
        self.assertEquals(view_context["user"]["username"], "new_query_user")
        self.assertEquals(response.templates[0].name, "sqlshare_web/query/run.html")


    def test_save_query_flow(self):
        response = self.client.post(reverse("sqlshare_web.views.new_query"),
                                    { "sql": "select (1)" })


        view_context = response.context[-1]
        self.assertEquals(view_context["user"]["username"], "new_query_user")
        self.assertEquals(view_context["sql"], "select (1)")
        self.assertEquals(view_context["errors"], {})
        self.assertEquals(response.templates[0].name, "sqlshare_web/query/name.html")

        response = self.client.post(reverse("sqlshare_web.views.new_query"),
                                    { "sql": "select (1)",
                                      "save": "1",
                                    })

        view_context = response.context[-1]
        self.assertTrue(view_context["errors"]["name"])

        response = self.client.post(reverse("sqlshare_web.views.new_query"),
                                    { "save": "1", })

        view_context = response.context[-1]
        self.assertTrue(view_context["errors"]["name"])
        self.assertTrue(view_context["errors"]["sql"])

        name = "test_save_%s" % calendar.timegm(time.gmtime())

        response = self.client.post(reverse("sqlshare_web.views.new_query"),
                                    { "save": "1",
                                      "name": name,
                                      "sql": "SELECT (1)",
                                      "description": "Testing creation"})

        self.assertRedirects(response, reverse("dataset_detail", kwargs={"owner": "new_query_user", "name": name }))
