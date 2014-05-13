from django import template
from django.core.urlresolvers import reverse

register = template.Library()

from connect.rp.forms import AuthReqForm

@register.assignment_tag(takes_context=True)
def authreq_form(context):

    return AuthReqForm(vender=None)
