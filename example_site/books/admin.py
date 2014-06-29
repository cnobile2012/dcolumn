#
# example_site/books/admin.py
#

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from dcolumn.dcolumns.admin import KeyValueInlineMixin
from dcolumn.common.admin_mixins import UserAdminMixin

from .forms import BookForm, ParentForm, KeyValueForm


#
# KeyValue
#
class KeyValueInline(KeyValueInlineMixin, admin.TabularInline):
    model = KeyValue
    extra = 0
    fieldsets = (
        (None, {'fields': ('dynamic_column', 'value',)}),
        )
    form = KeyValueForm
    ordering = ('parent',)


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
# Parent
#
class ParentAdmin(UserAdminMixin):
    fieldsets = (
        (None, {'fields': ('name', 'column_collection',)}),
        (_('Status'), {'classes': ('collapse',),
                       'fields': ('active', 'creator', 'user', 'ctime',
                                  'mtime',)}),
        )
    readonly_fields = ('creator', 'user', 'ctime', 'mtime',)
    list_display = ('name', 'column_collection', 'creator', 'ctime', 'mtime',
                    'active', '_detail_producer',)
    list_editable = ('active',)
    ordering = ('name', 'creator__username', 'active',)
    list_filter = ('active', 'name', 'creator',)
    inlines = (KeyValueInline,)
    form = ParentForm


admin.site.register(Book, BookAdmin)
admin.site.register(Parent, ParentAdmin)
