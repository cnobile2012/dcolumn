# -*- coding: utf-8 -*-
#
# dcolumn/dcolumns/tests/test_dcolumns_forms.py
#
# WARNING: These unittests can only be run from within the original test
#          framework from https://github.com/cnobile2012/dcolumn.
#

import logging

from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

from ..models import DynamicColumn, ColumnCollection

from .base_tests import BaseDcolumns

log = logging.getLogger('tests.dcolumns.forms')


class TestCollectionBaseFormMixin(BaseDcolumns):
    _TEST_USERNAME = 'TestUser'
    _TEST_PASSWORD = 'TestPassword_007'

    def __init__(self, name):
        super(TestCollectionBaseFormMixin, self).__init__(name)
        self.client = None

    def setUp(self):
        super(TestCollectionBaseFormMixin, self).setUp()
        self.client = self._set_user_auth(self.user)

    def _set_user_auth(self, user, username=_TEST_USERNAME,
                       password=_TEST_PASSWORD, login=True):
        client = Client()

        if login:
            client.login(username=username, password=password)

        return client

    def test_proper_configuration(self):
        """
        Test that creating a book works properly. TODO -- code needs some work
        so that it will raise a ValidationError when configuration is wrong,
        as of now it raises a ValueError causing a 500 response code.
        """
        self.skipTest("Temporarily skipped")
        url = reverse('book-create')
        # Test that we get an error indicating that no there is prerequisite
        # data setup with a 200 status code.
        data = {'title': "Test Book Title"}
        response = self.client.post(url, data)
        log.debug("POST url: %s", url)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)
        self.assertTrue(self._has_error(response), msg)
        self._test_errors(response, tests={
            'column_collection': "A ColumnCollection needs to "
            })

    def test_create(self):
        """
        Test that creating a book works properly.
        """
        #self.skipTest("Temporarily skipped")
        # Create the initial configuration objects.
        required = DynamicColumn.YES
        book, cc, values = self._create_book_objects(required=required)
        log.debug("Created Book: %s, ColumnCollection: %s, values: %s",
                  book, cc, values)
        # Test that we get a field required error on the 'abstract' slug.
        url = reverse('book-create')
        data = {'title': "Test Book Title"}
        response = self.client.post(url, data)
        log.debug("POST url: %s", url)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)
        msg = "Should have errors: {}".format(response.context_data.get(
            'form').errors)
        self.assertTrue(self._has_error(response), msg)
        self._test_errors(response, tests={
            'abstract': "Abstract field is required."})
        # Test saving a new record.
        data['abstract'] = "Short abstract to satisfy the required field."
        response = self.client.post(url, data)
        msg = "response status: {}, should be 302".format(response.status_code)
        self.assertEquals(response.status_code, 302, msg)
        # Check that we have a record.
        response = self.client.get(response.url)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)
        title = response.context_data.get('object').title
        msg = "title: '{}' should match '{}'.".format(title, data.get('title'))
        self.assertEqual(title, data.get('title'), msg)

    def test_update(self):
        """
        Test that updating a book works properly.
        """
        #self.skipTest("Temporarily skipped")
        # Create the initial configuration objects.
        required = DynamicColumn.YES
        book, cc, values = self._create_book_objects(required=required)
        log.debug("Created Book: %s, ColumnCollection: %s, values: %s",
                  book, cc, values)
        # Test that we get a valid response.
        url = reverse('book-create')
        data = {'title': "Test Book Title",
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
        abstract = response.context_data.get('object').get_key_value('abstract')
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
        dc1 = self._create_dynamic_column_record(
            "Author", DynamicColumn.CHOICE, 'book_top', 2,
            relation=self.choice2index.get("Author"),
            required=DynamicColumn.YES)
        log.debug("Created Author: %s, ColumnCollection: %s, values: %s",
                  author, a_cc, a_values)
        promotion, p_cc, p_values = self._create_promotion_objects()
        dc2 = self._create_dynamic_column_record(
            "Promotion", DynamicColumn.CHOICE, 'book_top', 4,
            relation=self.choice2index.get("Promotion"),
            store_relation=DynamicColumn.YES)
        log.debug("Created Promotion: %s, ColumnCollection: %s, values: %s",
                  promotion, p_cc, p_values)
        cc = self._create_column_collection_record(
            "Book Current", 'book', dynamic_columns=[dc1, dc2])
        # Try to create a book entry with errors.
        url = reverse('book-create')
        data = {'title': "Test Book Title"}
        response = self.client.post(url, data)
        log.debug("POST url: %s", url)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)
        msg = "Should have errors: {}".format(response.context_data.get(
            'form').errors)
        self.assertTrue(self._has_error(response), msg)
        self._test_errors(response, tests={
            'author': "Author field is required."})
        # Try to create a record with an invalid promotion PK.
        data['author'] = author.pk
        data['promotion'] = 999999 # Should be invalid
        response = self.client.post(url, data)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)
        msg = "Should have errors: {}".format(response.context_data.get(
            'form').errors)
        self.assertTrue(self._has_error(response), msg)
        self._test_errors(response, tests={
            'promotion': "Could not find record "})
        # Try to create a record with an empty promotion PK.
        data['author'] = author.pk
        data['promotion'] = 'junk'
        response = self.client.post(url, data)
        msg = "response status: {}, should be 200, values: {}".format(
            response.status_code, p_values)
        self.assertEquals(response.status_code, 200, msg)
        msg = "Should have errors: {}".format(response.context_data.get(
            'form').errors)
        self.assertTrue(self._has_error(response), msg)
        self._test_errors(response, tests={
            'promotion': ", must be a number."})
        # Try to create a record with a promotion PK set to 0 (zero).
        data['author'] = author.pk
        data['promotion'] = '0'
        response = self.client.post(url, data)
        msg = "response status: {}, should be 302, values: {}".format(
            response.status_code, p_values)
        self.assertEquals(response.status_code, 302, msg)
        response = self.client.get(response.url)
        relations = response.context_data.get('relations')
        value = relations.get(dc2.pk).get('value')
        msg = "response status: {}, should be 200, relations: {}".format(
            response.status_code, relations)
        self.assertEquals(response.status_code, 200, msg)
        self.assertTrue(value == '', msg)

    def test_validate_boolean_type(self):
        """
        Test that boolean types are validated properly.
        """
        #self.skipTest("Temporarily skipped")
        author, a_cc, a_values = self._create_author_objects()
        dc0 = self._create_dynamic_column_record(
            "Author", DynamicColumn.CHOICE, 'book_top', 2,
            relation=self.choice2index.get("Author"),
            required=DynamicColumn.YES)
        dc1 = self._create_dynamic_column_record(
            "Ignore", DynamicColumn.BOOLEAN, 'book_top', 1)
        # Create the collection.
        cc = self._create_column_collection_record(
            "Book Current", 'book', dynamic_columns=[dc0, dc1,])
        # Setup default required fields and uri.
        url = reverse('book-create')
        data = {'title': "Test Book Title", 'author': author.pk}
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
        value = relations.get(dc1.pk).get('value')
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
            'ignore': "be an integer, numeric string, true/false, or yes/no."})

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
        dc2 = self._create_dynamic_column_record(
            "Date and Time", DynamicColumn.DATETIME, 'promotion_top', 3,
            required=DynamicColumn.NO)
        cc = self._create_column_collection_record(
            "Promotions", 'promotion', dynamic_columns=[dc0, dc1, dc2])
        # Try to create a publisher entry with errors.
        url = reverse('promotion-create')
        data = {'name': "100% off everything.",
                'start-date': '03/01/20000',
                'start-time': 'xxx',
                'date-and-time': 'date and time'}
        response = self.client.post(url, data)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)
        msg = "Should have errors: {}".format(response.context_data.get(
            'form').errors)
        self.assertTrue(self._has_error(response), msg)
        self._test_errors(response, tests={
            'start-date': "Invalid date and/or time object ",
            'start-time': 'Invalid date and/or time object ',
            'date-and-time': 'Invalid date and/or time object '})

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
        dc1 = self._create_dynamic_column_record(
            "Edition", DynamicColumn.NUMBER, 'book_top', 3,
            required=DynamicColumn.NO)
        cc = self._create_column_collection_record(
            "Book Current", 'book', dynamic_columns=[dc0, dc1,])
        # Setup default required fields and uri.
        url = reverse('book-create')
        data = {'title': "Test Book Title", 'author': author.pk}
        # Test the NUMBER type.
        data['edition'] = 1
        response = self.client.post(url, data)
        msg = "response status: {}, should be 302".format(response.status_code)
        self.assertEquals(response.status_code, 302, msg)
        # Get the page
        response = self.client.get(response.url)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)
        relations = response.context_data.get('relations')
        value = relations.get(dc1.pk).get('value')
        msg = "value: {}, edition: {}, relations: {}".format(
            value, data['edition'], relations)
        self.assertTrue(value == 1, msg)
        # Test the NUMBER type with a non-number.
        data['edition'] = 'bad number'
        response = self.client.post(url, data)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)
        self.assertTrue(self._has_error(response), msg)
        self._test_errors(response, tests={
            'edition': 'Edition field is not a number.'})

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
            required=DynamicColumn.YES)
        dc1 = self._create_dynamic_column_record(
            "Extra Field", DynamicColumn.TEXT, 'book_top', 3,
            required=DynamicColumn.NO)
        cc = self._create_column_collection_record(
            "Book Current", 'book', dynamic_columns=[dc0, dc1,])
        # Setup default required fields and uri.
        url = reverse('book-create')
        data = {'title': "Test Book Title", 'author': author.pk}
        # Test length of extra-field
        data['extra-field'] = "Xo"*150
        response = self.client.post(url, data)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)
        msg = "Should have errors: {}".format(response.context_data.get(
            'form').errors)
        self.assertTrue(self._has_error(response), msg)
        self._test_errors(response, tests={
            'extra-field': "Extra Field field is too long."
            })
