from django.test import TestCase
from django.core.urlresolvers import reverse
from sqlshare_web.test.view import run_view_tests, login
import unittest
from django.test import Client
import time
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
            "resumableTotalChunks": 2,
            "resumableFilename": "test_upload.csv",
        })

        self.assertEquals(response.status_code, 404)

        file_handle = StringIO("a,b,c,d\n1,2,3,4\n5,6,7,8\n")

        response = self.client.post(reverse("dataset_upload_chunk"), {
            "resumableChunkNumber": 1,
            "resumableTotalChunks": 2,
            "resumableFilename": "test_upload.csv",
            "file": file_handle
        })

        self.assertEquals(response.status_code, 200)

        # Test that resumable is working properly
        response = self.client.get(reverse("dataset_upload_chunk"), {
            "resumableChunkNumber": 1,
            "resumableTotalChunks": 2,
            "resumableFilename": "test_upload.csv",
        })

        self.assertEquals(response.status_code, 200)

        # Test that some random other user doesn't see that progress
        c2 = Client()
        login(c2, "rando_upload")

        response = c2.get(reverse("dataset_upload_chunk"), {
            "resumableChunkNumber": 1,
            "resumableTotalChunks": 2,
            "resumableFilename": "test_upload.csv",
        })

        self.assertEquals(response.status_code, 404)

        file_handle = StringIO("1,2,3,4\n5,6,7,8")

        response = self.client.post(reverse("dataset_upload_chunk"), {
            "resumableChunkNumber": 2,
            "resumableTotalChunks": 2,
            "resumableFilename": "test_upload.csv",
            "file": file_handle
        })

        response = self.client.get(reverse("upload_parser", kwargs={"filename": "test_upload.csv"}))
        self.assertEquals(response.templates[0].name, "sqlshare_web/parser.html")
        view_context = response.context[-1]
        self.assertEquals(view_context["user"]["username"], "upload_file_user")

        response = c2.get(reverse("upload_parser", kwargs={"filename": "test_upload.csv"}))

        self.assertEquals(response.status_code, 404)

        # Make sure we stay on the page w/ an update...
        response = self.client.post(reverse("upload_parser", kwargs={"filename": "test_upload.csv"}), {"delimiter": "a", "has_header": False, "update_preview": True })
        self.assertEquals(response.templates[0].name, "sqlshare_web/parser.html")

        # Moving on...
        response = self.client.post(reverse("upload_parser", kwargs={"filename": "test_upload.csv"}), { "delimiter": ",", "has_header": True, "update_preview": "0"})

        self.assertRedirects(response, reverse("upload_finalize", kwargs={"filename": "test_upload.csv"}))

        response = self.client.get(reverse("upload_finalize", kwargs={"filename": "test_upload.csv"}))
        self.assertEquals(response.templates[0].name, "sqlshare_web/upload_finalize.html")
        view_context = response.context[-1]
        self.assertEquals(view_context["user"]["username"], "upload_file_user")
        self.assertEquals(view_context["filename"], "test_upload.csv")
        self.assertEquals(view_context["file_chunk_count"], '2')

        # Send off to the backend server:
        response = self.client.post(reverse('upload_finalize_process', kwargs={"filename": "test_upload.csv"}), { "chunk": "1" })
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, "next_chunk")

        response = self.client.post(reverse('upload_finalize_process', kwargs={"filename": "test_upload.csv"}), { "chunk": "2" })
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, "next_chunk")

        response = self.client.post(reverse('upload_finalize_process', kwargs={"filename": "test_upload.csv"}), { "chunk": "3" })
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, "upload_complete")

        response = self.client.post(reverse('upload_finalize_process', kwargs={"filename": "test_upload.csv"}), { "finalize": True, "dataset_name": "test_upload.csv", "dataset_description": "Desc", "is_public": True })
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, "finalizing")

        has_done = False
        for i in range(1,  10):
            time.sleep(1)
            response = self.client.get(reverse('upload_finalize_process', kwargs={"filename": "test_upload.csv"}))
            self.assertEquals(response.status_code, 200)
            if response.content == "Done":
                has_done = True
                break

        self.assertTrue(has_done)
        self.assertTrue("ss_max_chunk_test_upload.csv" not in self.client.session)
        self.assertTrue("ss_file_id_upload.csv" not in self.client.session)


        # Now, make sure we didn't leave any chunk behind:
        response = self.client.get(reverse("dataset_upload_chunk"), {
            "resumableChunkNumber": 1,
            "resumableTotalChunks": 2,
            "resumableFilename": "test_upload.csv",
        })

        self.assertEquals(response.status_code, 404)

        response = self.client.get(reverse("dataset_upload_chunk"), {
            "resumableChunkNumber": 2,
            "resumableTotalChunks": 2,
            "resumableFilename": "test_upload.csv",
        })

        self.assertEquals(response.status_code, 404)


