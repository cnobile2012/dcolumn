# -*- coding: utf-8 -*-
#
# dcolumn/dcolumns/tests/test_dcolumns_views.py
#
# WARNING: These unittests can only be run from within the original test
#          framework from https://github.com/cnobile2012/dcolumn.
#

import datetime
import pytz
import dateutil
import json

from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

from dcolumn.dcolumns.views import CollectionAJAXView
from dcolumn.dcolumns.models import DynamicColumn
from example_site.books.choices import Language

from .base_tests import BaseDcolumns


class TestCollectionAJAXView(BaseDcolumns):
    _TEST_USERNAME = 'TestUser'
    _TEST_PASSWORD = 'TestPassword_007'

    def __init__(self, name):
        super(TestCollectionAJAXView, self).__init__(name)
        self.client = None

    def setUp(self):
        super(TestCollectionAJAXView, self).setUp()
        self.client = self._set_user_auth()

    def _set_user_auth(self, username=_TEST_USERNAME,
                       password=_TEST_PASSWORD, login=True):
        client = Client()

        if login:
            client.login(username=username, password=password)

        return client

    def test_exceptions(self):
        """
        Test that exceptions happen when they are supposed to happen.
        """
        #self.skipTest("Temporarily skipped")
        # Setup objects for the collections.
        # Test for proper response
        class_name = 'bookX'
        url = reverse('api-collections', kwargs={'class_name': class_name})
        response = self.client.get(url)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)
        #self.assertTrue(self._has_error(response), msg)
        self._test_errors(response, tests={
            'class_name': 'bookX',
            'message': u'Error occurred: ColumnCollection matching query ',
            'valid': False
            }, exclude_keys=['valid'])

    def test_valid_response(self):
        """
        Test that the AJAX response is valid
        """
        #self.skipTest("Temporarily skipped")
        # Setup objects for the collections.
        author, a_cc, a_values = self._create_author_objects()
        promotion, p_cc, p_values = self._create_promotion_objects()
        language = Language.objects.model_objects()[3] # Russian
        dc0 = self._create_dynamic_column_record(
            "Date & Time", DynamicColumn.DATETIME, 'book_top', 6)
        dc1 = self._create_dynamic_column_record(
            "Ignore", DynamicColumn.BOOLEAN, 'book_top', 7)
        dc2 = self._create_dynamic_column_record(
            "Edition", DynamicColumn.NUMBER, 'book_top', 8)
        dc3 = self._create_dynamic_column_record(
            "Percentage", DynamicColumn.FLOAT, 'book_top', 9)
        book, b_cc, b_values = self._create_book_objects(
            author=author, promotion=promotion, language=language,
            extra_dcs=[dc0, dc1, dc2, dc3])
        value = datetime.datetime.now(pytz.utc).isoformat()
        kv0 = self._create_key_value_record(book, dc0, value)
        b_values[dc0.slug] = dateutil.parser.parse(kv0.value)
        value = 'FALSE'
        kv1 = self._create_key_value_record(book, dc1, value)
        b_values[dc1.slug] = kv1.value
        value = 2
        kv2 = self._create_key_value_record(book, dc2, value)
        b_values[dc2.slug] = kv2.value
        value = 20.5
        kv3 = self._create_key_value_record(book, dc3, value)
        b_values[dc3.slug] = kv3.value
        # Test for proper response
        class_name = 'book'
        url = reverse('api-collections', kwargs={'class_name': class_name})
        response = self.client.get(url)
        msg = "response status: {}, should be 200".format(response.status_code)
        self.assertEquals(response.status_code, 200, msg)
        content = json.loads(response.content.decode(encoding='utf-8'))
        msg = "content: {}".format(content)
        self.assertEqual(content.get('class_name'), class_name, msg)
        self.assertTrue('dynamicColumns' in content, msg)
        self.assertTrue('relations' in content, msg)
        self.assertTrue('valid' in content, msg)
