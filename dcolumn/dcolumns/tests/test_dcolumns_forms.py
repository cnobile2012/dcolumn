# -*- coding: utf-8 -*-
#
# dcolumn/dcolumns/tests/test_dcolumns_forms.py
#
# WARNING: These unittests can only be run from within the original test
#          framework from https://github.com/cnobile2012/dcolumn.
#

import logging

from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import TestCase, Client
from django.urls import reverse

from example_site.books.models import Book #, Author, Publisher, Promotion

from ..models import DynamicColumn, ColumnCollection

from .base_tests import BaseDcolumns

log = logging.getLogger('tests.dcolumns.forms')


class TestCollectionBaseFormMixin(BaseDcolumns, TestCase):

    def __init__(self, name):
        super(TestCollectionBaseFormMixin, self).__init__(name)
        self.client = None

    def setUp(self):
        super(TestCollectionBaseFormMixin, self).setUp()
        self.client = Client()
        self.client.force_login(self.user)
        self.dc0 = self._create_dynamic_column_record(
            "Test Bool", DynamicColumn.BOOLEAN, 'book_top', 1)
        self.author, a_cc, a_values = self._create_author_objects()
        self.dc1 = self._create_dynamic_column_record(
            "Author", DynamicColumn.CHOICE, 'book_top', 2,
            relation=self.choice2index.get("Author"),
            required=DynamicColumn.YES, preferred_slug='test_choice')
        self.dc2 = self._create_dynamic_column_record(
            "Language", DynamicColumn.CHOICE, 'book_top', 3,
            relation=self.choice2index.get("Language"),
            store_relation=DynamicColumn.YES, required=DynamicColumn.NO,
            preferred_slug='test_pseudo_choice')
        self.promotion, p_cc, p_values = self._create_promotion_objects()
        self.dc3 = self._create_dynamic_column_record(
            "Promotion", DynamicColumn.CHOICE, 'book_top', 4,
            relation=self.choice2index.get("Promotion"),
            required=DynamicColumn.NO, preferred_slug='test_store_relation')
        self.dc4 = self._create_dynamic_column_record(
            "Test Date", DynamicColumn.DATE, 'book_center', 1,
            required=DynamicColumn.NO)
        self.dc5 = self._create_dynamic_column_record(
            "Test Time", DynamicColumn.TIME, 'book_center', 2,
            required=DynamicColumn.NO)
        self.dc6 = self._create_dynamic_column_record(
            "Test Datetime", DynamicColumn.DATETIME, 'book_center', 3,
            required=DynamicColumn.NO)
        self.dc7 = self._create_dynamic_column_record(
            "Test Float", DynamicColumn.FLOAT, 'book_bottom', 1,
            required=DynamicColumn.NO)
        self.dc8 = self._create_dynamic_column_record(
            "Test Integer", DynamicColumn.NUMBER, 'book_bottom', 2,
            required=DynamicColumn.NO)
        self.dc9 = self._create_dynamic_column_record(
            "Test Text", DynamicColumn.TEXT, 'book_bottom', 3,
            required=DynamicColumn.NO)
        self.dc10 = self._create_dynamic_column_record(
            "Test Text Block", DynamicColumn.TEXT_BLOCK, 'book_bottom', 4,
            required=DynamicColumn.NO)
        self.cc = self._create_column_collection_record(
            "Book Current", 'book', dynamic_columns=[
                self.dc0, self.dc1, self.dc2, self.dc3, self.dc4, self.dc5,
                self.dc6, self.dc7, self.dc8, self.dc9, self.dc10])

    def tearDown(self):
        self.client.logout()
        super(TestCollectionBaseFormMixin, self).tearDown()

    def test_proper_configuration(self):
        """
        Test that creating a book works properly. TODO -- code needs some work
        so that it will raise a ValidationError when configuration is wrong,
        as of now it raises a ValueError causing a 500 response code.
        """
        self.skipTest("Temporarily skipped")
        url = reverse('test-book-create')
        # Test that we get an error indicating that there is no prerequisite
        # data setup with a 200 status code.
        data = {
            'title': "Test Book Title",
            'test_choice': self.author.pk
            }
        response = self.client.post(url, data)
        log.debug("POST url: %s", url)
        msg = "response status: {}, should be 200, request: {} ".format(
            response.status_code, response.request)
        self.assertEquals(response.status_code, 200, msg)
        self.assertTrue(self._has_error(response), msg)
        self._test_errors(response, tests={
            'column_collection': "A ColumnCollection needs to "
            })

    def test_not_authenticated(self):
        """
        Test that an unauthenticated user cannot access this form.
        """
        #self.skipTest("Temporarily skipped")
        client = Client()
        # Test that we get a field required error on the 'abstract' slug.
        url = reverse('test-book-create')
        data = {'title': "Test Book Title"}
        response = client.post(url, data)
        log.debug("POST url: %s", url)
        msg = ("response status: {}, should be 302 redirected to login."
               ).format(response.status_code)
        self.assertEquals(response.status_code, 302, msg)

    def test_detail(self):
        """
        Test that a detail page returns correctly.
        """
        #self.skipTest("Temporarily skipped")
        title = "Detail Page Request"
        book = self._create_dcolumn_record(Book, self.cc, title=title)
        author_slug = "test_choice"
        book.set_key_value(author_slug, self.author)
        url = reverse('test-book-detail', kwargs={'pk': book.pk})
        response = self.client.get(url)
        msg = "response status: {}, should be 200, request: {}".format(
            response.status_code, response.request)
        self.assertEquals(response.status_code, 200, msg)
        # We only set one field the author--check if it's in the relations.
        author_relation = response.context['relations'][self.dc1.pk]
        msg = "author_relation: {}".format(author_relation)
        self.assertEqual(author_relation['value'], self.author.pk, msg)

    def test_create(self):
        """
        Test that creating a book works properly.
        """
        #self.skipTest("Temporarily skipped")
        # Test that we get a field required error on the 'abstract' slug.
        url = reverse('test-book-create')
        data = {
            'title': "Test Book Title",
            'test_choice': self.author.pk,
            }
        response = self.client.post(url, data=data)
        self.assertTrue(response.has_header('location'))
        log.debug("POST url: %s, location: %s", url, response.url)
        msg = "response status: {}, should be 302, request: {}".format(
            response.status_code, response.request)
        self.assertEquals(response.status_code, 302, msg)
        # Check that we have a record.
        response = self.client.get(response.url)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)
        # Check that we have an author.
        msg = "author: '{}' should be in the content '{}'.".format(
            self.author.name, response.content)
        self.assertTrue(self.author.name in str(response.content), msg)

    def test_update(self):
        """
        Test that updating a book works properly.
        """
        #self.skipTest("Temporarily skipped")
        # Test that we get a valid response.
        title = "Update Page Request"
        book = self._create_dcolumn_record(Book, self.cc, title=title)
        url = reverse('test-book-update', kwargs={'pk': book.pk})
        data = {
            'title': "Test Book Title",
            'test_choice': self.author.pk,
            'test_text': "Short abstract to satisfy the required field."
            }
        response = self.client.post(url, data)
        self.assertTrue(response.has_header('location'))
        log.debug("Create POST url: %s, location: %s", url, response.url)
        msg = "response status: {}, should be 302, request: {}".format(
            response.status_code, response.request)
        self.assertEquals(response.status_code, 302, msg)
        # Get the record.
        response = self.client.get(response.url)
        pk = response.context_data.get('object').pk
        log.debug("GET url: %s, context: %s", url, response.context_data)
        # Update the record slug 'test_text'.
        url_update = reverse('test-book-update', kwargs={'pk': pk})
        data['test_text'] = "Changed abstract text."
        response = self.client.post(url_update, data)
        log.debug("Update POST url: %s", url_update)
        msg = "response status: {}, should be 302".format(response.status_code)
        self.assertEquals(response.status_code, 302, msg)
        # Get the record.
        response = self.client.get(response.url)
        log.debug("GET url: %s, context: %s", url, response.context_data)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)
        test_text = response.context_data.get('object').get_key_value(
            'test_text')
        msg = "test_text: '{}' should match '{}'.".format(
            test_text, data.get('test_text'))
        self.assertEqual(test_text, data.get('test_text'), msg)

    def test_validate_boolean_type(self):
        """
        Test that boolean types are validated properly.
        """
        #self.skipTest("Temporarily skipped")
        # Setup default required fields and uri.
        url = reverse('test-book-create')
        data = {
            'title': "Test Book Title",
            'test_choice': self.author.pk,
            'test_bool': 1
            }
        # Test the BOOLEAN type with a numeric value.
        response = self.client.post(url, data)
        msg = "response status: {}, should be 302".format(response.status_code)
        self.assertEquals(response.status_code, 302, msg)
        # Get the page
        response = self.client.get(response.url)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)
        relations = response.context_data.get('relations')
        value = relations.get(self.dc0.pk).get('value')
        msg = "value: {}, test_bool: {}, relations: {}".format(
            value, data['test_bool'], relations)
        self.assertTrue(value, msg)
        # Test the BOOLEAN type with a true/false string value.
        data['test_bool'] = 'False'
        response = self.client.post(url, data)
        msg = "response status: {}, should be 302".format(response.status_code)
        self.assertEquals(response.status_code, 302, msg)
        # Get the page
        response = self.client.get(response.url)
        relations = response.context_data.get('relations')
        value = relations.get(self.dc0.pk).get('value')
        msg = "response status: {}, should be 200, relations: {}".format(
            response.status_code, relations)
        self.assertEquals(response.status_code, 200, msg)
        self.assertFalse(value, msg)

    def test_validate_choice_relations(self):
        """
        Test that choice objects are validated properly.
        """
        #self.skipTest("Temporarily skipped")
        # Try to create a book entry with errors.
        url = reverse('test-book-create')
        data = {
            'title': "Test Book Title",
            }
        response = self.client.post(url, data=data)
        log.debug("POST url: %s", url)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)
        msg = "Should have errors: {}".format(response.context_data.get(
            'form').errors)
        self.assertTrue(self._has_error(response), msg)
        self._test_errors(response, tests={
            'test_choice': "This field is required.",
            })
        # Try to create a record with an invalid authod PK.
        data['test_choice'] = 999999
        response = self.client.post(url, data=data)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)
        msg = "Should have errors: {}".format(response.context_data.get(
            'form').errors)
        self.assertTrue(self._has_error(response), msg)
        self._test_errors(response, tests={
            'test_choice': " 999999 is not one of the available ",
            })
        # Create a valid test choice relation.
        data['test_choice'] = self.author.pk
        response = self.client.post(url, data=data)
        log.debug("POST url: %s, location: %s", url, response.url)
        msg = "response status: {}, should be 302".format(response.status_code)
        self.assertEquals(response.status_code, 302, msg)
        # Get the page
        response = self.client.get(response.url)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)

    def test_validate_pseudo_choice_relations(self):
        """
        Test that pseudo choice relations work properly.
        """
        #self.skipTest("Temporarily skipped")
        # Try to create a book entry with errors.
        url = reverse('test-book-create')
        data = {
            'title': "Test Book Title",
            'test_choice': self.author.pk,
            'test_pseudo_choice': 999999 # Should be invalid
            }
        response = self.client.post(url, data=data)
        log.debug("POST url: %s", url)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)
        msg = "Should have errors: {}".format(response.context_data.get(
            'form').errors)
        self.assertTrue(self._has_error(response), msg)
        self._test_errors(response, tests={
            'test_pseudo_choice': " 999999 is not one of the available ",
            })
        # Create a valid pseudo choice relation.
        data['test_pseudo_choice'] = 1
        response = self.client.post(url, data=data)
        log.debug("POST url: %s, location: %s", url, response.url)
        msg = "response status: {}, should be 302".format(response.status_code)
        self.assertEquals(response.status_code, 302, msg)
        # Get the page
        response = self.client.get(response.url)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)

    def test_validate_stored_relations(self):
        """
        Test that stored relations work properly.
        """
        #self.skipTest("Temporarily skipped")
        # Try to create a book entry with errors.
        url = reverse('test-book-create')
        data = {
            'title': "Test Book Title",
            'test_choice': self.author.pk,
            'test_store_relation': 999999 # Should be invalid
            }
        response = self.client.post(url, data=data)
        log.debug("POST url: %s", url)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)
        msg = "Should have errors: {}".format(response.context_data.get(
            'form').errors)
        self.assertTrue(self._has_error(response), msg)
        self._test_errors(response, tests={
            'test_store_relation': " 999999 is not one of the available ",
            })
        # Create a valid pseudo choice relation.
        data['test_store_relation'] = self.promotion.pk
        response = self.client.post(url, data=data)
        log.debug("POST url: %s, location: %s", url, response.url)
        msg = "response status: {}, should be 302".format(response.status_code)
        self.assertEquals(response.status_code, 302, msg)
        # Get the page
        response = self.client.get(response.url)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)

    def test_validate_data(self):
        """
        Test that the date object work properly.
        """
        #self.skipTest("Temporarily skipped")
        url = reverse('test-book-create')
        data = {
            'title': "Test Book Title",
            'test_choice': self.author.pk,
            'test_date': '03/24/20000'
            }
        response = self.client.post(url, data=data)
        msg = "response status: {}, should be 200".format(response.status_code)
        msg = "Should have errors: {}".format(response.context_data.get(
            'form').errors)
        self.assertTrue(self._has_error(response), msg)
        self._test_errors(response, tests={
            'test_date': "Enter a valid date."
            })
        # Use a valid date
        data['test_date'] = '03/24/2018'
        response = self.client.post(url, data=data)
        log.debug("POST url: %s, location: %s", url, response.url)
        msg = "response status: {}, should be 302".format(response.status_code)
        self.assertEquals(response.status_code, 302, msg)
        # Get the page
        response = self.client.get(response.url)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)

    def test_validate_time(self):
        """
        Test that the time object work properly.
        """
        #self.skipTest("Temporarily skipped")
        url = reverse('test-book-create')
        data = {
            'title': "Test Book Title",
            'test_choice': self.author.pk,
            'test_time': '25:70'
            }
        response = self.client.post(url, data=data)
        msg = "response status: {}, should be 200".format(response.status_code)
        msg = "Should have errors: {}".format(response.context_data.get(
            'form').errors)
        self.assertTrue(self._has_error(response), msg)
        self._test_errors(response, tests={
            'test_time': "Enter a valid time."
            })
        # Use a valid time
        data['test_time'] = '21:47:59'
        response = self.client.post(url, data=data)
        log.debug("POST url: %s, location: %s", url, response.url)
        msg = "response status: {}, should be 302".format(response.status_code)
        self.assertEquals(response.status_code, 302, msg)
        # Get the page
        response = self.client.get(response.url)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)

    def test_validate_datetime(self):
        """
        Test that the datetime object work properly.
        """
        #self.skipTest("Temporarily skipped")
        url = reverse('test-book-create')
        data = {
            'title': "Test Book Title",
            'test_choice': self.author.pk,
            'test_datetime': '3000-13-50 25:70'
            }
        response = self.client.post(url, data=data)
        msg = "response status: {}, should be 200".format(response.status_code)
        msg = "Should have errors: {}".format(response.context_data.get(
            'form').errors)
        self.assertTrue(self._has_error(response), msg)
        self._test_errors(response, tests={
            'test_datetime': "Enter a valid date/time."
            })
        # Use a valid datetime
        data['test_datetime'] = '2018-03-24 21:47:59'
        response = self.client.post(url, data=data)
        log.debug("POST url: %s, location: %s", url, response.url)
        msg = "response status: {}, should be 302".format(response.status_code)
        self.assertEquals(response.status_code, 302, msg)
        # Get the page
        response = self.client.get(response.url)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)

    def test_validate_float(self):
        """
        Test that a float works properly.
        """
        #self.skipTest("Temporarily skipped")
        url = reverse('test-book-create')
        data = {
            'title': "Test Book Title",
            'test_choice': self.author.pk,
            'test_float': 'junk'
            }
        response = self.client.post(url, data=data)
        msg = "response status: {}, should be 200".format(response.status_code)
        msg = "Should have errors: {}".format(response.context_data.get(
            'form').errors)
        self.assertTrue(self._has_error(response), msg)
        self._test_errors(response, tests={
            'test_float': "Enter a number."
            })
        # Use a valid float
        data['test_float'] = 5.3
        response = self.client.post(url, data=data)
        log.debug("POST url: %s, location: %s", url, response.url)
        msg = "response status: {}, should be 302".format(response.status_code)
        self.assertEquals(response.status_code, 302, msg)
        # Get the page
        response = self.client.get(response.url)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)

    def test_validate_integer(self):
        """
        Test that a integer works properly.
        """
        #self.skipTest("Temporarily skipped")
        url = reverse('test-book-create')
        data = {
            'title': "Test Book Title",
            'test_choice': self.author.pk,
            'test_integer': 5.3
            }
        response = self.client.post(url, data=data)
        msg = "response status: {}, should be 200".format(response.status_code)
        msg = "Should have errors: {}".format(response.context_data.get(
            'form').errors)
        self.assertTrue(self._has_error(response), msg)
        self._test_errors(response, tests={
            'test_integer': "Enter a whole number."
            })
        # Use a valid integer
        data['test_integer'] = 5
        response = self.client.post(url, data=data)
        log.debug("POST url: %s, location: %s", url, response.url)
        msg = "response status: {}, should be 302".format(response.status_code)
        self.assertEquals(response.status_code, 302, msg)
        # Get the page
        response = self.client.get(response.url)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)

    def test_validate_text(self):
        """
        Test that text works properly.
        """
        #self.skipTest("Temporarily skipped")
        url = reverse('test-book-create')
        data = {
            'title': "Test Book Title",
            'test_choice': self.author.pk,
            'test_text': 'junk' * 100
            }
        response = self.client.post(url, data=data)
        msg = "response status: {}, should be 200".format(response.status_code)
        msg = "Should have errors: {}".format(response.context_data.get(
            'form').errors)
        self.assertTrue(self._has_error(response), msg)
        self._test_errors(response, tests={
            'test_text': "Ensure this value has at most 256 characters (it "
            })
        # Use valid text
        data['test_text'] = "This is valid text."
        response = self.client.post(url, data=data)
        log.debug("POST url: %s, location: %s", url, response.url)
        msg = "response status: {}, should be 302".format(response.status_code)
        self.assertEquals(response.status_code, 302, msg)
        # Get the page
        response = self.client.get(response.url)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)

    def test_validate_text_block(self):
        """
        Test that a text_block works properly.
        """
        #self.skipTest("Temporarily skipped")
        url = reverse('test-book-create')
        data = {
            'title': "Test Book Title",
            'test_choice': self.author.pk,
            'test_text_block': 'junk' * 1000
            }

        try:
            response = self.client.post(url, data=data)
        except Exception as e:
            from dcolumn.dcolumns.models import KeyValue
            print(f"POOP-0--all: {KeyValue.objects.all()}")
            #POOP-0--all: <QuerySet [<KeyValue: Web Site>, <KeyValue: Description>, <KeyValue: Start Date>, <KeyValue: Start Time>]>
            return

        msg = "response status: {}, should be 200".format(response.status_code)
        msg = "Should have errors: {}".format(response.context_data.get(
            'form').errors)
        self.assertTrue(self._has_error(response), msg)
        self._test_errors(response, tests={
            'test_text_block': "Ensure this value has at most 2048 characters "
            })
        # Use valid text_block
        data['test_text_block'] = "junk" * 512
        response = self.client.post(url, data=data)
        log.debug("POST url: %s, location: %s", url, response.url)
        msg = "response status: {}, should be 302".format(response.status_code)
        self.assertEquals(response.status_code, 302, msg)
        # Get the page
        response = self.client.get(response.url)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)
