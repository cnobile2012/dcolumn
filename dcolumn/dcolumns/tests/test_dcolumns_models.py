# -*- coding: utf-8 -*-
#
# dcolumn/dcolumns/tests/test_dcolumns_models.py
#
# WARNING: These unittests can only be run from within the original test
#          framework from https://github.com/cnobile2012/dcolumn.
#

import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase

from example_site.books.choices import Language
from example_site.books.models import Author, Book, Publisher, Promotion

from ..models import DynamicColumn, ColumnCollection, KeyValue

User = get_user_model()


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
        self, name, value_type, location, order, preferred_slug=None,
        relation=None, required=DynamicColumn.NO, active=True,
        store_relation=DynamicColumn.NO):
        kwargs = {}
        kwargs['name'] = name
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
        return DynamicColumn.objects.create(**kwargs)

    def _create_column_collection_record(self, name, dynamic_columns=[],
                                         active=True):
        kwargs = {}
        kwargs['name'] = name
        kwargs['active'] = active
        kwargs['creator'] = self.user
        kwargs['updater'] = self.user
        obj = ColumnCollection.objects.create(**kwargs)
        obj.process_dynamic_columns(dynamic_columns)
        return obj

    def _create_dcolumn_record(self, model, collection, **kwargs):
        kwargs['creator'] = self.user
        kwargs['updater'] = self.user
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
            "Language", DynamicColumn.CHOICE, 'book_center', 6, relation=1)
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
            "Postal Code", DynamicColumn.TEXT, 'publisher_top', 6)
        slugs = DynamicColumn.objects.get_fk_slugs()
        msg = "slugs: {}".format(slugs)
        self.assertEqual(len(slugs), 0, msg)
        # Test with a choice type object.
        dc1 = self._create_dynamic_column_record(
            "Language", DynamicColumn.CHOICE, 'book_center', 6, relation=1)
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
            "Author", DynamicColumn.CHOICE, 'book_top', 1, relation=3)
        dc1 = self._create_dynamic_column_record(
            "Publisher", DynamicColumn.CHOICE, 'book_top', 2, relation=4)
        dc2 = self._create_dynamic_column_record(
            "Abstract", DynamicColumn.TEXT_BLOCK, 'book_top', 3)
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
            "Postal Code", DynamicColumn.TEXT, 'publisher_top', 6)
        dc1 = self._create_dynamic_column_record(
            "Language", DynamicColumn.CHOICE, 'book_center', 6, relation=1)
        dc2 = self._create_dynamic_column_record(
            "Web Site", DynamicColumn.TEXT, 'author_top', 1)
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
            "Author", DynamicColumn.CHOICE, 'book_top', 1, relation=3)
        dc1 = self._create_dynamic_column_record(
            "Publisher", DynamicColumn.CHOICE, 'book_top', 2, relation=4)
        dc2 = self._create_dynamic_column_record(
            "Abstract", DynamicColumn.TEXT_BLOCK, 'book_top', 3)
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

    def test_get_active_relation_items(self):
        """
        Test that a list of related item strings is returned.
        """
        #self.skipTest("Temporarily skipped")
        # Create two choice items.
        dc0 = self._create_dynamic_column_record(
            "Author", DynamicColumn.CHOICE, 'book_top', 1, relation=3)
        dc1 = self._create_dynamic_column_record(
            "Publisher", DynamicColumn.CHOICE, 'book_top', 2, relation=4)
        # Add to a collection.
        cc0 = self._create_column_collection_record(
            "Books", dynamic_columns=[dc0, dc1])
        # Test get_active_relation_items
        result = ColumnCollection.objects.get_active_relation_items('Books')
        msg = "result: {}".format(result)

        for name in ("Author", "Publisher",):
            self.assertTrue(name in result, msg)

    def test_get_collection_choices(self):
        """
        """
        #self.skipTest("Temporarily skipped")
        # Create a few dynamic columns.
        dc0 = self._create_dynamic_column_record(
            "Author", DynamicColumn.CHOICE, 'book_top', 1, relation=3)
        dc1 = self._create_dynamic_column_record(
            "Publisher", DynamicColumn.CHOICE, 'book_top', 2, relation=4)
        dc2 = self._create_dynamic_column_record(
            "Abstract", DynamicColumn.TEXT_BLOCK, 'book_top', 3)
        # Add to a collection.
        cc0 = self._create_column_collection_record(
            "Books", dynamic_columns=[dc0, dc1, dc2])
        # Test get_collection_choices using slugs.
        result = ColumnCollection.objects.get_collection_choices('Books')
        msg = "result: {}".format(result)

        for key, value in (('author', 'Author'),
                           ('publisher', 'Publisher'),
                           ('abstract', 'Abstract')):
            self.assertTrue(key in dict(result), msg)
            self.assertTrue(value in dict(result).values(), msg)

        # Test get_collection_choices using pks.
        result = ColumnCollection.objects.get_collection_choices(
            'Books', use_pk=True)
        msg = "result: {}".format(result)

        for key, value in ((dc0.pk, 'Author'),
                           (dc1.pk, 'Publisher'),
                           (dc2.pk, 'Abstract')):
            self.assertTrue(key in dict(result), msg)
            self.assertTrue(value in dict(result).values(), msg)


class TestCollectionBase(BaseDcolumns):

    def __init__(self, name):
        super(TestCollectionBase, self).__init__(name)

    def test_serialize_columns(self):
        """
        Finish testing Collection.serialize_columns. Check that the dynamic
        columns get serialized properly.
        """
        #self.skipTest("Temporarily skipped")
        # Create a few dynamic columns.
        field0 = "Author"
        field1 = "Publisher"
        field2 = "Abstract"
        dc0 = self._create_dynamic_column_record(
            field0, DynamicColumn.CHOICE, 'book_top', 1, relation=3)
        dc1 = self._create_dynamic_column_record(
            field1, DynamicColumn.CHOICE, 'book_top', 2, relation=4)
        dc2 = self._create_dynamic_column_record(
            field2, DynamicColumn.TEXT_BLOCK, 'book_top', 3)
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
        kv0 = self._create_key_value_record(book, dc0, author.pk)
        kv1 = self._create_key_value_record(book, dc1, publisher.pk)
        kv2 = self._create_key_value_record(book, dc2, "Test for Abstract.")
        # Get serialized object.
        result = ColumnCollection.objects.serialize_columns('Books', obj=book)
        msg = "result: {}".format(result)
        dc_records = {dc0.pk: field0, dc1.pk: field1, dc2.pk: field2}

        for pk, dc_name in dc_records.items():
            name = result.get(pk).get('name')
            self.assertEqual(dc_name, name, msg)

    def test_get_all_slugs(self):
        """
        Test that all dynamic column slugs are returned in a list.
        """
        #self.skipTest("Temporarily skipped")
        # Create a few dynamic columns.
        dc0 = self._create_dynamic_column_record(
            "Author", DynamicColumn.CHOICE, 'book_top', 1, relation=3)
        dc1 = self._create_dynamic_column_record(
            "Publisher", DynamicColumn.CHOICE, 'book_top', 2, relation=4)
        dc2 = self._create_dynamic_column_record(
            "Abstract", DynamicColumn.TEXT_BLOCK, 'book_top', 3)
        # Add to a collection.
        cc0 = self._create_column_collection_record(
            "Books", dynamic_columns=[dc0, dc1, dc2])
        # Test get_all_slugs
        result = Book.objects.get_all_slugs()
        msg = "result: {}".format(result)
        self.assertEqual(len(result), 3, msg)

    def test_get_all_fields(self):
        """
        Test that all field names are returned in a list.
        """
        #self.skipTest("Temporarily skipped")
        # Create a few dynamic columns.
        dc0 = self._create_dynamic_column_record(
            "Author", DynamicColumn.CHOICE, 'book_top', 1, relation=3)
        dc1 = self._create_dynamic_column_record(
            "Publisher", DynamicColumn.CHOICE, 'book_top', 2, relation=4)
        dc2 = self._create_dynamic_column_record(
            "Abstract", DynamicColumn.TEXT_BLOCK, 'book_top', 3)
        # Add to a collection.
        cc0 = self._create_column_collection_record(
            "Books", dynamic_columns=[dc0, dc1, dc2])
        # Test get_all_slugs
        result = Book.objects.get_all_fields()
        msg = "result: {}".format(result)
        self.assertEqual(len(result), 7, msg)

    def test_get_all_fields_and_slugs(self):
        """
        Test that all field names and dynamic column slugs are returned in a
        sorted list.
        """
        #self.skipTest("Temporarily skipped")
        # Create a few dynamic columns.
        dc0 = self._create_dynamic_column_record(
            "Author", DynamicColumn.CHOICE, 'book_top', 1, relation=3)
        dc1 = self._create_dynamic_column_record(
            "Publisher", DynamicColumn.CHOICE, 'book_top', 2, relation=4)
        dc2 = self._create_dynamic_column_record(
            "Abstract", DynamicColumn.TEXT_BLOCK, 'book_top', 3)
        # Add to a collection.
        cc0 = self._create_column_collection_record(
            "Books", dynamic_columns=[dc0, dc1, dc2])
        # Test get_all_slugs
        result = Book.objects.get_all_fields_and_slugs()
        msg = "result: {}".format(result)
        self.assertEqual(len(result), 10, msg)

    def test_serialize_key_value_pairs(self):
        """
        Test that the key valie pairs get serialized in a dict.
        """
        #self.skipTest("Temporarily skipped")
        author, a_values = self._create_author_objects()
        publisher, p_values = self._create_publisher_objects()
        book, b_values = self._create_book_objects(
            author_pk=author.pk, publisher_pk=publisher.pk)
        result = book.serialize_key_value_pairs(by_slug=True)
        msg = "result: {}".format(result)

        for key, value in result.items():
            self.assertEqual(value, b_values.get(key), msg)

        self.assertEqual(len(result), len(b_values), msg)

        # TODO Addetest for by_slug.

    def test_get_dynamic_column(self):
        """
        Test that the dynamic column is returned when it's slug is passed.
        """
        #self.skipTest("Temporarily skipped")
        book, b_values = self._create_book_objects()
        obj = book.get_dynamic_column('abstract')
        msg = "obj.name: {}, obj.value_type: {}".format(
            obj.name, obj.value_type)
        self.assertEqual(obj.name, 'Abstract', msg)
        self.assertEqual(obj.value_type, DynamicColumn.TEXT_BLOCK, msg)

    def test_get_key_value_pair(self):
        """
        Check that the value of the KeyValue object is returned.
        """
        #self.skipTest("Temporarily skipped")
        # Create a book object.
        author, a_values = self._create_author_objects()
        promotion, p_values = self._create_promotion_objects()
        language = Language()
        book, b_values = self._create_book_objects(
            author_pk=author.pk, promotion_pk=promotion.pk,
            language_pk=language.pk)
        # Test Choice ForeignKey mode with store_relation set to False.
        slug = 'author'
        value = book.get_key_value_pair(slug)
        msg = "value: {}, b_values: {}, a_values: {}, author.name: {}".format(
            value, b_values, a_values, author.name)
        self.assertEqual(value, author.name, msg)
        # Test Choice mode with store_relation set to True.
        slug = 'promotion'
        value = book.get_key_value_pair(slug)
        msg = "value: {}, b_values: {}, p_values: {}".format(
            value, b_values, p_values)
        self.assertEqual(value, b_values.get(slug), msg)
        # Test TIME
        
        # Test DATE

        # Test DATETIME

        # Test BOOLEAN

        # Test NUMBER

        # Test FLOAT

        # Test TEXT

        # Test TEXT_BLOCK
        slug = 'abstract'
        value = book.get_key_value_pair(slug)
        msg = "value: {}, b_values: {}".format(value, b_values)
        self.assertEqual(value, b_values.get(slug), msg)
        # Test that an empty string is returned for a bad slug.
        value = book.get_key_value_pair('not-a-slug')
        msg = "value: {}, b_values: {}".format(value, b_values)
        self.assertEqual(value, '', msg)










    def test_set_key_value_pair(self):
        """
        """
        #self.skipTest("Temporarily skipped")
        # Add a numeric column to books.
        dc0 = self._create_dynamic_column_record(
            "Edition", DynamicColumn.NUMBER, 'book_top', 4)
        book, b_values = self._create_book_objects(extra_dcs=[dc0])
        value = 0
        kv0 = self._create_key_value_record(book, dc0, value)
        b_values[dc0.slug] = value
        # Update the edition (normal numeric case).
        new_value = 1
        book.set_key_value_pair('edition', new_value)
        found_value = book.get_key_value_pair('edition')
        msg = "Initial value: {}, found_value: {}, new_found: {}".format(
            value, found_value, new_value)
        self.assertEqual(found_value, new_value, msg)
        # Update the edition by `increment` on a number.
        book.set_key_value_pair('edition', 'increment')
        found_value = book.get_key_value_pair('edition')
        msg = "Initial value: {}, found_value: {}, new_found: {}".format(
            value, found_value, 2)
        self.assertEqual(found_value, 2, msg)
        # Update the edition by `decrement` on a number.
        book.set_key_value_pair('edition', 'decrement')
        found_value = book.get_key_value_pair('edition')
        msg = "Initial value: {}, found_value: {}, new_found: {}".format(
            value, found_value, 1)
        self.assertEqual(found_value, 1, msg)
        # Update the abstract (normal text case).
        new_value = "A new abstract"
        book.set_key_value_pair('abstract', new_value)
        found_value = book.get_key_value_pair('abstract')
        msg = "Initial value: {}, found_value: {}, new_found: {}".format(
            value, found_value, new_value)
        self.assertEqual(found_value, new_value, msg)
        # 




    # Go back and put the methods below into previous tests.




    def _create_author_objects(self):
        """
        Create  a set of Author objects.
        """
        dcs = []
        dc0 = self._create_dynamic_column_record(
            "Web Site", DynamicColumn.TEXT, 'author_top', 1)
        dcs.append(dc0)
        # Add to a collection.
        cc = self._create_column_collection_record(
            "Authors", dynamic_columns=dcs)
        # Create a book entry.
        author = self._create_dcolumn_record(
            Author, cc, name='Pickup Andropoff')
        value = "example.org"
        kv0 = self._create_key_value_record(author, dc0, value)
        return author, {dc0.slug: kv0.value}

    def _create_publisher_objects(self):
        """
        Create  a set of Publisher objects.
        """
        dcs = []
        dc0 = self._create_dynamic_column_record(
            "Web Site", DynamicColumn.TEXT, 'publisher_top', 1)
        dcs.append(dc0)
        # Add to a collection.
        cc = self._create_column_collection_record(
            "Publishers", dynamic_columns=dcs)
        # Create a book entry.
        publisher = self._create_dcolumn_record(
            Publisher, cc, name='Some big Publisher')
        value = "example.org"
        kv0 = self._create_key_value_record(publisher, dc0, value)
        return publisher, {dc0.slug: kv0.value}

    def _create_promotion_objects(self):
        """
        Create  a set of Promotion objects.
        """
        dcs = []
        # Create promotion description
        dc0 = self._create_dynamic_column_record(
            "Description", DynamicColumn.TEXT, 'publisher_top', 1)
        dcs.append(dc0)
        # Create promotion start date.
        dc1 = self._create_dynamic_column_record(
            "Start Date", DynamicColumn.TIME, 'publisher_top', 2)
        dcs.append(dc1)
        # Create promotion start time.
        dc2 = self._create_dynamic_column_record(
            "Start Time", DynamicColumn.TIME, 'publisher_top', 3)
        dcs.append(dc2)
        # Add to a collection.
        cc = self._create_column_collection_record(
            "Promotion", dynamic_columns=dcs)
        # Create a book entry.
        promotion = self._create_dcolumn_record(
            Promotion, cc, name='Promotion')
        value = "50% off everything for ever."
        kv0 = self._create_key_value_record(promotion, dc0, value)
        value = datetime.date.today().isoformat()
        kv1 = self._create_key_value_record(promotion, dc1, value)
        value = datetime.time(hour=12, minute=0, second=0).isoformat()
        kv2 = self._create_key_value_record(promotion, dc2, value)
        return promotion, {dc0.slug: kv0.value, dc1.slug: kv1.value,
                           dc2.slug: kv2.value}

    def _create_book_objects(self, author_pk=0, publisher_pk=0, promotion_pk=0,
                             language_pk=0, extra_dcs=[]):
        """
        Create  a set of Book objects.
        """
        if extra_dcs:
            dcs = extra_dcs
        else:
            dcs = []

        dc0 = self._create_dynamic_column_record(
            "Abstract", DynamicColumn.TEXT_BLOCK, 'book_top', 3)
        dcs.append(dc0)

        if author_pk: # Database table
            dc1 = self._create_dynamic_column_record(
                "Author", DynamicColumn.CHOICE, 'book_top', 1, relation=3)
            dcs.append(dc1)

        if publisher_pk: # Database table
            dc2 = self._create_dynamic_column_record(
                "Publisher", DynamicColumn.CHOICE, 'book_top', 2, relation=4)
            dcs.append(dc2)

        if promotion_pk: # Database table
            dc3 = self._create_dynamic_column_record(
                "Promotion", DynamicColumn.CHOICE, 'book_top', 3, relation=5,
                store_relation=DynamicColumn.YES)
            dcs.append(dc3)

        if language_pk: # Choice object
            dc4 =self._create_dynamic_column_record(
                "Language", DynamicColumn.CHOICE, 'book_top', 4, relation=6)
            dcs.append(dc4)

        # Add to a collection.
        cc = self._create_column_collection_record(
            "Books", dynamic_columns=dcs)
        # Create a book entry.
        book = self._create_dcolumn_record(Book, cc, title='Test Book')
        value = "Very very short abstract"
        kv0 = self._create_key_value_record(book, dc0, value)
        values = {dc0.slug: value}

        if author_pk:
            kv1 = self._create_key_value_record(book, dc1, author_pk)
            values[dc1.slug] = kv1.value

        if publisher_pk:
            kv2 = self._create_key_value_record(book, dc2, publisher_pk)
            values[dc2.slug] = kv2.value

        if promotion_pk:
            kv3 = self._create_key_value_record(book, dc3, promotion_pk)
            values[dc3.slug] = kv3.value

        if language_pk:
            kv4 = self._create_key_value_record(book, dc4, language_pk)
            values[dc4.slug] = kv4.value

        return book, values
