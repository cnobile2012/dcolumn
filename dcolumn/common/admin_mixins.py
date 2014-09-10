#
# dcolumn/common/admin_mixins.py
#

import datetime

from django.contrib import admin


class UserAdminMixin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if change is False:
            obj.creator = request.user

        obj.updater = request.user
        super(UserAdminMixin, self).save_model(request, obj, form, change)
