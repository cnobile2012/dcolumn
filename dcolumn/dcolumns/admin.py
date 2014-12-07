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
                       'fields': ('active', 'creator', 'created', 'updater',
                                  'updated',)}),
        )
    readonly_fields = ('creator', 'created', 'updater', 'updated',)
    list_display = ('name', 'updater', 'updated',)
    filter_horizontal = ('dynamic_column',)
    form = ColumnCollectionForm

    class Media:
        js = ('dcolumn/js/jquery-1.11.1.min.js', 'dcolumn/js/inheritance.js',
              'dcolumn/js/column-collection.js',)
        css = {u'all': ('dcolumn/css/column-collection.css',)}


#
# DynamicColumn
#
class DynamicColumnAdmin(UserAdminMixin):
    fieldsets = (
        (None, {'fields': ('name', 'value_type', 'relation',
                           'store_relation',)}),
        (_('Screen Location'), {'fields': ('location', 'order', 'required',)}),
        (_('Status'), {'classes': ('collapse',),
                       'fields': ('preferred_slug', 'slug', 'active',
                                  'creator', 'created', 'updater',
                                  'updated',)}),
        )
    readonly_fields = ('creator', 'slug', 'updater', 'created', 'updated',)
    list_display = ('name', '_collection_producer', 'slug', 'value_type',
                    '_relation_producer', 'store_relation', 'required',
                    'location', 'order', 'updated', 'active',)
    list_editable = ('location', 'order', 'active',)
    ordering = ('column_collection__name', 'location', 'order', 'name',)
    form = DynamicColumnForm


admin.site.register(ColumnCollection, ColumnCollectionAdmin)
admin.site.register(DynamicColumn, DynamicColumnAdmin)
