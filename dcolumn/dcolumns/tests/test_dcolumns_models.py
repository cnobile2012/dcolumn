# -*- coding: utf-8 -*-
#
# dcolumn/dcolumns/tests/test_dcolumns_models.py
#
# WARNING: These unittests can only be run from within the original test
#          framework from https://github.com/cnobile2012/dcolumn.
#
import datetime
import dateutil
import pytz

from django.core.exceptions import ValidationError

from example_site.books.choices import Language
from example_site.books.models import Author, Book, Publisher, Promotion

from ..models import DynamicColumn, ColumnCollection, KeyValue
from .base_tests import BaseDcolumns


class TestDynamicColumn(BaseDcolumns):

    def __init__(self, name):
        super(TestDynamicColumn, self).__init__(name)

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
            "Language", DynamicColumn.CHOICE, 'book_center', 6,
            relation=self.choice2index.get("Language"))
        slugs = DynamicColumn.objects.get_fk_slugs()
        msg = "slugs: {}".format(slugs)
        self.assertEqual(len(slugs), 1, msg)

    def test_relation_producer(self):
        """
        Test that this method returns the correct relation type for the
        database int value. Used in the Django admin.
        """
        #self.skipTest("Temporarily skipped")
        # Create two DynamicColumn objects.
        dc0 = self._create_dynamic_column_record(
            "Postal Code", DynamicColumn.TEXT, 'publisher_top', 1)
        dc1 = self._create_dynamic_column_record(
            "Language", DynamicColumn.CHOICE, 'book_center', 1,
            relation=self.choice2index.get("Language"))
        require = {dc0: '', dc1: "Language"}

        for dc, value in require.items():
            result = dc.relation_producer()
            msg = "value: {}, result: {}".format(value, result)
            self.assertEqual(value, result, msg)

    def test_collection_producer(self):
        """
        Test that the correct ``Collection`` name is returned for this
        ``DynamicColumn``.
        """
        #self.skipTest("Temporarily skipped")
        # Create a DynamicColumn object.
        dc0 = self._create_dynamic_column_record(
            "Postal Code", DynamicColumn.TEXT, 'publisher_top', 1)
        cc_name = "Publisher"
        cc = self._create_column_collection_record(
            cc_name, 'publisher', dynamic_columns=[dc0])
        result = dc0.collection_producer()
        value = '<span>{}</span>'.format(cc_name)
        msg = "value {}, result".format(value, result)
        self.assertEqual(value, result, msg)

    def test_updater_producer(self):
        """
        Test that the updater_producer returns the proper values.
        """
        #self.skipTest("Temporarily skipped")
        # Create a DynamicColumn object.
        dc0 = self._create_dynamic_column_record(
            "Postal Code", DynamicColumn.TEXT, 'publisher_top', 1)
        cc_name = "Publisher"
        cc = self._create_column_collection_record(
            cc_name, 'publisher', dynamic_columns=[dc0])
        # Test that the full name is returned
        result = dc0.updater_producer()
        value = "{} {}".format(self.user.first_name, self.user.last_name)
        msg = "value {}, result".format(value, result)
        self.assertEqual(value, result, msg)
        # Test that the username is returned.
        self.user.last_name = ''
        self.user.first_name = ''
        result = dc0.updater_producer()
        value = "{}".format(self.user.username)
        msg = "value {}, result".format(value, result)
        self.assertEqual(value, result, msg)

    def test_creator_producer(self):
        """
        Test that the creator_producer returns the proper values.
        """
        #self.skipTest("Temporarily skipped")
        # Create a DynamicColumn object.
        dc0 = self._create_dynamic_column_record(
            "Postal Code", DynamicColumn.TEXT, 'publisher_top', 1)
        cc_name = "Publisher"
        cc = self._create_column_collection_record(
            cc_name, 'publisher', dynamic_columns=[dc0])
        # Test that the full name is returned
        result = dc0.creator_producer()
        value = "{} {}".format(self.user.first_name, self.user.last_name)
        msg = "value {}, result".format(value, result)
        self.assertEqual(value, result, msg)
        # Test that the username is returned.
        self.user.last_name = ''
        self.user.first_name = ''
        result = dc0.creator_producer()
        value = "{}".format(self.user.username)
        msg = "value {}, result".format(value, result)
        self.assertEqual(value, result, msg)

    def test_clean(self):
        """
        Test that ``DynamicColumn.preferred_slug`` is populated in
        ``DynamicColumn.slug``. Also test that if a ``DynamicColumn.value_type``
        is a ``CHOICE`` that ``DynamicColumn.relation`` is also set.
        """
        #self.skipTest("Temporarily skipped")
        # Create a DynamicColumn object.
        preferred_slug = 'zip-code'
        dc0 = self._create_dynamic_column_record(
            "Postal Code", DynamicColumn.TEXT, 'publisher_top', 1,
            preferred_slug=preferred_slug)
        dc1 = self._create_dynamic_column_record(
            "Language", DynamicColumn.CHOICE, 'book_center', 1,
            relation=self.choice2index.get("Language"))
        # Test preferred_slug
        msg = "preferred_slug: {}, result".format(preferred_slug, dc0.slug)
        self.assertEqual(preferred_slug, dc0.slug)
        # Test slug
        slug = 'language'
        msg = "slug: {}, result".format(slug, dc1.slug)
        self.assertEqual(slug, dc1.slug)
        # Test CHOICE and not relation
        with self.assertRaises(ValidationError) as cm:
            dc2 = self._create_dynamic_column_record(
                "Author", DynamicColumn.CHOICE, 'book_top', 1)
        # Test relation and not CHOICE
        with self.assertRaises(ValidationError) as cm:
            dc3 = self._create_dynamic_column_record(
                "Author", DynamicColumn.TEXT, 'book_top', 1,
                relation=self.choice2index.get("Author"))
        # Test invalid dynamic column type raises a ValidationError.
        with self.assertRaises(ValidationError) as cm:
            dc4 = self._create_dynamic_column_record(
                "Bad Type", 100, 'book_top', 14)

    def test_get_choice_relation_object_and_field(self):
        """
        Test that the model class object and the correct field.
        """
        #self.skipTest("Temporarily skipped")
        # Create a choice type object.
        dc0 = self._create_dynamic_column_record(
            "Language", DynamicColumn.CHOICE, 'book_center', 6,
            relation=self.choice2index.get("Language"))
        obj, field = dc0.get_choice_relation_object_and_field()
        msg = "obj: %s, field: {}".format(obj, field)
        self.assertTrue(obj == Language, msg)
        self.assertEqual(field, 'name', msg)


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
            "Author", DynamicColumn.CHOICE, 'book_top', 1,
            relation=self.choice2index.get("Author"))
        dc1 = self._create_dynamic_column_record(
            "Publisher", DynamicColumn.CHOICE, 'book_top', 2,
            relation=self.choice2index.get("Publisher"))
        dc2 = self._create_dynamic_column_record(
            "Abstract", DynamicColumn.TEXT_BLOCK, 'book_top', 3)
        # Test that there are no dynamic columns.
        cc = self._create_column_collection_record("Books", 'book')
        msg = "dynamic columns: {!s}".format(cc.dynamic_column.all())
        self.assertEqual(cc.dynamic_column.count(), 0, msg)
        # Test that there is one dynamic column.
        cc.process_dynamic_columns([dc0])
        msg = "dynamic columns: {!s}".format(cc.dynamic_column.all())
        self.assertEqual(cc.dynamic_column.count(), 1, msg)
        # Test that there are two dynamic columns.
        cc.process_dynamic_columns([dc0, dc1])
        msg = "dynamic columns: {!s}".format(cc.dynamic_column.all())
        self.assertEqual(cc.dynamic_column.count(), 2, msg)
        # Test that replacing one dynamic column the results are two.
        cc.process_dynamic_columns([dc1, dc2])
        msg = "dynamic columns: {!s}".format(cc.dynamic_column.all())
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
            "Language", DynamicColumn.CHOICE, 'book_center', 6,
            relation=self.choice2index.get("Language"))
        dc2 = self._create_dynamic_column_record(
            "Web Site", DynamicColumn.TEXT, 'author_top', 1)
        # Add two dynamic columns to the collections.
        cc0 = self._create_column_collection_record(
            'Author', 'author', dynamic_columns=[dc2])
        cc1 = self._create_column_collection_record(
            'Publisher', 'publisher', dynamic_columns=[dc0])
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
        # Test that the DoesNotExist gets raised when an invalid column
        # collection name is provided.
        with self.assertRaises(ColumnCollection.DoesNotExist) as cm:
            ColumnCollection.objects.get_column_collection('BadModelName')

    def test_serialize_columns(self):
        """
        Test the serialization of a collection's dynamic columns.
        """
        #self.skipTest("Temporarily skipped")
        # Create a few dynamic columns.
        dc0 = self._create_dynamic_column_record(
            "Author", DynamicColumn.CHOICE, 'book_top', 1,
            relation=self.choice2index.get("Author"))
        dc1 = self._create_dynamic_column_record(
            "Publisher", DynamicColumn.CHOICE, 'book_top', 2,
            relation=self.choice2index.get("Publisher"))
        dc2 = self._create_dynamic_column_record(
            "Abstract", DynamicColumn.TEXT_BLOCK, 'book_top', 3)
        # Test that the serialized object is correct using pks and has no value.
        cc0 = self._create_column_collection_record(
            "Books", 'book', dynamic_columns=[dc0, dc1, dc2])
        result = ColumnCollection.objects.serialize_columns('book')
        msg = "result: {}".format(result)

        for pk in (dc0.pk, dc1.pk, dc2.pk):
            self.assertTrue(pk in result, msg)
            # Test that the value is not included.
            self.assertEquals(result[pk].get('value'), None, msg)

        # Test that the serialized oject is correct using slugs and has no
        # value.
        result = ColumnCollection.objects.serialize_columns(
            'book', by_slug=True)
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
            "Author", DynamicColumn.CHOICE, 'book_top', 1,
            relation=self.choice2index.get("Author"))
        dc1 = self._create_dynamic_column_record(
            "Publisher", DynamicColumn.CHOICE, 'book_top', 2,
            relation=self.choice2index.get("Publisher"))
        # Add to a collection.
        cc0 = self._create_column_collection_record(
            "Books", 'book', dynamic_columns=[dc0, dc1])
        # Test get_active_relation_items
        result = ColumnCollection.objects.get_active_relation_items('book')
        msg = "result: {}".format(result)

        for name in ("Author", "Publisher",):
            self.assertTrue(name in result, msg)

    def test_get_collection_choices(self):
        """
        """
        #self.skipTest("Temporarily skipped")
        # Create a few dynamic columns.
        dc0 = self._create_dynamic_column_record(
            "Author", DynamicColumn.CHOICE, 'book_top', 1,
            relation=self.choice2index.get("Author"))
        dc1 = self._create_dynamic_column_record(
            "Publisher", DynamicColumn.CHOICE, 'book_top', 2,
            relation=self.choice2index.get("Publisher"))
        dc2 = self._create_dynamic_column_record(
            "Abstract", DynamicColumn.TEXT_BLOCK, 'book_top', 3)
        # Add to a collection.
        cc0 = self._create_column_collection_record(
            "Books", 'book', dynamic_columns=[dc0, dc1, dc2])
        # Test get_collection_choices using slugs.
        result = ColumnCollection.objects.get_collection_choices('book')
        msg = "result: {}".format(result)

        for key, value in (('author', 'Author'),
                           ('publisher', 'Publisher'),
                           ('abstract', 'Abstract')):
            self.assertTrue(key in dict(result), msg)
            self.assertTrue(value in dict(result).values(), msg)

        # Test get_collection_choices using pks.
        result = ColumnCollection.objects.get_collection_choices(
            'book', use_pk=True)
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
        # Create a few book objects.
        author, a_cc, a_values = self._create_author_objects()
        promotion, p_cc, p_values = self._create_promotion_objects()
        book, b_cc, b_values = self._create_book_objects(
            author=author, promotion=promotion)
        # Get serialized object.
        result = ColumnCollection.objects.serialize_columns(
            'book', obj=book, by_slug=True)
        msg = "result: {}, b_values: {}".format(result, b_values)

        for slug, dc_value in b_values.items():
            value = result.get(slug).get('value')
            self.assertEqual(value, dc_value, msg)

    def test_model_objects(self):
        """
        Test that the correct object types get returned.
        """
        #self.skipTest("Temporarily skipped")
        # Create a few book objects.
        author, a_cc, a_values = self._create_author_objects()
        promotion, p_cc, p_values = self._create_promotion_objects()
        book, b_cc, b_values = self._create_book_objects(
            author=author, promotion=promotion)
        # Get object list.
        result = Book.objects.model_objects()
        msg = "result: {}, book: {}".format(result, book)

        for record in result:
            self.assertEqual(record.title, book.title, msg)

    def test_get_choice(self):
        """
        Test that a valid list of HTML select option choices are returned both
        with and without a header option.
        """
        #self.skipTest("Temporarily skipped")
        # Create a few book objects.
        author, a_cc, a_values = self._create_author_objects()
        promotion, p_cc, p_values = self._create_promotion_objects()
        book, b_cc, b_values = self._create_book_objects(
            author=author, promotion=promotion)
        # Test that a book and HTML select option header is returned.
        result = Book.objects.get_choices('title')
        msg = "result: {}, book: {}".format(result, book)
        self.assertTrue(0 in dict(result), msg)
        self.assertEqual(dict(result).get(book.pk), book.title, msg)
        # Test that a book and HTML select option header is not returned.
        result = Book.objects.get_choices('title', comment=False)
        msg = "result: {}, book: {}".format(result, book)
        self.assertFalse(0 in dict(result), msg)
        self.assertEqual(dict(result).get(book.pk), book.title, msg)

    def test_get_value_by_pk(self):
        """
        Test that a value is returned based on the objects pk.
        """
        #self.skipTest("Temporarily skipped")
        # Create a few book objects.
        author, a_cc, a_values = self._create_author_objects()
        promotion, p_cc, p_values = self._create_promotion_objects()
        book, b_cc, b_values = self._create_book_objects(
            author=author, promotion=promotion)
        # Test for normal operation.
        result = Book.objects.get_value_by_pk(book.pk, 'title')
        msg = "result: {}".format(result)
        self.assertEqual(result, book.title, msg)
        # Test that an exception is raised with invalid PK.
        with self.assertRaises(Book.DoesNotExist) as cm:
            Book.objects.get_value_by_pk(5000, 'title')
        # Test that an exception is raised with an invalid field argument.
        with self.assertRaises(AttributeError) as cm:
            Book.objects.get_value_by_pk(book.pk, 'bad_field')

    def test_get_all_slugs(self):
        """
        Test that all dynamic column slugs are returned in a list.
        """
        #self.skipTest("Temporarily skipped")
        # Create a few book objects.
        author, a_cc, a_values = self._create_author_objects()
        promotion, p_cc, p_values = self._create_promotion_objects()
        book, b_cc, b_values = self._create_book_objects(
            author=author, promotion=promotion)
        # Test get_all_slugs
        result = Book.objects.get_all_slugs()
        msg = "result: {}, b_values: {}".format(result, b_values)
        self.assertEqual(len(result), len(b_values), msg)

    def test_get_all_fields(self):
        """
        Test that all field names are returned in a list.
        """
        #self.skipTest("Temporarily skipped")
        # Create a few book objects.
        author, a_cc, a_values = self._create_author_objects()
        promotion, p_cc, p_values = self._create_promotion_objects()
        book, b_cc, b_values = self._create_book_objects(
            author=author, promotion=promotion)
        # Test get_all_fields.
        result = Book.objects.get_all_fields()
        msg = "result: {}".format(result)
        self.assertEqual(len(result), 7, msg)

    def test_get_all_fields_and_slugs(self):
        """
        Test that all field names and dynamic column slugs are returned in a
        sorted list for the requested model.
        """
        #self.skipTest("Temporarily skipped")
        # Create a few book objects.
        author, a_cc, a_values = self._create_author_objects()
        promotion, p_cc, p_values = self._create_promotion_objects()
        book, b_cc, b_values = self._create_book_objects(
            author=author, promotion=promotion)
        # Test get_all_fields_and_slugs.
        result = Book.objects.get_all_fields_and_slugs()
        msg = "result: {}".format(result)
        self.assertEqual(len(result), 10, msg)

    def test_serialize_key_values(self):
        """
        Test that the key values get serialized in a dict.
        """
        #self.skipTest("Temporarily skipped")
        author, a_cc, a_values = self._create_author_objects()
        publisher, p_cc, p_values = self._create_publisher_objects()
        book, b_cc, b_values = self._create_book_objects(
            author=author, publisher=publisher)
        result = book.serialize_key_values(by_slug=True)
        msg = "result: {}, b_values: {}".format(result, b_values)

        for key, value in result.items():
            self.assertEqual(value, b_values.get(key), msg)

        self.assertEqual(len(result), len(b_values), msg)

        # TODO Addetest for by_slug.

    def test_get_dynamic_column(self):
        """
        Test that the dynamic column is returned when it's slug is passed.
        """
        #self.skipTest("Temporarily skipped")
        book, b_cc, b_values = self._create_book_objects()
        obj = book.get_dynamic_column('abstract')
        msg = "obj.name: {}, obj.value_type: {}".format(
            obj.name, obj.value_type)
        self.assertEqual(obj.name, 'Abstract', msg)
        self.assertEqual(obj.value_type, DynamicColumn.TEXT_BLOCK, msg)

    def test_get_key_value(self):
        """
        Check that all the possible combinations of this method work
        correctly.
        """
        #self.skipTest("Temporarily skipped")
        # Create a book object and lots of dynamic columns.
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
        dc4 = self._create_dynamic_column_record(
            "Bad Bool", DynamicColumn.BOOLEAN, 'book_top', 10)
        dc5 = self._create_dynamic_column_record(
            "Bad Date", DynamicColumn.DATE, 'book_top', 11)
        dc6 = self._create_dynamic_column_record(
            "Bad Number", DynamicColumn.NUMBER, 'book_top', 12)
        dc7 = self._create_dynamic_column_record(
            "Bad Float", DynamicColumn.FLOAT, 'book_top', 13)
        book, b_cc, b_values = self._create_book_objects(
            author=author, promotion=promotion, language=language,
            extra_dcs=[dc0, dc1, dc2, dc3, dc4, dc5, dc6, dc7])
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
        value = 'junk'
        kv4 = self._create_key_value_record(book, dc4, value)
        b_values[dc4.slug] = kv4.value
        value = 'junk'
        kv5 = self._create_key_value_record(book, dc5, value)
        b_values[dc5.slug] = kv5.value
        value = 'junk'
        kv6 = self._create_key_value_record(book, dc6, value)
        b_values[dc6.slug] = kv6.value
        value = 'junk'
        kv7 = self._create_key_value_record(book, dc7, value)
        b_values[dc7.slug] = kv7.value
        # Test Choice mode with store_relation set to True.
        slug = 'promotion'
        value = book.get_key_value(slug)
        msg = "value: {}, b_values: {}, p_values: {}".format(
            value, b_values, p_values)
        self.assertEqual(value, b_values.get(slug), msg)
        # Test Choice ForeignKey mode with store_relation set to False.
        slug = 'author'
        value = book.get_key_value(slug)
        msg = "value: {}, b_values: {}, a_values: {}, author.name: {}".format(
            value, b_values, a_values, author.name)
        self.assertEqual(value, author.name, msg)
        # Test Choice AttributeError exception.
        with self.assertRaises(AttributeError) as cm:
            value = book.get_key_value(slug, 'bad_field')
        # Test Choice ValueError exception.
        with self.assertRaises(TypeError) as cm:
            book.get_key_value(slug, book)
        # Test TIME
        slug = 'start-time'
        value = promotion.get_key_value(slug)
        msg = "value: {}, b_values: {}, p_values: {}".format(
            value, b_values, p_values)
        t = p_values.get(slug)
        self.assertEqual(value, t, msg)
        # Test DATE
        slug = 'start-date'
        value = promotion.get_key_value(slug)
        msg = "value: {}, b_values: {}, p_values: {}".format(
            value, b_values, p_values)
        d = p_values.get(slug)
        self.assertEqual(value, d, msg)
        # Test DATETIME
        slug = 'date-time'
        value = book.get_key_value(slug)
        msg = "value: {}, b_values: {}".format(value, b_values)
        dt = b_values.get(slug)
        self.assertEqual(value, dt, msg)
        # Test BOOLEAN
        slug = 'ignore'
        value = book.get_key_value(slug)
        msg = "value: {}, b_values: {}".format(value, b_values)
        bool_value = True if b_values.get(slug).lower() == 'true' else False
        self.assertEqual(value, bool_value, msg)
        # Test bad BOOLEAN
        slug = 'bad-bool'
        with self.assertRaises(ValueError) as cm:
            value = book.get_key_value(slug)
        # Test NUMBER
        slug = 'edition'
        value = book.get_key_value(slug)
        msg = "value: {}, b_values: {}".format(value, b_values)
        self.assertEqual(value, int(b_values.get(slug)), msg)
        # Test invalid NUMBER.
        slug = 'bad-number'
        with self.assertRaises(ValueError) as cm:
            book.get_key_value(slug)
        # Test FLOAT
        slug = 'percentage'
        value = book.get_key_value(slug)
        msg = "value: {}, b_values: {}".format(value, b_values)
        self.assertEqual(value, float(b_values.get(slug)), msg)
        # Test invalid FLOAT.
        slug = 'bad-float'
        with self.assertRaises(ValueError) as cm:
            book.get_key_value(slug)
        # Test TEXT
        slug = 'description'
        value = promotion.get_key_value(slug)
        msg = "value: {}, b_values: {}, p_values: {}".format(
            value, b_values, p_values)
        self.assertEqual(value, p_values.get(slug), msg)
        # Test TEXT_BLOCK
        slug = 'abstract'
        value = book.get_key_value(slug)
        msg = "value: {}, b_values: {}".format(value, b_values)
        self.assertEqual(value, b_values.get(slug), msg)
        # Test that an empty string is returned for a bad slug.
        value = book.get_key_value('not-a-slug')
        msg = "value: {}, b_values: {}".format(value, b_values)
        self.assertEqual(value, '', msg)
        # Test invalid value other that a bad bolean.
        slug = 'bad-date'
        with self.assertRaises(ValueError) as cm:
            value = book.get_key_value(slug)

    def _create_test_objects(self):
        # Add a few columns to author, promotion, and book.
        language = Language.objects.model_objects()[3] # Russian
        author, a_cc, a_values = self._create_author_objects()
        new_author = self._create_dcolumn_record(
            Author, a_cc, name="Sr. Walter Raleigh")
        promotion, p_cc, p_values = self._create_promotion_objects()
        new_promotion = self._create_dcolumn_record(
            Promotion, p_cc, name="100% off nothing.")
        dc0 = self._create_dynamic_column_record(
            "Edition", DynamicColumn.NUMBER, 'book_top', 4)
        dc1 = self._create_dynamic_column_record(
            "Date & Time", DynamicColumn.DATETIME, 'book_top', 5)
        dc2 = self._create_dynamic_column_record(
            "Ignore", DynamicColumn.BOOLEAN, 'book_top', 6)
        dc3 = self._create_dynamic_column_record(
            "Percentage", DynamicColumn.FLOAT, 'book_top', 7)
        # Web Site gets created, so no KeyValue is pre-created.
        dc4 = self._create_dynamic_column_record(
            "Web Site", DynamicColumn.TEXT, 'book_top', 8)
        book, b_cc, b_values = self._create_book_objects(
            author=author, promotion=promotion, language=language,
            extra_dcs=[dc0, dc1, dc2, dc3, dc4])
        value = 0
        kv0 = self._create_key_value_record(book, dc0, value)
        b_values[dc0.slug] = kv0.value
        value = datetime.datetime.now(pytz.utc).isoformat()
        kv1 = self._create_key_value_record(book, dc1, value)
        b_values[dc1.slug] = kv1.value
        value = 'FALSE'
        kv2 = self._create_key_value_record(book, dc2, value)
        b_values[dc2.slug] = kv2.value
        value = 20.5
        kv3 = self._create_key_value_record(book, dc3, value)
        b_values[dc3.slug] = kv3.value
        return (book, b_values, author, a_values, new_author, promotion,
                p_values, new_promotion, language)

    def test_set_key_value_exceptions(self):
        """
        Check that exceptions are raised correctly.
        """
        #self.skipTest("Temporarily skipped")
        # Get the test objects
        (book, b_values, author, a_values, new_author, promotion, p_values,
         new_promotion, language) = self._create_test_objects()
        # Test general error condition.
        slug = 'bad-slug'
        value = 'Should never get set.'
        with self.assertRaises(ValueError) as cm:
            book.set_key_value(slug, value)
        # Test for exception when invalid arguments are passed.
        value = None
        force = True
        with self.assertRaises(ValueError) as cm:
            book.set_key_value(slug, value, force=force)

    def test_set_key_value_CHOICE(self):
        """
        Check that the CHOICE type works correctly.
        """
        #self.skipTest("Temporarily skipped")
        # Get the test objects
        (book, b_values, author, a_values, new_author, promotion, p_values,
         new_promotion, language) = self._create_test_objects()
        # Test Choice ValueError exception.
        slug = 'author'
        with self.assertRaises(ValueError) as cm:
            book.set_key_value(slug, 'bad-data')
        # Test CHOICE ForeignKey mode with store_relation set to False.
        slug = 'author'
        book.set_key_value(slug, new_author)
        found_value = book.get_key_value(slug)
        msg = "Initial value: {}, found_value: {}, new_pk: {}".format(
            author.pk, found_value, new_author.pk)
        self.assertEqual(found_value, new_author.name, msg)
        # Test CHOICE mode with an integer pk value from a KeyValue record.
        book.set_key_value(slug, author.pk)
        found_value = book.get_key_value(slug)
        msg = ("Initial value: {}, found_value: {}, new_pk: {}, values: {}"
               ).format(new_author.name, found_value, author.name, b_values)
        self.assertEqual(found_value, author.name, msg)
        # Test CHOICE mode with a string pk value from a KeyValue record.
        book.set_key_value(slug, str(new_author.pk))
        found_value = book.get_key_value(slug)
        msg = ("Initial value: {}, found_value: {}, new_pk: {}, values: {}"
               ).format(author.name, found_value, new_author.name, b_values)
        self.assertEqual(found_value, new_author.name, msg)
        # Test CHOICE mode with store_relation set to True.
        slug = 'promotion'
        book.set_key_value(slug, new_promotion)
        found_value = book.get_key_value(slug)
        msg = "Initial value: {}, found_value: {}, new_pk: {}".format(
            promotion.name, found_value, new_promotion.name)
        self.assertEqual(found_value, new_promotion.name, msg)
        # Test that an alternate field can be set.
        slug = 'language'
        value = 'Russian'
        book.set_key_value(slug, language)
        found_value = book.get_key_value(slug, field='name')
        msg = "Initial value: {}, found_value: {}, new_pk: {}".format(
            language.name, found_value, value)
        self.assertEqual(found_value, value, msg)

    def test_set_key_value_TIME(self):
        """
        Check that the TIME type works correctly.
        """
        #self.skipTest("Temporarily skipped")
        # Get the test objects
        (book, b_values, author, a_values, new_author, promotion, p_values,
         new_promotion, language) = self._create_test_objects()
        # Test TIME
        slug = 'start-time'
        dt = datetime.datetime.now(pytz.utc)
        time = datetime.time(hour=dt.hour, minute=dt.minute, second=dt.second,
                             microsecond=dt.microsecond, tzinfo=dt.tzinfo)
        promotion.set_key_value(slug, time)
        found_value = promotion.get_key_value(slug)
        msg = "Initial value: {}, found_value: {}, new_time: {}".format(
            p_values.get(slug), found_value, time)
        self.assertEqual(found_value, time, msg)

    def test_set_key_value_DATE(self):
        """
        Check that the DATE type works correctly.
        """
        #self.skipTest("Temporarily skipped")
        # Get the test objects
        (book, b_values, author, a_values, new_author, promotion, p_values,
         new_promotion, language) = self._create_test_objects()
        # Test DATE with object
        slug = 'start-date'
        date = datetime.date.today() + datetime.timedelta(days=1)
        promotion.set_key_value(slug, date)
        found_value = promotion.get_key_value(slug)
        msg = "Initial value: {}, found_value: {}, new_date: {}".format(
            p_values.get(slug), found_value, date)
        self.assertEqual(found_value, date, msg)
        # Test DATE with string
        slug = 'start-date'
        date = '2015-01-01'
        dt = dateutil.parser.parse(date)
        parsed_date = datetime.date(year=dt.year, month=dt.month, day=dt.day)
        promotion.set_key_value(slug, date)
        found_value = promotion.get_key_value(slug)
        msg = "Initial value: {}, found_value: {}, new_date: {}".format(
            p_values.get(slug), found_value, parsed_date)
        self.assertEqual(found_value, parsed_date, msg)
        # Test DATE with bad date string
        slug = 'start-date'
        date = '2015-13-01'
        with self.assertRaises(ValueError) as cm:
            promotion.set_key_value(slug, date)
        # Test DATE with garbage text string.
        slug = 'start-date'
        date = 'garbage string'
        with self.assertRaises(ValueError) as cm:
            promotion.set_key_value(slug, date)

    def test_set_key_value_DATETIME(self):
        """
        Check that the DATETIME type works correctly.
        """
        #self.skipTest("Temporarily skipped")
        # Get the test objects
        (book, b_values, author, a_values, new_author, promotion, p_values,
         new_promotion, language) = self._create_test_objects()
        # Test Choice ValueError exception.
        slug = 'date-time'
        with self.assertRaises(ValueError) as cm:
            book.set_key_value(slug, 2000)
        # Test DATETIME
        dt = datetime.datetime.now(pytz.utc)
        book.set_key_value(slug, dt)
        found_value = book.get_key_value(slug)
        msg = "Initial value: {}, found_value: {}, new_datetime: {}".format(
            b_values.get(slug), found_value, dt)
        self.assertEqual(found_value, dt, msg)

    def test_set_key_value_BOOLEAN(self):
        """
        Check that the BOOLEAN type works correctly.
        """
        #self.skipTest("Temporarily skipped")
        # Get the test objects
        (book, b_values, author, a_values, new_author, promotion, p_values,
         new_promotion, language) = self._create_test_objects()
        slug = 'ignore'
        # Test BOOLEAN ValueError exception with a string that cannot be
        # converted to a boolead.
        with self.assertRaises(ValueError) as cm:
            book.set_key_value(slug, 'bad-data')
        # Test BOOLEAN ValueError exception with an object.
        with self.assertRaises(ValueError) as cm:
            book.set_key_value(slug, book)
        # Test BOOLEAN with a boolean.
        value = False
        book.set_key_value(slug, value)
        found_value = book.get_key_value(slug)
        msg = "Initial value: {}, found_value: {}, new_bool: {}".format(
            b_values.get(slug), found_value, value)
        self.assertEqual(found_value, False, msg)
        # Test BOOLEAN numeric
        value = 1
        book.set_key_value(slug, value)
        found_value = book.get_key_value(slug)
        msg = "Initial value: {}, found_value: {}, new_bool: {}".format(
            b_values.get(slug), found_value, value)
        self.assertEqual(found_value, True, msg)
        # Test BOOLEAN text True or False
        value = 'TRUE'
        book.set_key_value(slug, value)
        found_value = book.get_key_value(slug)
        msg = "Initial value: {}, found_value: {}, new_bool: {}".format(
            b_values.get(slug), found_value, value)
        self.assertEqual(found_value, True, msg)
        # Test BOOLEAN text numeric 0
        value = '0'
        book.set_key_value(slug, value)
        found_value = book.get_key_value(slug)
        msg = "Initial value: {}, found_value: {}, new_bool: {}".format(
            b_values.get(slug), found_value, value)
        self.assertEqual(found_value, False, msg)
        # Test BOOLEAN text numeric 2000
        value = '2000'
        book.set_key_value(slug, value)
        found_value = book.get_key_value(slug)
        msg = "Initial value: {}, found_value: {}, new_bool: {}".format(
            b_values.get(slug), found_value, value)
        self.assertEqual(found_value, True, msg)

    def test_set_key_value_FLOAT(self):
        """
        Check that the FLOAT type works correctly.
        """
        #self.skipTest("Temporarily skipped")
        # Get the test objects
        (book, b_values, author, a_values, new_author, promotion, p_values,
         new_promotion, language) = self._create_test_objects()
        # Test FLOAT ValueError exception with an integer.
        slug = 'percentage'
        value = book
        with self.assertRaises(ValueError) as cm:
            book.set_key_value(slug, value)
        # Test FLOAT with a real float
        value = 30.0
        book.set_key_value(slug, value)
        found_value = book.get_key_value(slug)
        msg = "Initial value: {}, found_value: {}, new_float: {}".format(
            b_values.get(slug), found_value, value)
        self.assertEqual(found_value, value, msg)
        # Test FLOAT with string value.
        value = '20.5'
        book.set_key_value(slug, value)
        found_value = book.get_key_value(slug)
        msg = "Initial value: {}, found_value: {}, float: {}".format(
            b_values.get(slug), found_value, value)
        self.assertEqual(found_value, float(value), msg)
        # Test FLOAT with string value.
        value = 30
        book.set_key_value(slug, value)
        found_value = book.get_key_value(slug)
        msg = "Initial value: {}, found_value: {}, float: {}".format(
            b_values.get(slug), found_value, value)
        self.assertEqual(found_value, float(value), msg)

    def test_set_key_value_NUMBER(self):
        """
        Check that the NUMBER type works correctly.
        """
        #self.skipTest("Temporarily skipped")
        # Get the test objects
        (book, b_values, author, a_values, new_author, promotion, p_values,
         new_promotion, language) = self._create_test_objects()
        # Test FLOAT ValueError exception with an integer.
        slug = 'edition'
        value = book
        with self.assertRaises(ValueError) as cm:
            book.set_key_value(slug, value)
        # Test NUMBER (normal integer numeric case).
        value = 1
        book.set_key_value(slug, value)
        found_value = book.get_key_value(slug)
        msg = "Initial value: {}, found_value: {}, new_int: {}".format(
            b_values.get(slug), found_value, value)
        self.assertEqual(found_value, value, msg)
        # Test NUMBER (normal string numeric case).
        value = '1'
        book.set_key_value(slug, value)
        found_value = book.get_key_value(slug)
        msg = "Initial value: {}, found_value: {}, new_int: {}".format(
            b_values.get(slug), found_value, value)
        self.assertEqual(found_value, int(value), msg)
        # Test NUMBER by `increment` on a number.
        book.set_key_value(slug, 'increment')
        found_value = book.get_key_value(slug)
        msg = "Initial value: {}, found_value: {}, new_int: {}".format(
            b_values.get(slug), found_value, 2)
        self.assertEqual(found_value, 2, msg)
        # Test NUMBER by `decrement` on a number.
        book.set_key_value(slug, 'decrement')
        found_value = book.get_key_value(slug)
        msg = "Initial value: {}, found_value: {}, new_int: {}".format(
            b_values.get(slug), found_value, 1)
        self.assertEqual(found_value, 1, msg)

    def test_set_key_value_TEXT_and_TEXT_BLOCK(self):
        """
        Check that the TEXT and TEXT_BLOCK type works correctly.
        """
        #self.skipTest("Temporarily skipped")
        # Get the test objects
        (book, b_values, author, a_values, new_author, promotion, p_values,
         new_promotion, language) = self._create_test_objects()
        # Test TEXT (normal text case).
        slug = 'abstract'
        value = "A new abstract"
        book.set_key_value(slug, value)
        found_value = book.get_key_value(slug)
        msg = "Initial value: {}, found_value: {}, new_value: {}".format(
            b_values.get(slug), found_value, value)
        self.assertEqual(found_value, value, msg)
        # Test creating a TEXT KeyValue object.
        slug = 'web-site'
        value = "www.example.org"
        book.set_key_value(slug, value)
        found_value = book.get_key_value(slug)
        b_values[slug] = value
        msg = "found_value: {}, new_value: {}".format(found_value, value)
        self.assertEqual(found_value, value, msg)
        result = book.serialize_key_values(by_slug=True)
        msg = "result: {}, b_values: ()".format(result, b_values)
        self.assertEqual(len(result), len(b_values), msg)


class TestKeyValue(BaseDcolumns):

    def __init__(self, name):
        super(TestKeyValue, self).__init__(name)

    def test_str_value(self):
        """
        Test that the __str__ method returns the correct value.
        """
        #self.skipTest("Temporarily skipped")
        # Create a KeyValue object.
        dc0 = self._create_dynamic_column_record(
            "Edition", DynamicColumn.NUMBER, 'book_top', 4)
        book, b_cc, b_values = self._create_book_objects(extra_dcs=[dc0,])
        value = 5
        kv = self._create_key_value_record(book, dc0, value)
        # Test that the values are the same.
        msg = "value: {}, instance value: {!s}".format(kv.value, kv)
        self.assertEqual(kv.value, str(kv), msg)
