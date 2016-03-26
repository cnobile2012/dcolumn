# -*- coding: utf-8 -*-
#
# dcolumn/dcolumns/tests/test_dcolumns_forms.py
#
# WARNING: These unittests can only be run from within the original test
#          framework from https://github.com/cnobile2012/dcolumn.
#

from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

from ..models import DynamicColumn, ColumnCollection

from .test_dcolumns_models import BaseDcolumns


class TestCollectionFormMixin(BaseDcolumns):
    _TEST_USERNAME = 'TestUser'
    _TEST_PASSWORD = 'TestPassword_007'

    def __init__(self, name):
        super(TestCollectionFormMixin, self).__init__(name)
        self.client = None

    def setUp(self):
        super(TestCollectionFormMixin, self).setUp()
        self.client = self._set_user_auth(self.user)

    def _set_user_auth(self, user, username=_TEST_USERNAME,
                       password=_TEST_PASSWORD, login=True):
        client = Client()

        if login:
            client.login(username=username, password=password)

        return client

    def _has_error(self, response):
        result = False

        if hasattr(response, 'context_data'):
            errors = response.context_data.get('form').errors

            if errors:
                result = True

        return result

    def _test_errors(self, response, tests={}):
        if hasattr(response, 'context_data'):
            errors = dict(response.context_data.get('form').errors)
            print errors

            for key, value in tests.items():
                err_msg = errors.pop(key, '').as_text()
                msg = "For key '{}' value '{}' not found in '{}'".format(
                    key, value, err_msg)
                self.assertTrue(value in err_msg, msg)

            msg = "Unaccounted for errors: {}".format(errors)
            self.assertFalse(len(errors), msg)

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
        url = reverse('book-create')
        data = {'title': "Test Book Title"}
        required = DynamicColumn.YES
        book, cc, values = self._create_book_objects(required=required)
        # Test that we get a field required error on the 'abstract' slug.
        response = self.client.post(url, data)
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
        url = reverse('book-create')
        data = {'title': "Test Book Title",
                'abstract': "Short abstract to satisfy the required field."}
        required = DynamicColumn.YES
        book, cc, values = self._create_book_objects(required=required)
        # Test that we get a valid response.
        response = self.client.post(url, data)
        msg = "response status: {}, should be 302".format(response.status_code)
        self.assertEquals(response.status_code, 302, msg)
        # Get the record.
        response = self.client.get(response.url)
        pk = response.context_data.get('object').pk
        # Update the record.
        url_update = reverse('book-update', kwargs={'pk': pk})
        data['abstract'] = "Changed abstract text."
        response = self.client.post(url_update, data)
        msg = "response status: {}, should be 302".format(response.status_code)
        self.assertEquals(response.status_code, 302, msg)
        # Get the record.
        response = self.client.get(response.url)
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
        # Create the DynamicColumn for the author.
        author, a_cc, a_values = self._create_author_objects()
        dc1 = self._create_dynamic_column_record(
            "Author", DynamicColumn.CHOICE, 'book_top', 2,
            relation=self.choice2index.get("Author"),
            required=DynamicColumn.YES)
        # Create the collection.
        cc = self._create_column_collection_record(
            "Book Current", 'book', dynamic_columns=[dc1])
        # Create a book entry.
        url = reverse('book-create')
        data = {'title': "Test Book Title"}
        response = self.client.post(url, data)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)
        msg = "Should have errors: {}".format(response.context_data.get(
            'form').errors)
        self.assertTrue(self._has_error(response), msg)
        self._test_errors(response, tests={
            'author': ""})





        #author, a_cc, a_values = self._create_author_objects()










# Redirect: ['allowed_schemes', 'charset', 'client', 'close', 'closed', 'content', 'context', 'cookies', 'delete_cookie', 'flush', 'get', 'getvalue', 'has_header', 'items', 'json', 'make_bytes', 'next', 'reason_phrase', 'request', 'resolver_match', 'serialize', 'serialize_headers', 'set_cookie', 'set_signed_cookie', 'setdefault', 'status_code', 'streaming', 'tell', 'templates', 'url', 'writable', 'write', 'writelines', 'wsgi_request']

# Get: ['add_post_render_callback', 'charset', 'client', 'close', 'closed', 'content', 'context', 'context_data', 'cookies', 'delete_cookie', 'flush', 'get', 'getvalue', 'has_header', 'is_rendered', 'items', 'json', 'make_bytes', 'next', 'reason_phrase', 'render', 'rendered_content', 'rendering_attrs', 'request', 'resolve_context', 'resolve_template', 'resolver_match', 'serialize', 'serialize_headers', 'set_cookie', 'set_signed_cookie', 'setdefault', 'status_code', 'streaming', 'tell', 'template_name', 'templates', 'using', 'writable', 'write', 'writelines', 'wsgi_request']

