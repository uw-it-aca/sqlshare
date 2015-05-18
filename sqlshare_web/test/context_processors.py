from sqlshare_web.context_processors import google_analytics, less_compiled
from django.test import TestCase


class TestContextProcessors(TestCase):
    def test_less_compiled(self):
        with self.settings(COMPRESS_PRECOMPILERS=None):
            self.assertEquals(less_compiled({}), { 'less_compiled': False })

        with self.settings(COMPRESS_PRECOMPILERS=()):
            self.assertEquals(less_compiled({}), { 'less_compiled': False })

        with self.settings(COMPRESS_PRECOMPILERS=(('text/other', 'whatwhat {infile} {outfile}'),)):
            self.assertEquals(less_compiled({}), { 'less_compiled': False })

        with self.settings(COMPRESS_PRECOMPILERS=(('text/other', 'whatwhat {infile} {outfile}'), ('text/less', 'lessc {infile} {outfile}'))):
            self.assertEquals(less_compiled({}), { 'less_compiled': True})


    def test_ga(self):
        with self.settings(GOOGLE_ANALYTICS_KEY=None):
            self.assertEquals(google_analytics({}), { 'GOOGLE_ANALYTICS_KEY': None, 'google_analytics': None })

        with self.settings(GOOGLE_ANALYTICS_KEY="ga_1234"):
            self.assertEquals(google_analytics({}), { 'GOOGLE_ANALYTICS_KEY': "ga_1234", 'google_analytics': "ga_1234"})
