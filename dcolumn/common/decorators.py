# -*- coding: utf-8 -*-
#
# dcolumn/common/decorators.py
#

"""
Dynamic Column decorators.

by: Carl J. Nobile

email: carl.nobile@gmail.com
"""
__docformat__ = "restructuredtext en"

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required

from dcolumn.dcolumns.manager import dcolumn_manager


def dcolumn_login_required(function=None,
                           redirect_field_name=REDIRECT_FIELD_NAME,
                           login_url=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.

    :param function: The function or method to decorate.
    :type function: Function or method
    :param redirect_field_name: See `Django Docs <https://docs.djangoproject.com/en/1.9/topics/auth/default/#django.contrib.auth.decorators.login_required>`_.
    :type redirect_field_name: str
    :param login_url: Optional URL to login through.
    :type login_url: str
    :rtype: The results from ``login_required``'
    """
    if dcolumn_manager.api_auth_state:
        return function

    return login_required(function, redirect_field_name=redirect_field_name,
                          login_url=login_url)
