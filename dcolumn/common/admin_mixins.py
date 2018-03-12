# -*- coding: utf-8 -*-
#
# dcolumn/common/admin_mixins.py
#

"""
Mixins used in the Django admin.
"""
__docformat__ = "restructuredtext en"

import datetime

from django.contrib import admin


class UserAdminMixin(admin.ModelAdmin):
    """
    Admin mixin that must be used in any model implimented with
    CollectionBase as it's base class.
    """

    def save_model(self, request, obj, form, change):
        """
        When saving a record from the admin the `creator` should be
        updated with the request user object if `change` is `False`.
        The `updater` is always updated withthe request user object.

        :param request: Django request object.
        :type request: HttpRequest
        :param obj: Django model object
        :type obj: Model object
        :param form: Django form object.
        :type form: Form object
        :param change: If `True` the record was updated, if `False` the
                       record was created.
        :type change: bool
        """
        if change is False:
            obj.creator = request.user

        obj.updater = request.user
        super(UserAdminMixin, self).save_model(request, obj, form, change)
