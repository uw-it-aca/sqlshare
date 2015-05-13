SQLSHARE WEB
============

This README documents whatever steps are necessary to get your application up and running.

## Installing the application ##

**Create a virtualenv for your project**
    
    $ virutualenv yourenv
    $ cd yourenv
    $ source bin/activate

**Create an empty Django project**
    
    $ (yourenv) pip install django
    $ (yourenv) django-admin.py startproject yourproj
    $ (yourenv) cd yourproj
    
**Install Sqlshare Web**  
    
    $ (yourenv) pip install -e git+https://github.com/uw-it-aca/sqlshare/#egg=aca-sqlshare-web
    
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
    
    TEMPLATE_CONTEXT_PROCESSORS = (
        ...
        'sqlshare_web.context_processors.less_compiled',
        'sqlshare_web.context_processors.google_analytics',
        'sqlshare_web.context_processors.devtools_bar',
    )
    
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
      
**Run your server:**
    
    $ (yourenv) python manage.py runserver 0:8000
    
    
**It worked!** 
    
    You should see the Django server running when viewing http://localhost:8000
