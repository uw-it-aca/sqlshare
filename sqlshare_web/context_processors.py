from django.conf import settings


def less_compiled(request):
    """ See if django-compressor is being used to precompile less
    """
    key = getattr(settings, "COMPRESS_PRECOMPILERS", ())
    if not key:
        return {'less_compiled': False}
    for compiler in key:
        if compiler[0] == "text/less":
            return {'less_compiled':  True}

    return {'less_compiled': False}


def google_analytics(request):

    ga_key = getattr(settings, 'GOOGLE_ANALYTICS_KEY', False)
    return {
        'GOOGLE_ANALYTICS_KEY': ga_key,
        'google_analytics': ga_key
    }
