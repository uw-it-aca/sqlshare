from django.test import TestCase
from django.core.urlresolvers import reverse
from sqlshare_web.test.view import run_view_tests, login
import unittest
from django.test import Client


@unittest.skipUnless(run_view_tests(), "Requires ENV")
class TestQueryView(TestCase):
    def setUp(self):
        self.client = Client()
        login(self.client, "run_query")

    def test_login_required(self):
        response = self.client.get(reverse("sqlshare_web.views.new_query"))

        view_context = response.context[-1]

        self.assertEquals(view_context["user"]["username"], "run_query")
