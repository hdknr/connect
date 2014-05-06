# -*- coding: utf-8 -*-
from django.template.response import TemplateResponse


def default(request):
    return TemplateResponse(
        request,
        'todos/default.html',
        dict(request=request, ))
