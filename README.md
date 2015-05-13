SQLSHARE WEB
============

This README documents whatever steps are necessary to get your application up and running.

## Installing the application ##

**Create a virtualenv for your project**
    
    $ virutualenv yourenv
    $ cd yourenv
    $ source bin/activate
    
**Install Sqlshare Web**  
    
    $ (yourenv) pip install -e git+https://github.com/uw-it-aca/sqlshare/#egg=sqlshare-web

**Create an empty Django project**
    
    $ (yourenv) django-admin.py startproject yourproj .
    $ (yourenv) cd yourproj
    
**Update your urls.py**
    
    urlpatterns = patterns('',
        ...
        url(r'^', include('sqlshare_web.urls')),
    )
    
**Update your settings.py**
    
    from django_mobileesp.detector import mobileesp_agent as agent
    
    DETECT_USER_AGENTS = {
        'is_tablet' : agent.detectTierTablet,
        'is_mobile': agent.detectMobileQuick,
    }

    INSTALLED_APPS = (
        ...
        'compressor',
        'templatetag_handlebars',
        'sqlshare_web',
    )
    
    TEMPLATES = [
        {
            ...
            'OPTIONS': {
                'context_processors': [
                    ...
                    'sqlshare_web.context_processors.less_compiled',
                    'sqlshare_web.context_processors.google_analytics',
                ]
            }
        }
    ]

    STATICFILES_FINDERS = (
        "django.contrib.staticfiles.finders.FileSystemFinder",
        "django.contrib.staticfiles.finders.AppDirectoriesFinder",
        'compressor.finders.CompressorFinder',
    )

    COMPRESS_ROOT = "/tmp/some/path/for/files"
    COMPRESS_PRECOMPILERS = (('text/less', 'lessc {infile} {outfile}'),)
    COMPRESS_ENABLED = False # True if you want to compress your development build
    COMPRESS_OFFLINE = False # True if you want to compress your build offline
    COMPRESS_OUTPUT_DIR = ''
    COMPRESS_CSS_FILTERS = [
        'compressor.filters.css_default.CssAbsoluteFilter',
        'compressor.filters.cssmin.CSSMinFilter'
    ]
    COMPRESS_JS_FILTERS = [
        'compressor.filters.jsmin.JSMinFilter',
    ]

**Create your database**
    $ (yourenv) python manage.py syncdb

**Run your server:**
    
    $ (yourenv) python manage.py runserver 0:8000
    
    
**It worked!** 
    
    You should see the Django server running when viewing http://localhost:8000
