# -*- coding: utf-8 -*-
from django.template.response import TemplateResponse
from django.contrib.sites.models import get_current_site


def default(request):
    site = get_current_site(request)
    print "SITE", site
    return TemplateResponse(
        request,
        'todos/default.html',
        dict(request=request, ))
