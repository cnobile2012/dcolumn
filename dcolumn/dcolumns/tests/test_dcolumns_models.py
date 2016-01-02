# -*- coding: utf-8 -*-
#
# dcolumn/dcolumns/tests/test_dcolumns_models.py
#
# WARNING: These unittests can only be run from within the original test
#          framework from https://github.com/cnobile2012/dcolumn.
#

import logging

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.core.exceptions import ValidationError

from example_site.books.choices import Language
from example_site.books.models import Author, Book, Publisher

from ..models import DynamicColumn, ColumnCollection, KeyValue

User = get_user_model()
# Silence the DEBUG logs.
log = logging.getLogger('dcolumns.common.model_mixins')
log.setLevel(logging.CRITICAL)
log = logging.getLogger('dcolumns.dcolumns.models')
log.setLevel(logging.CRITICAL)


class BaseDcolumns(TestCase):
    _TEST_USERNAME = 'TestUser'
    _TEST_PASSWORD = 'TestPassword_007'

    def __init__(self, name):
        super(BaseDcolumns, self).__init__(name)
        self.user = None

    def setUp(self):
        self.user = self._create_user()

    def _create_user(self, username=_TEST_USERNAME, email=None,
                     password=_TEST_PASSWORD, is_superuser=True):
        user = User.objects.create_user(username=username, password=password)
        user.first_name = "Test"
        user.last_name = "User"
        user.is_active = True
        user.is_staff = True
        user.is_superuser = is_superuser
        user.save()
        return user

    def _create_dynamic_column_record(
        self, name, slug, value_type, location, order, preferred_slug=None,
        relation=None, required=DynamicColumn.NO, active=True,
        store_relation=DynamicColumn.NO):
        kwargs = {}
        kwargs['name'] = name
        kwargs['slug'] = slug
        kwargs['value_type'] = value_type
        kwargs['location'] = location
        kwargs['order'] = order
        kwargs['preferred_slug'] = preferred_slug
        kwargs['relation'] = relation
        kwargs['required'] = required
        kwargs['store_relation'] = store_relation
        kwargs['active'] = active
        kwargs['creator'] = self.user
        kwargs['updater'] = self.user
        obj = DynamicColumn(**kwargs)
        obj.save()
        return obj

    def _create_column_collection_record(self, name, dynamic_columns=[],
                                         active=True):
        kwargs = {}
        kwargs['name'] = name
        kwargs['active'] = active
        kwargs['creator'] = self.user
        kwargs['updater'] = self.user
        obj = ColumnCollection(**kwargs)
        obj.save()
        obj.process_dynamic_columns(dynamic_columns)
        return obj

    def _create_dcolumn_record(self, model, collection, **kwargs):
        kwargs['created'] = self.user
        kwargs['updated'] = self.user
        return model.objects.create(column_collection=collection, **kwargs)

    def _create_key_value_record(self, collection, dynamic_column, value):
        kwargs = {}
        kwargs['collection'] = collection
        kwargs['dynamic_column'] = dynamic_column
        kwargs['value'] = value
        return KeyValue.objects.create(**kwargs)


class TestDynamicColumn(BaseDcolumns):

    def __init__(self, name):
        super(TestDynamicColumn, self).__init__(name)

    def test_get_choice_relation_object_and_field(self):
        """
        Test that the relation object is returned.
        """
        #self.skipTest("Temporarily skipped")
        # Create a choice type object.
        dc0 = self._create_dynamic_column_record(
            "Language", 'language', DynamicColumn.CHOICE, 'book_center', 6,
            relation=1)
        obj, field = dc0.get_choice_relation_object_and_field()
        msg = "obj: %s, field: {}".format(obj, field)
        self.assertTrue(obj == Language, msg)
        self.assertEqual(field, 'name', msg)

    def test_get_fk_slugs(self):
        """
        Test that a dict of slugs are returned for CHOICE type fields.
        """
        #self.skipTest("Temporarily skipped")
        # Test with no choice type objects.
        dc0 = self._create_dynamic_column_record(
            "Postal Code", 'postal-code', DynamicColumn.TEXT, 'publisher_top', 6
            )
        slugs = DynamicColumn.objects.get_fk_slugs()
        msg = "slugs: {}".format(slugs)
        self.assertEqual(len(slugs), 0, msg)
        # Test with a choice type object.
        dc1 = self._create_dynamic_column_record(
            "Language", 'language', DynamicColumn.CHOICE, 'book_center', 6,
            relation=1)
        slugs = DynamicColumn.objects.get_fk_slugs()
        msg = "slugs: {}".format(slugs)
        self.assertEqual(len(slugs), 1, msg)


class TestColumnCollection(BaseDcolumns):

    def __init__(self, name):
        super(TestColumnCollection, self).__init__(name)

    def test_process_dynamic_columns(self):
        """
        Test that dynamic columns are added, updated and removed from the
        ColumnCollection model properly.
        """
        #self.skipTest("Temporarily skipped")
        dc0 = self._create_dynamic_column_record(
            "Author", 'author', DynamicColumn.CHOICE, 'book_top', 1,
            relation=3)
        dc1 = self._create_dynamic_column_record(
            "Publisher", 'publisher', DynamicColumn.CHOICE, 'book_top', 2,
            relation=4)
        dc2 = self._create_dynamic_column_record(
            "Abstract", 'abstract', DynamicColumn.TEXT_BLOCK, 'book_top', 3)
        # Test that there are no dynamic columns.
        cc = self._create_column_collection_record("Books")
        msg = "dynamic columns: {}".format(cc.dynamic_column.all())
        self.assertEqual(cc.dynamic_column.count(), 0, msg)
        # Test that there is one dynamic column.
        cc.process_dynamic_columns([dc0])
        msg = "dynamic columns: {}".format(cc.dynamic_column.all())
        self.assertEqual(cc.dynamic_column.count(), 1, msg)
        # Test that there are two dynamic columns.
        cc.process_dynamic_columns([dc0, dc1])
        msg = "dynamic columns: {}".format(cc.dynamic_column.all())
        self.assertEqual(cc.dynamic_column.count(), 2, msg)
        # Test that replacing one dynamic column the results are two.
        cc.process_dynamic_columns([dc1, dc2])
        msg = "dynamic columns: {}".format(cc.dynamic_column.all())
        self.assertEqual(cc.dynamic_column.count(), 2, msg)

    def test_get_column_collection(self):
        """
        Test that the proper sets are returned from the get_column_collection
        method.
        """
        #self.skipTest("Temporarily skipped")
        # Create a few dynamic columns.
        dc0 = self._create_dynamic_column_record(
            "Postal Code", 'postal-code', DynamicColumn.TEXT, 'publisher_top', 6
            )
        dc1 = self._create_dynamic_column_record(
            "Language", 'language', DynamicColumn.CHOICE, 'book_center', 6,
            relation=1)
        dc2 = self._create_dynamic_column_record(
            "Web Site", 'author-url', DynamicColumn.TEXT, 'author_top', 1)
        # Add two dynamic columns to the collections.
        cc0 = self._create_column_collection_record(
            'Author', dynamic_columns=[dc2])
        cc1 = self._create_column_collection_record(
            'Publisher', dynamic_columns=[dc0])
        # Test that there is one per collection.
        cc_set0 = ColumnCollection.objects.get_column_collection('Author')
        cc_set1 = ColumnCollection.objects.get_column_collection('Publisher')
        msg = "cc_set0: {}, cc_set1: {}".format(cc_set0, cc_set1)
        self.assertEqual(cc_set0.count(), 1, msg)
        self.assertTrue(cc_set0[0] == dc2, msg)
        self.assertEqual(cc_set1.count(), 1, msg)
        self.assertTrue(cc_set1[0] == dc0, msg)
        # Test that any unassigned dynamic columns are returned.
        cc_set2 = ColumnCollection.objects.get_column_collection(
            'Book', unassigned=True)
        msg = "cc_set2: {}".format(cc_set2)
        self.assertEqual(cc_set2.count(), 1, msg)
        self.assertTrue(cc_set2[0] == dc1, msg)

    def test_serialize_columns(self):
        """
        Test the serialization of a collection's dynamic columns.
        """
        #self.skipTest("Temporarily skipped")
        # Create a few dynamic columns.
        dc0 = self._create_dynamic_column_record(
            "Author", 'author', DynamicColumn.CHOICE, 'book_top', 1,
            relation=3)
        dc1 = self._create_dynamic_column_record(
            "Publisher", 'publisher', DynamicColumn.CHOICE, 'book_top', 2,
            relation=4)
        dc2 = self._create_dynamic_column_record(
            "Abstract", 'abstract', DynamicColumn.TEXT_BLOCK, 'book_top', 3)
        # Test that the serialized object is correct using pks and has no value.
        cc0 = self._create_column_collection_record(
            "Books", dynamic_columns=[dc0, dc1, dc2])
        result = ColumnCollection.objects.serialize_columns('Books')
        msg = "result: {}".format(result)

        for pk in (dc0.pk, dc1.pk, dc2.pk):
            self.assertTrue(pk in result, msg)
            # Test that the value is not included.
            self.assertEquals(result[pk].get('value'), None, msg)

        # Test that the serialized oject is correct using slugs and has no
        # value.
        result = ColumnCollection.objects.serialize_columns(
            'Books', by_slug=True)
        msg = "result: {}".format(result)

        for slug in (dc0.slug, dc1.slug, dc2.slug):
            self.assertTrue(slug in result, msg)
            # Test that the value is not included.
            self.assertEquals(result[slug].get('value'), None, msg)




















class TestCollectionBase(BaseDcolumns):

    def __init__(self, name):
        super(TestCollectionBase, self).__init__(name)

    def test_collection_serialize_columns(self):
        """

        """
        self.skipTest("Temporarily skipped")
        # Put the dynamic columns in a collection.
        cc0 = self._create_column_collection_record(
            "Books", dynamic_columns=[dc0, dc1, dc2])
        cc1 = self._create_column_collection_record(
            "Authors", dynamic_columns=[])
        cc2 = self._create_column_collection_record(
            "Publishers", dynamic_columns=[])

        # Test that the serialized object has values.
        # Create three records one each for Book, Author, and Publisher.
        book = self._create_dcolumn_record(
            Book, collection=cc0, title="Bogus Book Name")
        author = self._create_dcolumn_record(
            Author, collection=cc1, name='Me Myself')
        publisher = self._create_dcolumn_record(
            Publisher, collection=cc2, name='My Publisher')
        # Create three values for Book.
        kv0 = self._create_key_value_record(cc0, dc0, author.pk)
        kv1 = self._create_key_value_record(cc0, dc1, publisher.pk)
        kv2 = self._create_key_value_record(cc0, dc2, "Test for Abstract.")
        # Get serialized object.
        result = ColumnCollection.objects.serialize_columns('Books', obj=book)
        msg = "result: {}".format(result)
        print msg
        #for pk in (dc0.pk, dc1.pk, dc2.pk):
        #    self.assertTrue(False, msg)






