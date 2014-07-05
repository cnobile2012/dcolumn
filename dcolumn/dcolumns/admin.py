#
# dcolumn/dcolumns/admin.py
#

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from dcolumn.common.admin_mixins import UserAdminMixin

from .models import DynamicColumn, ColumnCollection, KeyValue
from .forms import DynamicColumnForm, ColumnCollectionForm, KeyValueForm


#
# KeyValue
#
class KeyValueInline(admin.TabularInline):
    fieldsets = (
        (None, {'fields': ('dynamic_column', 'value',)}),
        )
    ordering = ('dynamic_column__location', 'dynamic_column__order',)
    extra = 0
    model = KeyValue
    form = KeyValueForm

    class Media:
        js = ('dcolumn/js/jquery-1.11.1.min.js', 'dcolumn/js/jquery.cookie.js',
              'dcolumn/js/inheritance.js', 'dcolumn/js/dynamic-column.js',)


#
# ColumnCollection
#
class ColumnCollectionAdmin(UserAdminMixin):
    fieldsets = (
        (None, {'fields': ('name', 'dynamic_column',)}),
        (_('Status'), {'classes': ('collapse',),
                       'fields': ('active', 'creator', 'ctime', 'user',
                                  'mtime',)}),
        )
    readonly_fields = ('creator', 'ctime', 'user', 'mtime',)
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
    list_display = ('name', '_collection_producer', 'value_type',
                    '_relation_producer', 'store_relation', 'required',
                    'location', 'order', 'mtime', 'active',)
    list_editable = ('location', 'order', 'active',)
    ordering = ('column_collection__name', 'location', 'order', 'name',)
    form = DynamicColumnForm


admin.site.register(ColumnCollection, ColumnCollectionAdmin)
admin.site.register(DynamicColumn, DynamicColumnAdmin)
