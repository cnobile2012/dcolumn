#
# dcolumn/dynamic_columns/admin.py
#

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Book, Parent, DynamicColumn, KeyValue, DynamicColumnItem
from .forms import (
    BookForm, ParentForm, DynamicColumnForm, KeyValueForm,
    DynamicColumnItemForm)
from dcolumn.common.admin_mixins import UserAdminMixin


#
# Book
#
class BookAdmin(UserAdminMixin):
    fieldsets = (
        (None, {'fields': ('title', 'author', 'publisher', 'isbn10',
                           'isbn13')}),
        (_('Status'), {'classes': ('collapse',),
                       'fields': ('active', 'user', 'ctime', 'mtime',)}),
        )
    readonly_fields = ('user', 'ctime', 'mtime',)
    list_display = ('title', 'author', 'publisher', 'user', 'mtime',)
    form = BookForm


#
# DynamicColumnItem
#
class DynamicColumnItemAdmin(UserAdminMixin):
    fieldsets = (
        (None, {'fields': ('name', 'dynamic_column',)}),
        (_('Status'), {'classes': ('collapse',),
                       'fields': ('active', 'user', 'ctime', 'mtime',)}),
        )
    readonly_fields = ('user', 'ctime', 'mtime',)
    list_display = ('name', 'user', 'mtime',)
    filter_horizontal = ('dynamic_column',)
    form = DynamicColumnItemForm


#
# KeyValue
#
class KeyValueInline(admin.TabularInline):
    model = KeyValue
    extra = 1
    fieldsets = (
        (None, {'fields': ('parent', 'dynamic_column', 'value',)}),
        )
    form = KeyValueForm
    ordering = ('parent',)

    class Media:
        js = ('js/jquery-2.0.3.min.js', 'js/jquery.cookie.js',
              'dcolumn/js/inheritance.js', 'dcolumn/js/dynamic-column.js',)


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


#
# Parent
#
class ParentAdmin(UserAdminMixin):
    fieldsets = (
        (None, {'fields': ('name', 'dynamic_column_item',)}),
        (_('Status'), {'classes': ('collapse',),
                       'fields': ('active', 'creator', 'user', 'ctime',
                                  'mtime',)}),
        )
    readonly_fields = ('creator', 'user', 'ctime', 'mtime',)
    list_display = ('name', 'dynamic_column_item', 'creator', 'ctime', 'mtime',
                    'active', '_detail_producer',)
    list_editable = ('active',)
    ordering = ('name', 'creator__username', 'active',)
    list_filter = ('active', 'name', 'creator',)
    inlines = (KeyValueInline,)
    form = ParentForm


admin.site.register(Book, BookAdmin)
admin.site.register(DynamicColumnItem, DynamicColumnItemAdmin)
admin.site.register(DynamicColumn, DynamicColumnAdmin)
admin.site.register(Parent, ParentAdmin)
