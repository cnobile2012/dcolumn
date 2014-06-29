#
# dcolumn/dcolumns/admin.py
#

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import DynamicColumn, KeyValueMixin, ColumnCollection
from .forms import DynamicColumnForm, ColumnCollectionForm
from dcolumn.common.admin_mixins import UserAdminMixin


#
# KeyValueInlineMixin
#
class KeyValueInlineMixin(object):
    extra = 0
    fieldsets = (
        (None, {'fields': ('dynamic_column', 'value',)}),
        )

    class Media:
        js = ('dcolumn/js/jquery-2.0.3.min.js', 'dcolumn/js/jquery.cookie.js',
              'dcolumn/js/inheritance.js', 'dcolumn/js/dynamic-column.js',)


#
# ColumnCollection
#
class ColumnCollectionAdmin(UserAdminMixin):
    fieldsets = (
        (None, {'fields': ('name', 'dynamic_column',)}),
        (_('Status'), {'classes': ('collapse',),
                       'fields': ('active', 'user', 'ctime', 'mtime',)}),
        )
    readonly_fields = ('user', 'ctime', 'mtime',)
    list_display = ('name', 'user', 'mtime',)
    filter_horizontal = ('dynamic_column',)
    form = ColumnCollectionForm


#
# DynamicColumn
#
class DynamicColumnAdmin(UserAdminMixin):
    fieldsets = (
        (None, {'fields': ('name', 'value_type', 'relation', 'store_relation',
                           'required',)}),
        (_('Screen Location'), {'fields': ('location', 'order',)}),
        (_('Status'), {'classes': ('collapse',),
                       'fields': ('slug', 'active', 'creator', 'ctime', 'user',
                                  'mtime',)}),
        )
    readonly_fields = ('creator', 'slug', 'user', 'ctime', 'mtime',)
    list_display = ('name', 'value_type', '_relation_producer',
                    'store_relation', 'required', 'location', 'order',
                    'mtime', 'active',)
    list_editable = ('location', 'order', 'active',)
    ordering = ('location', 'order', 'name',)
    form = DynamicColumnForm


admin.site.register(ColumnCollection, ColumnCollectionAdmin)
admin.site.register(DynamicColumn, DynamicColumnAdmin)
