# coding: utf-8

# imports
import re

# django imports
from django import template
from django.contrib.contenttypes.models import ContentType
from django.contrib import admin
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

# grappelli imports
from grappelli_safe.settings import *

register = template.Library()

@register.filter
def use_grappelli_media(media):
    html = []
    for attr in ("render_js", "render_css"):
        for f in getattr(media, attr)():
            f = f.replace(settings.STATIC_URL + "admin/",
                          settings.ADMIN_MEDIA_PREFIX, 1)
            html.append(f)
    return mark_safe("\n".join(html))


# SEARCH FIELDS VERBOSE
class GetSearchFields(template.Node):

    def __init__(self, opts, var_name):
        self.opts = template.Variable(opts)
        self.var_name = var_name

    def render(self, context):
        opts = str(self.opts.resolve(context)).split('.')
        model = models.get_model(opts[0], opts[1])
        try:
            field_list = admin.site._registry[model].search_fields_verbose
        except:
            field_list = ""

        context[self.var_name] = ", ".join(field_list)
        return ""


def do_get_search_fields_verbose(parser, token):
    """
    Get search_fields_verbose in order to display on the Changelist.
    """

    try:
        tag, arg = token.contents.split(None, 1)
    except:
        raise template.TemplateSyntaxError, "%s tag requires arguments" % token.contents.split()[0]
    m = re.search(r'(.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%r tag had invalid arguments" % tag
    opts, var_name = m.groups()
    return GetSearchFields(opts, var_name)

register.tag('get_search_fields_verbose', do_get_search_fields_verbose)


# ADMIN_TITLE
def get_admin_title():
    """
    Returns the Title for the Admin-Interface.
    """

    return ADMIN_TITLE

register.simple_tag(get_admin_title)


# ADMIN_URL
def get_admin_url():
    """
    Returns the URL for the Admin-Interface.
    """

    return ADMIN_URL

register.simple_tag(get_admin_url)


# GRAPPELLI MESSAGING SYSTEM
def get_messages(session):
    """
    Get Success and Error Messages.
    """

    try:
        msg = session['grappelli']['message']
        del session['grappelli']['message']
        session.modified = True
    except:
        msg = ""

    return {
        'message': msg
    }

register.inclusion_tag('admin/includes_grappelli/messages.html')(get_messages)


