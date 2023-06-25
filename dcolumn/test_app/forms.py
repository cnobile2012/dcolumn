#
# dcolumn/test_app/forms.py
#

import logging

from django import forms
from django.core.exceptions import ObjectDoesNotExist

from dcolumn.dcolumns.forms import CollectionBaseFormMixin
from dcolumn.dcolumns.models import KeyValue

from example_site.books.choices import Language
from example_site.books.models import Promotion, Author, Book

log = logging.getLogger('tests.test_app.forms')


#
# TestBook
#
class TestBookForm(CollectionBaseFormMixin):
    title = forms.CharField(
        max_length=250, strip=True, required=True)
    test_bool = forms.BooleanField(
        required=False)
    test_choice = forms.ChoiceField(
        required=True)
    test_pseudo_choice = forms.ChoiceField(
        required=False)
    test_store_relation = forms.ChoiceField(
        required=False)
    test_date = forms.DateField(
        required=False)
    test_time = forms.TimeField(
        required=False)
    test_datetime = forms.DateTimeField(
        required=False)
    test_float = forms.FloatField(
        required=False)
    test_integer = forms.IntegerField(
        required=False)
    test_text = forms.CharField(
        max_length=256, strip=True, required=False)
    test_text_block = forms.CharField(
        max_length=2048, strip=True, required=False)
    active = forms.BooleanField(
        required=False)

    def __init__(self, *args, **kwargs):
        super(TestBookForm, self).__init__(*args, **kwargs)
        log.debug("TestBookForm args: %s, kwargs: %s", args, kwargs)
        self.fields['test_choice'].choices = (
            Author.objects.get_choices('name'))
        self.fields['test_pseudo_choice'].choices = (
            Language.objects.get_choices('name'))
        self.fields['test_store_relation'].choices = (
            Promotion.objects.get_choices('name'))
        # Get rid of the annoying colon after every label.
        self.label_suffix = ''
        log.debug("TestBookForm test_choice: %s, test_pseudo_choice: %s, "
                  "test_store_relation: %s",
                  self.fields['test_choice'].choices,
                  self.fields['test_pseudo_choice'].choices,
                  self.fields['test_store_relation'].choices)

    def clean_test_choice(self):
        return self._get_object(Author, 'test_choice')

    def clean_test_pseudo_choice(self):
        return self._get_object(Language, 'test_pseudo_choice')

    def clean_test_store_relation(self):
        return self._get_object(Promotion, 'test_store_relation')

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

        log.debug("Choices--field: %s, value: %s, is_zero: %s, obj: %s",
                  field, value, is_zero, obj)
        return obj

    def clean(self):
        cleaned_data = super(TestBookForm, self).clean()
        log.debug("cleaned_data: %s", cleaned_data)
        return cleaned_data

    class Meta:
        model = Book
        fields = ['title', 'test_bool', 'test_choice', 'test_pseudo_choice',
                  'test_store_relation', 'test_date', 'test_time',
                  'test_datetime', 'test_float', 'test_integer', 'test_text',
                  'test_text_block', 'active',
                  ] + CollectionBaseFormMixin.Meta.fields
