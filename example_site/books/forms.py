#
# example_site/books/forms.py
#

import logging

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from dcolumn.dcolumns.forms import CollectionBaseFormMixin
from dcolumn.dcolumns.models import KeyValue

from .choices import Language
from .models import Promotion, Author, Publisher, Book

log = logging.getLogger('examples.books.forms')


#
# Promotion
#
class PromotionForm(CollectionBaseFormMixin):
    name = forms.CharField(
        max_length=250, strip=True, required=True)
    promotion_description = forms.CharField(
        max_length=2048, strip=True, required=False)
    promotion_start_date = forms.DateField(
        required=True)
    promotion_start_time = forms.TimeField(
        required=True)
    promotion_end_date = forms.DateField(
        required=True)
    promotion_end_time = forms.TimeField(
        required=True)
    active = forms.BooleanField(
        required=False)

    def __init__(self, *args, **kwargs):
        super(PromotionForm, self).__init__(*args, **kwargs)
        log.debug("PromotionForm args: %s, kwargs: %s", args, kwargs)
        # Get rid of the annoying colon after every label.
        self.label_suffix = ''

    class Meta:
        model = Promotion
        fields = ['name', 'promotion_description', 'promotion_start_date',
                  'promotion_start_time', 'promotion_end_date',
                  'promotion_end_time', 'active'
                  ] + CollectionBaseFormMixin.Meta.fields

    class Media:
        css = {
            'all': ('css/promotions.css',)
            }


#
# Author
#
class AuthorForm(CollectionBaseFormMixin):
    name = forms.CharField(
        max_length=250, strip=True, required=True)
    author_url = forms.URLField(
        max_length=1024, required=False)
    active = forms.BooleanField(
        required=False)

    def __init__(self, *args, **kwargs):
        super(AuthorForm, self).__init__(*args, **kwargs)
        log.debug("AuthorForm args: %s, kwargs: %s", args, kwargs)
        # Get rid of the annoying colon after every label.
        self.label_suffix = ''

    class Meta:
        model = Author
        fields = ['name', 'author_url', 'active',
                  ] + CollectionBaseFormMixin.Meta.fields


#
# Publisher
#
class PublisherForm(CollectionBaseFormMixin):
    name = forms.CharField(
        max_length=250, strip=True, required=True)
    address_1 = forms.CharField(
        max_length=250, strip=True, required=False)
    address_2 = forms.CharField(
        max_length=250, strip=True, required=False)
    city = forms.CharField(
        max_length=250, strip=True, required=False)
    state = forms.CharField(
        max_length=250, strip=True, required=False)
    country = forms.CharField(
        max_length=250, strip=True, required=False)
    postal_code = forms.CharField(
        max_length=250, strip=True, required=False)
    publisher_phone = forms.CharField(
        max_length=250, strip=True, required=False)
    publisher_url = forms.CharField(
        max_length=1024, strip=True, required=False)
    active = forms.BooleanField(
        required=False)

    def __init__(self, *args, **kwargs):
        super(PublisherForm, self).__init__(*args, **kwargs)
        log.debug("PublisherForm args: %s, kwargs: %s", args, kwargs)
        # Get rid of the annoying colon after every label.
        self.label_suffix = ''

    class Meta:
        model = Publisher
        fields = ['name', 'address_1', 'address_2', 'city', 'state',
                  'country', 'postal_code', 'publisher_phone', 'publisher_url',
                  'active',] + CollectionBaseFormMixin.Meta.fields


#
# Book
#
class BookForm(CollectionBaseFormMixin):
    title = forms.CharField(
        max_length=250, strip=True, required=True)
    author = forms.ChoiceField(
        required=True)
    publisher = forms.ChoiceField(
        required=True)
    abstract = forms.CharField(
        max_length=2048, strip=True, required=False)
    number_of_pages = forms.IntegerField(
        required=False)
    edition = forms.IntegerField(
        required=False)
    published_date = forms.DateField(
        required=False)
    copyright_year = forms.IntegerField(
        required=False)
    isbn10 = forms.CharField(
        max_length=250, strip=True, required=False)
    isbn13 = forms.CharField(
        max_length=250, strip=True, required=False)
    language = forms.ChoiceField(
        required=False)
    promotion = forms.ChoiceField(
        required=False)
    book_sku = forms.CharField(
        max_length=250, strip=True, required=False)
    active = forms.BooleanField(
        required=False)

    def __init__(self, *args, **kwargs):
        super(BookForm, self).__init__(*args, **kwargs)
        log.debug("BookForm args: %s, kwargs: %s", args, kwargs)
        self.fields['author'].choices = Author.objects.get_choices('name')
        self.fields['publisher'].choices = Publisher.objects.get_choices(
            'name')
        self.fields['language'].choices = Language.objects.get_choices('name')
        self.fields['promotion'].choices = Promotion.objects.get_choices(
            'name')
        # Get rid of the annoying colon after every label.
        self.label_suffix = ''

    def clean_author(self):
        return self._get_object(Author, 'author')

    def clean_publisher(self):
        return self._get_object(Publisher, 'publisher')

    def clean_language(self):
        return self._get_object(Language, 'language')

    def clean_promotion(self):
        return self._get_object(Promotion, 'promotion')

    def _get_object(self, model, field):
        """
        A zero would be the first select option indicating the
        instructions on selecting a choice. Therefore it's not permitted
        on required fields. If the data is correct then try to get the
        object.
        """
        value = self.cleaned_data.get(field, 0)
        is_zero = value in (0, '0', None, '')
        obj = None

        if self.fields[field].required and is_zero:
            msg = _("The value {} is not permitted.").format(value)
            raise forms.ValidationError(msg)

        if not is_zero: # Left blank
            try:
                obj = model.objects.get(pk=value)
            except ObjectDoesNotExist:
                msg = _("Could not find {} with this id {}").format(
                    model.__name__, value)
                raise forms.ValidationError(msg)

        return obj

    class Meta:
        model = Book
        fields = ['title', 'author', 'publisher', 'abstract',
                  'number_of_pages', 'edition', 'published_date',
                  'copyright_year', 'isbn10', 'isbn13', 'language',
                  'promotion', 'book_sku', 'active',
                  ] + CollectionBaseFormMixin.Meta.fields
