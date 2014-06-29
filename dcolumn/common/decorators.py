#
# dcolumn/common/decorators.py
#

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required

from dcolumn.dcolumns.manager import dcolumn_manager


def dcolumn_login_required(function=None,
                           redirect_field_name=REDIRECT_FIELD_NAME,
                           login_url=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    if dcolumn_manager.get_api_auth_state():
        return function

    return login_required(function, redirect_field_name=redirect_field_name,
                          login_url=login_url)
