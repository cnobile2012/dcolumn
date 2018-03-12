# -*- coding: utf-8 -*-
#
# dcolumn/common/decorators.py
#

"""
Dynamic Column decorators.
"""
__docformat__ = "restructuredtext en"

import inspect

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required

from dcolumn.dcolumns.manager import dcolumn_manager


def dcolumn_login_required(function=None,
                           redirect_field_name=REDIRECT_FIELD_NAME,
                           login_url=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary. Authentication on the API can be turned
    on or off depending on the ``settings.DYNAMIC_COLUMNS[
    'INACTIVATE_API_AUTH' ]`` state.

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


#
# InspectChoice
#
class InspectChoice(object):
    """
    This class does introspection on a non-model ``CHOICE`` object and
    supplies a decorator for the choice manager mixin. It should not be
    necessary to use this class outside of DColumns itself.
    """

    def __init__(self):
        self._path, self._caller_name = self._caller_info(skip=4)

    def _caller_info(self, skip=2):
        """
        Get a name of a caller in the format module.class.method.

        :param skip: Specifies how many levels of stack to skip while getting
                     caller name. skip=1 means 'who calls me', skip=2 'who
                     calls my caller' etc.
        :type skip: int
        :rtype: A list or empty string

        An empty string is returned if skipped levels exceed stack height.

        See: https://gist.github.com/techtonik/2151727
        """
        stack = inspect.stack()
        start = 0 + skip

        if len(stack) < start + 1: # pragma: no cover
            return ''

        parentframe = stack[start][0]
        name_list = []
        module = inspect.getmodule(parentframe)
        # `modname` can be None when frame is executed directly in console
        # TODO(techtonik): consider using __main__

        if module:
            name_list.append(module.__name__)

        # detect classname
        if 'self' in parentframe.f_locals: # pragma: no cover
            # I don't know any way to detect a call from the object method
            # XXX: there seems to be no way to detect a static method call--it
            # will be just a function call.
            name_list.append(parentframe.f_locals['self'].__class__.__name__)

        codename = parentframe.f_code.co_name

        if codename != '<module>':  # top level usually
            name_list.append( codename ) # function or a method

        del parentframe
        #log.debug("name_list: %s", name_list)
        return name_list

    @classmethod
    def set_model(self, method):
        """
        A decorator to set the choices model object of the calling class in
        the manager.

        :param method: The method name to be decorated.
        :type method: str
        :rtype: The enclosed function embedded in this method.
        """
        def wrapper(this, *args, **kwargs):
            modules = __import__(
                this._path, globals=globals(), locals=locals(),
                fromlist=(this._caller_name,), level=0)
            this.model = getattr(modules, this._caller_name)
            return method(this, *args, **kwargs)

        # Make the wrapper look like the decorated method.
        wrapper.__name__ = method.__name__
        wrapper.__dict__ = method.__dict__
        wrapper.__doc__ = method.__doc__
        return wrapper
