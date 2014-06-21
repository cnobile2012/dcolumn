#
# dcolumn/common/admin_mixins.py
#

import datetime

from django.contrib import admin


class UserAdminMixin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if change is False:
            obj.creator = request.user

        obj.user = request.user

        # Just in case an external import was done.
        # (A migration where a ctime didn't exist.)
        if obj.ctime is None:
            obj.ctime = datetime.datetime.now()

        super(UserAdminMixin, self).save_model(request, obj, form, change)
