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
        title = "Detail Page Request"
        book = self._create_dcolumn_record(Book, self.cc, title=title)
        author_slug = "test_choice"
        book.set_key_value(author_slug, self.author)
        url = reverse('test-book-detail', kwargs={'pk': book.pk})
        response = self.client.get(url)
        msg = "response status: {}, should be 200, request: {}".format(
            response.status_code, response.request)
        self.assertEquals(response.status_code, 200, msg)
        # We only set one fiels the author, check if it's in the relations.
        author_relation = response.context['relations'][self.dc1.pk]
        msg = "author_relation: {}".format(author_relation)
        self.assertEqual(author_relation['value'], self.author.pk, msg)

    def test_create(self):
        """
        Test that creating a book works properly.
        """
        # Test that we get a field required error on the 'abstract' slug.
        url = reverse('test-book-create')
        data = {'title': "Test Book Title",
                'test_choice': self.author.pk,
                #'publisher': publisher.pk
                }
        response = self.client.post(url, data=data)
        self.assertTrue(response.has_header('location'))
        location = response._headers['location']
        log.debug("POST url: %s, location: %s", url, location)
        msg = "response status: {}, should be 302, request: {}".format(
            response.status_code, response.request)
        self.assertEquals(response.status_code, 302, msg)
        # Check that we have a record.
        response = self.client.get(location[1])
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
        # Create the initial configuration objects.
        required = DynamicColumn.YES
        author, a_cc, a_values = self._create_author_objects()
        publisher, p_cc, p_values = self._create_publisher_objects()
        book, cc, values = self._create_book_objects(author=author,
                                                     publisher=publisher,
                                                     required=required)
        log.debug("Created Book: %s, ColumnCollection: %s, values: %s",
                  book, cc, values)
        # Test that we get a valid response.
        url = reverse('book-update', kwargs={'pk': book.pk})
        data = {'title': "Test Book Title",
                'author': author.pk,
                'publisher': publisher.pk,
                'abstract': "Short abstract to satisfy the required field."}
        response = self.client.post(url, data)
        log.debug("Create POST url: %s", url)
        msg = "response status: {}, should be 302".format(response.status_code)
        self.assertEquals(response.status_code, 302, msg)
        # Get the record.
        response = self.client.get(response.url)
        pk = response.context_data.get('object').pk
        log.debug("GET url: %s, context: %s", url, response.context_data)
        # Update the record.
        url_update = reverse('book-update', kwargs={'pk': pk})
        data['abstract'] = "Changed abstract text."
        response = self.client.post(url_update, data)
        log.debug("Update POST url: %s", url_update)
        msg = "response status: {}, should be 302".format(response.status_code)
        self.assertEquals(response.status_code, 302, msg)
        # Get the record.
        response = self.client.get(response.url)
        log.debug("GET url: %s, context: %s", url, response.context_data)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)
        abstract = response.context_data.get('object').get_key_value(
            'abstract')
        msg = "abstract: '{}' should match '{}'.".format(
            abstract, data.get('abstract'))
        self.assertEqual(abstract, data.get('abstract'), msg)

    def test_validate_choice_relations(self):
        """
        Test that choice objects are validated properly.
        """
        #self.skipTest("Temporarily skipped")
        # Create the DynamicColumn for the author and promotion.
        author, a_cc, a_values = self._create_author_objects()
        dc0 = self._create_dynamic_column_record(
            "Author", DynamicColumn.CHOICE, 'book_top', 2,
            relation=self.choice2index.get("Author"),
            required=DynamicColumn.YES)
        log.debug("Created Author: %s, ColumnCollection: %s, values: %s",
                  author, a_cc, a_values)
        promotion, p_cc, p_values = self._create_promotion_objects()
        dc1 = self._create_dynamic_column_record(
            "Promotion", DynamicColumn.CHOICE, 'book_top', 4,
            relation=self.choice2index.get("Promotion"),
            store_relation=DynamicColumn.YES)
        log.debug("Created Promotion: %s, ColumnCollection: %s, values: %s",
                  promotion, p_cc, p_values)
        cc = self._create_column_collection_record(
            "Book Current", 'book', dynamic_columns=[dc0, dc1])
        # Try to create a book entry with errors.
        url = reverse('book-create')
        data = {'title': "Test Book Title"}
        response = self.client.post(url, data=data)
        log.debug("POST url: %s", url)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)
        msg = "Should have errors: {}".format(response.context_data.get(
            'form').errors)
        self.assertTrue(self._has_error(response), msg)
        self._test_errors(response, tests={
            'author': "This field is required.",
            'publisher': "This field is required.",
            })
        # Try to create a record with an invalid promotion PK.
        data['author'] = author.pk
        data['promotion'] = 999999 # Should be invalid
        response = self.client.post(url, data=data)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)
        msg = "Should have errors: {}".format(response.context_data.get(
            'form').errors)
        self.assertTrue(self._has_error(response), msg)
        self._test_errors(response, tests={
            'promotion': " 999999 is not one of the available choices.",
            'publisher': "This field is required.",
            })
        # Try to create a record with an empty promotion PK.
        data['author'] = author.pk
        data['promotion'] = 'junk'
        response = self.client.post(url, data=data)
        msg = "response status: {}, should be 200, values: {}".format(
            response.status_code, p_values)
        self.assertEquals(response.status_code, 200, msg)
        msg = "Should have errors: {}".format(response.context_data.get(
            'form').errors)
        self.assertTrue(self._has_error(response), msg)
        self._test_errors(response, tests={
            'promotion': " junk is not one of the available choices.",
            'publisher': "This field is required.",
            })

    def test_validate_boolean_type(self):
        """
        Test that boolean types are validated properly.
        """
        #self.skipTest("Temporarily skipped")
        author, a_cc, a_values = self._create_author_objects()
        dc0 = self._create_dynamic_column_record(
            "Author", DynamicColumn.CHOICE, 'book_top', 1,
            relation=self.choice2index.get("Author"),
            required=DynamicColumn.YES)
        publisher, p_cc, p_values = self._create_publisher_objects()
        dc1 = self._create_dynamic_column_record(
            "Publisher", DynamicColumn.CHOICE, 'book_top', 2,
            relation=self.choice2index.get("Publisher"),
            required=DynamicColumn.YES)
        dc2 = self._create_dynamic_column_record(
            "Ignore", DynamicColumn.BOOLEAN, 'book_top', 3)
        # Create the collection.
        cc = self._create_column_collection_record(
            "Book Current", 'book', dynamic_columns=[dc0, dc1, dc2])
        # Setup default required fields and uri.
        url = reverse('book-create')
        data = {'title': "Test Book Title",
                'author': author.pk,
                'publisher': publisher.pk
                }
        # Test the BOOLEAN type with a numeric value.
        data['ignore'] = 1
        response = self.client.post(url, data)
        msg = "response status: {}, should be 302".format(response.status_code)
        self.assertEquals(response.status_code, 302, msg)
        # Get the page
        response = self.client.get(response.url)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)
        relations = response.context_data.get('relations')
        value = relations.get(dc2.pk).get('value')
        msg = "value: {}, ignore: {}, relations: {}".format(
            value, data['ignore'], relations)
        self.assertTrue(value == 1, msg)
        # Test the BOOLEAN type with a true/false string value.
        data['ignore'] = 'False'
        response = self.client.post(url, data)
        msg = "response status: {}, should be 302".format(response.status_code)
        self.assertEquals(response.status_code, 302, msg)
        # Get the page
        response = self.client.get(response.url)
        relations = response.context_data.get('relations')
        value = relations.get(dc1.pk).get('value')
        msg = "response status: {}, should be 200, relations: {}".format(
            response.status_code, relations)
        self.assertEquals(response.status_code, 200, msg)
        self.assertTrue(value == 'False', msg)
        # Test the BOOLEAN type with a yes/no string value.
        data['ignore'] = 'YES'
        response = self.client.post(url, data)
        msg = "response status: {}, should be 302".format(response.status_code)
        self.assertEquals(response.status_code, 302, msg)
        # Get the page
        response = self.client.get(response.url)
        relations = response.context_data.get('relations')
        value = relations.get(dc1.pk).get('value')
        msg = "response status: {}, should be 200, relations: {}".format(
            response.status_code, relations)
        self.assertEquals(response.status_code, 200, msg)
        self.assertTrue(value == 'YES', msg)
        # Test the BOOLEAN type with bad data
        data['ignore'] = 'bad data'
        response = self.client.post(url, data)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)
        self.assertTrue(self._has_error(response), msg)
        self._test_errors(response, tests={
            'ignore': "be an integer, numeric string, true/false, or yes/no."
            })

    def test_validate_date_types(self):
        """
        Test that date objects are validated properly.
        """
        #self.skipTest("Temporarily skipped")
        # Create the collection
        dc0 = self._create_dynamic_column_record(
            "Start Date", DynamicColumn.DATE, 'promotion_top', 2,
            required=DynamicColumn.NO)
        dc1 = self._create_dynamic_column_record(
            "Start Time", DynamicColumn.TIME, 'promotion_top', 3,
            required=DynamicColumn.NO)
        cc = self._create_column_collection_record(
            "Promotions", 'promotion', dynamic_columns=[dc0, dc1])
        # Try to create a publisher entry with errors.
        url = reverse('promotion-create')
        data = {
            'name': "100% off everything.",
            'promotion_start_date': '03/01/20000',
            'promotion_start_time': 'xxx',
            }
        response = self.client.post(url, data=data)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)
        msg = "Should have errors: {}".format(response.context_data.get(
            'form').errors)
        self.assertTrue(self._has_error(response), msg)
        self._test_errors(response, tests={
            'promotion_start_date': "Enter a valid date.",
            'promotion_start_time': "Enter a valid time.",
            'promotion_end_date': "This field is required.",
            'promotion_end_time': "This field is required.",
            })

    def test_validate_numeric_type(self):
        """
        Test that numeric objects are validated properly.
        """
        #self.skipTest("Temporarily skipped")
        # Create the collection
        author, a_cc, a_values = self._create_author_objects()
        dc0 = self._create_dynamic_column_record(
            "Author", DynamicColumn.CHOICE, 'book_top', 2,
            relation=self.choice2index.get("Author"),
            required=DynamicColumn.YES)
        publisher, p_cc, p_values = self._create_publisher_objects()
        dc1 = self._create_dynamic_column_record(
            "Publisher", DynamicColumn.CHOICE, 'book_top', 3,
            relation=self.choice2index.get("Publisher"),
            required=DynamicColumn.YES)
        dc2 = self._create_dynamic_column_record(
            "Edition", DynamicColumn.NUMBER, 'book_top', 4,
            required=DynamicColumn.NO)
        cc = self._create_column_collection_record(
            "Book Current", 'book', dynamic_columns=[dc0, dc1, dc2])
        # Setup default required fields and uri.
        post_url = reverse('book-create')
        data = {
            'title': "Test Book Title",
            'author': author.pk,
            'publisher': publisher.pk
            }
        # Test the NUMBER type.
        data['edition'] = 1
        response = self.client.post(post_url, data=data)
        msg = "response status: {}, should be 302".format(response.status_code)
        self.assertEquals(response.status_code, 302, msg)
        # Get the page
        book = Book.objects.get(title=data.get('title'))
        get_url = reverse('book-detail', kwargs={'pk': book.pk})
        response = self.client.get(get_url)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)
        relations = response.context_data.get('relations')
        value = relations.get(dc2.pk).get('value')
        msg = "value: '{}', edition: '{}', relations: {}".format(
            value, data['edition'], relations)
        self.assertEqual(value, data['edition'], msg)
        # Test the NUMBER type with a non-number.
        data['edition'] = 'bad number'
        response = self.client.post(post_url, data)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)
        self.assertTrue(self._has_error(response), msg)
        self._test_errors(response, tests={
            'edition': 'Enter a whole number.'})

    def test_validate_value_length(self):
        """
        Test that value lengths are validated properly.
        """
        #self.skipTest("Temporarily skipped")
        # Create the collection.
        author, a_cc, a_values = self._create_author_objects()
        dc0 = self._create_dynamic_column_record(
            "Author", DynamicColumn.CHOICE, 'book_top', 2,
            relation=self.choice2index.get("Author"),
            preferred_slug='author',
            required=DynamicColumn.YES)
        publisher, p_cc, p_values = self._create_publisher_objects()
        dc1 = self._create_dynamic_column_record(
            "Publisher", DynamicColumn.CHOICE, 'book_top', 3,
            relation=self.choice2index.get("Publisher"),
            preferred_slug='publisher',
            required=DynamicColumn.YES)
        dc2 = self._create_dynamic_column_record(
            "Abstract", DynamicColumn.TEXT, 'book_top', 4,
            preferred_slug='abstract',
            required=DynamicColumn.NO)
        cc = self._create_column_collection_record(
            "Book Current", 'book', dynamic_columns=[dc0, dc1, dc2])
        # Setup default required fields and uri.
        url = reverse('book-create')
        data = {
            'title': "Test Book Title",
            'author': author.pk,
            'publisher': publisher.pk
            }
        # Test length of extra_field
        data['abstract'] = "Xo"*1500
        response = self.client.post(url, data=data)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)
        errors = response.context_data.get('form').errors
        msg = "Should have errors: {}".format(errors)
        self.assertTrue(self._has_error(response), msg)
        self._test_errors(response, tests={
            'abstract': "Ensure this value has at most 2048 characters "
            })
