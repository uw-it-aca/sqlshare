from django.test import TestCase
from django.core.urlresolvers import reverse
from sqlshare_web.test.view import run_view_tests, login
from django.test import Client
import unittest
import random


@unittest.skipUnless(run_view_tests(), "Requires ENV")
class TestDatasetView(TestCase):
    def setUp(self):
        self.client = Client()
        login(self.client, "dataset_view_user")

    def test_valid_own(self):
        name = "test_owner_dataset"
        response = self.client.post(reverse("sqlshare_web.views.new_query"),
                                    { "save": "1",
                                      "name": name,
                                      "sql": "SELECT (44)",
                                      "description": "Testing creation"})

        response = self.client.get(reverse("dataset_detail", kwargs={"name": name, "owner": "dataset_view_user" }))

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.templates[0].name, "sqlshare_web/detail.html")
        view_context = response.context[-1]
        self.assertEquals(view_context["user"]["username"], "dataset_view_user")

        self.assertEquals(view_context["dataset"]["sql_code"], "SELECT (44)")


    def test_non_existant(self):
        name = "rando-%s" % random.random()
        response = self.client.get(reverse("dataset_detail", kwargs={"name": name, "owner": "dataset_view_user" }))

        self.assertEquals(response.status_code, 404)


    def test_rando(self):
        name = "test_not_your_dataset"
        response = self.client.post(reverse("sqlshare_web.views.new_query"),
                                    { "save": "1",
                                      "name": name,
                                      "sql": "SELECT (44)",
                                      "description": "Testing creation"})

        c2 = Client()
        login(c2, "rando")

        response = c2.get(reverse("dataset_detail", kwargs={"name": name, "owner": "dataset_view_user" }))

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.templates[0].name, "sqlshare_web/detail_no_permission.html")

    def test_rando_public(self):
        name = "test_not_your_dataset-public"
        response = self.client.post(reverse("sqlshare_web.views.new_query"),
                                    { "save": "1",
                                      "name": name,
                                      "sql": "SELECT (33)",
                                      "is_public": "1",
                                      "description": "Testing creation"})

        c2 = Client()
        login(c2, "rando")

        response = c2.get(reverse("dataset_detail", kwargs={"name": name, "owner": "dataset_view_user" }))

        self.assertEquals(response.status_code, 200)
        view_context = response.context[-1]
        self.assertEquals(view_context["user"]["username"], "rando")

        self.assertEquals(view_context["dataset"]["sql_code"], "SELECT (33)")

