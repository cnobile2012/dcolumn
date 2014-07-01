#
# example_site/books/admin.py
#

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from dcolumn.common.admin_mixins import UserAdminMixin
from dcolumn.dcolumns.admin import KeyValueInline

from .models import Book, Author, Publisher
from .forms import BookForm, AuthorForm, PublisherForm


#
# Author
#
class AuthorAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('name',)}),
        (_('Status'), {'classes': ('collapse',),
                       'fields': ('column_collection', 'active', 'user',
                                  'ctime', 'mtime',)}),
        )
    readonly_fields = ('user', 'ctime', 'mtime',)
    list_display = ('name', 'column_collection', 'user', 'mtime',)
    inlines = (KeyValueInline,)
    form = AuthorForm


#
# Publisher
#
class PublisherAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('name',)}),
        (_('Status'), {'classes': ('collapse',),
                       'fields': ('column_collection', 'active', 'user',
                                  'ctime', 'mtime',)}),
        )
    readonly_fields = ('user', 'ctime', 'mtime',)
    list_display = ('name', 'column_collection', 'user', 'mtime',)
    inlines = (KeyValueInline,)
    form = PublisherForm


#
# Book
#
class BookAdmin(UserAdminMixin):
    fieldsets = (
        (None, {'fields': ('title',)}),
        (_('Status'), {'classes': ('collapse',),
                       'fields': ('column_collection', 'active', 'user',
                                  'ctime', 'mtime',)}),
        )
    readonly_fields = ('user', 'ctime', 'mtime',)
    list_display = ('title', 'column_collection', 'user', 'mtime',)
    inlines = (KeyValueInline,)
    form = BookForm


admin.site.register(Book, BookAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Publisher, PublisherAdmin)
