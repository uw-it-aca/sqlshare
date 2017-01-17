"""
Django settings for project project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '7-mearp412z5m^oztw(cjf$#=1kpel9%$5w6yu-ax_^#-f#x2v'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

GOOGLE_OAUTH2_CLIENT_ID = ''
GOOGLE_OAUTH2_CLIENT_SECRET = ''

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'oauth2_provider',
    'sqlshare_rest',
)

from django.http import HttpResponse
import os
class BadIdeaMiddleware(object):

    def unauthed(self):
        response = HttpResponse("""<html><title>Auth required</title><body>
                                <h1>Authorization Required</h1></body></html>""", content_type="text/html")
        response['WWW-Authenticate'] = 'Basic realm="Development"'
        response.status_code = 401
        return response

    def process_request(self,request):
        import base64

        if request.path.startswith("/o/token"):
            return None
        if request.path.startswith("/v3"):
            return None

        if not 'HTTP_AUTHORIZATION' in request.META:
        #if not request.META.in('HTTP_AUTHORIZATION'):
            return self.unauthed()
        else:
            try:
                authentication = request.META['HTTP_AUTHORIZATION']
                (authmeth, auth) = authentication.split(' ',1)
                if 'basic' != authmeth.lower():
                    return self.unauthed()
                auth = base64.b64decode(auth.strip()).decode('utf-8')
                #auth = auth.strip().decode('base64')
                username, password = auth.split(':',1)

                request.META["REMOTE_USER"] = username
                return None
            except Exception as ex:
                print ("Ex: ", ex)
                raise

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'project.settings.BadIdeaMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)


AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.RemoteUserBackend',
)

ROOT_URLCONF = 'project.urls'

WSGI_APPLICATION = 'project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': "sqlshare_rest_app",
        'USER': 'ss_rest_user',
        'HOST': 'localhost',
        'PASSWORD': 'ss_pass',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
