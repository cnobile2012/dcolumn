#
# example_site/books/admin.py
#

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from dcolumn.common.admin_mixins import UserAdminMixin
from dcolumn.dcolumns.admin import KeyValueInline

from .models import Promotion, Book, Author, Publisher
from .forms import PromotionForm, BookForm, AuthorForm, PublisherForm


#
# Promotion
#
class PromotionAdmin(UserAdminMixin):
    fieldsets = (
        (None, {'fields': ('name',)}),
        (_('Status'), {'classes': ('collapse',),
                       'fields': ('column_collection', 'active', 'creator',
                                  'created', 'updater', 'updated',)}),
        )
    readonly_fields = ('creator', 'created', 'updater', 'updated',)
    list_display = ('name', 'column_collection', 'active', 'updater_producer',
                    'updated', 'detail_producer',)
    list_editable = ('active',)
    inlines = (KeyValueInline,)
    form = PromotionForm


#
# Author
#
class AuthorAdmin(UserAdminMixin):
    fieldsets = (
        (None, {'fields': ('name',)}),
        (_('Status'), {'classes': ('collapse',),
                       'fields': ('column_collection', 'active', 'creator',
                                  'created', 'updater', 'updated',)}),
        )
    readonly_fields = ('creator', 'created', 'updater', 'updated',)
    list_display = ('name', 'column_collection', 'updater_producer',
                    'updated', 'detail_producer',)
    inlines = (KeyValueInline,)
    form = AuthorForm


#
# Publisher
#
class PublisherAdmin(UserAdminMixin):
    fieldsets = (
        (None, {'fields': ('name',)}),
        (_('Status'), {'classes': ('collapse',),
                       'fields': ('column_collection', 'active', 'creator',
                                  'created', 'updater', 'updated',)}),
        )
    readonly_fields = ('creator', 'created', 'updater', 'updated',)
    list_display = ('name', 'column_collection', 'updater_producer',
                    'updated', 'detail_producer',)
    inlines = (KeyValueInline,)
    form = PublisherForm


#
# Book
#
class BookAdmin(UserAdminMixin):
    fieldsets = (
        (None, {'fields': ('title',)}),
        (_('Status'), {'classes': ('collapse',),
                       'fields': ('column_collection', 'active', 'creator',
                                  'created', 'updater', 'updated',)}),
        )
    list_editable = ('active',)
    readonly_fields = ('creator', 'created', 'updater', 'updated',)
    list_display = ('title', 'column_collection', 'active', 'updater_producer',
                    'updated', 'detail_producer',)
    inlines = (KeyValueInline,)
    form = BookForm


admin.site.register(Promotion, PromotionAdmin)
admin.site.register(Publisher, PublisherAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Book, BookAdmin)
