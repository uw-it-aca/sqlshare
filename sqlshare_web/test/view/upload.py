from django.test import TestCase
from django.core.urlresolvers import reverse
from sqlshare_web.test.view import run_view_tests, login
import unittest
from django.test import Client
import six

if six.PY2:
    from StringIO import StringIO
elif six.PY3:
    from io import StringIO


@unittest.skipUnless(run_view_tests(), "Requires ENV")
class TestUploads(TestCase):
    def setUp(self):
        self.client = Client()
        login(self.client, "upload_file_user")


    def test_upload(self):
        response = self.client.get(reverse("sqlshare_web.views.dataset_upload"))

        view_context = response.context[-1]
        self.assertEquals(view_context["user"]["username"], "upload_file_user")
        self.assertEquals(response.templates[0].name, "sqlshare_web/upload.html")

        response = self.client.get(reverse("dataset_upload_chunk"), {
            "resumableChunkNumber": 1,
            "resumableTotalChunks": 1,
            "resumableFilename": "test_upload.csv",
        })

        self.assertEquals(response.status_code, 404)

        file_handle = StringIO("a,b,c,d\n1,2,3,4\n5,6,7,8")

        response = self.client.post(reverse("dataset_upload_chunk"), {
            "resumableChunkNumber": 1,
            "resumableTotalChunks": 1,
            "resumableFilename": "test_upload.csv",
            "file": file_handle
        })

        self.assertEquals(response.status_code, 200)

        # Test that resumable is working properly
        response = self.client.get(reverse("dataset_upload_chunk"), {
            "resumableChunkNumber": 1,
            "resumableTotalChunks": 1,
            "resumableFilename": "test_upload.csv",
        })

        self.assertEquals(response.status_code, 200)

        # Test that some random other user doesn't see that progress
        c2 = Client()
        login(c2, "rando_upload")

        response = c2.get(reverse("dataset_upload_chunk"), {
            "resumableChunkNumber": 1,
            "resumableTotalChunks": 1,
            "resumableFilename": "test_upload.csv",
        })

        self.assertEquals(response.status_code, 404)
