# -*- coding: utf-8 -*-
#
# dcolumn/dcolumns/tests/test_dcolumns_manager.py
#
# WARNING: These unittests can only be run from within the original test
#          framework from https://github.com/cnobile2012/dcolumn.
#

from django.test import TestCase

from example_site.books.choices import Language
from example_site.books.models import Author, Book, Promotion, Publisher

from dcolumn.dcolumns.manager import DynamicColumnManager

from ..models import DynamicColumn, ColumnCollection, KeyValue

from .test_dcolumns_models import BaseDcolumns


class TestManager(BaseDcolumns):

    def __init__(self, name):
        super(TestManager, self).__init__(name)

    def setUp(self):
        super(TestManager, self).setUp()
        self.manager = DynamicColumnManager()

    def test_manager_object_methods(self):
        """
        Test that the number of externally callable methods in the manager
        has not changed.
        """
        #self.skipTest("Temporarily skipped")
        methods = []

        for method in dir(self.manager):
            if method.startswith('_'):
                continue

            methods.append(method)

        msg = "methods: {}".format(methods)
        self.assertEqual(len(methods), 10, msg)

    def test_register_choice(self):
        """
        There's no easy way to test this since the manager is a borg pattern
        and always has data loaded from the actual application.
        """
        self.skipTest("Temporarily skipped")

    def test_choice_relations(self):
        """
        Test that the HTML select tag options are returned correctly. The
        contents of this list of tuples should only be choice objects.
        """
        #self.skipTest("Temporarily skipped")
        compare = (Author.__name__, Book.__name__, Language.__name__,
                   Promotion.__name__, Publisher.__name__)
        result = dict(self.manager.choice_relations)
        msg = "result: {}".format(result)

        for rel in compare:
            self.assertTrue(rel in result.values(), msg)

    def test_choice_relation_map(self):
        """
        Test that a dict of choice relation names are returned keyed by an
        integer.
        """
        #self.skipTest("Temporarily skipped")
        compare = (Author.__name__, Book.__name__, Language.__name__,
                   Promotion.__name__, Publisher.__name__)
        result = self.manager.choice_relation_map
        msg = "result: {}".format(result)

        for rel in compare:
            self.assertTrue(rel in result.values(), msg)

        # Test that the max value in keys is also the size of the set.
        keys = set(result.keys())
        count = len(keys)
        self.assertEqual(count, max(keys), msg)

    def test_choice_map(self):
        """
        Test that a dict is returned.
        """
        #self.skipTest("Temporarily skipped")
        compare = (Author, Book, Language, Promotion, Publisher)
        result = self.manager.choice_map
        msg = "result: {}".format(result)

        for rel in compare:
            model, field = result.get(rel.__name__)

            try:
                fields = [f.name for f in rel._meta.get_fields()]
            except:
                fields = [field]

            self.assertTrue(field in fields, "model: {}, {}, fields: {}".format(
                model.__name__, msg, fields))

    def test_register_css_containers(self):
        """
        There's no easy way to test this since the manager is a borg pattern
        and always has data loaded from the actual application.
        """
        self.skipTest("Temporarily skipped")

    def test_css_containers(self):
        """
        Test that css_containers returns a list of tuples.
        """
        #self.skipTest("Temporarily skipped")
        containers = self.manager.css_containers
        msg = "css_containers: {}".format(containers)
        self.assertTrue(isinstance(containers, list), msg)

        for css in containers:
            self.assertTrue(isinstance(css, tuple), msg)

    def test_css_container_map(self):
        """
        Test that css_container_map returns a dict.
        """
        #self.skipTest("Temporarily skipped")
        containers = self.manager.css_container_map
        msg = "css_container_map: {}".format(containers)
        self.assertTrue(isinstance(containers, dict), msg)

    def test_get_collection_name(self):
        """
        Test that a collection name will be returned.
        """
        #self.skipTest("Temporarily skipped")
        # Test that invalid models and non-existant models throw an exception.
        models = ['Language', 'XXX']

        with self.assertRaises(ValueError) as cm:
            for model in models:
                name = self.manager.get_collection_name(model.encode('utf-8'))

        # Test that a valid model with no records returns a None.
        name = self.manager.get_collection_name('Author'.encode('utf-8'))
        msg = "name: {}".format(name)
        self.assertFalse(name, msg)

        # Test for correct models, both model class names and names all
        # lowercase.
        dc0 = self._create_dynamic_column_record(
            'New Field', 'new_field', DynamicColumn.TEXT, 'author_top', 1)
        cc0 = self._create_column_collection_record('Author Current', [dc0])
        dcr0 = self._create_dcolumn_record(Author, cc0,
                                           **{'name': 'Carl Nobile'})
        model_map = {'Author': 'Author Current',
                     'author': 'Author Current',
                     }

        for model, expected_name in model_map.items():
            name = self.manager.get_collection_name(model.encode('utf-8'))
            msg = "name: {}, expected: {}".format(name, expected_name)
            self.assertEqual(name, expected_name, msg)

    def test_api_auth_state(self):
        """
        Test that the API (AJAX) auth state is returned properly.
        """
        #self.skipTest("Temporarily skipped")
        # Test API auth state.
        state = self.manager.api_auth_state
        msg = "state: {}".format(state)
        self.assertEqual(state, False, msg)

    def test_get_relation_model_field(self):
        """
        Test that passing the correct numericvalue returns a tuple of the
        relation (model) path and the field to key on.
        """
        #self.skipTest("Temporarily skipped")
        # Test get_relation_model_field
        for key in self.manager.choice_relation_map:
            model, field = self.manager.get_relation_model_field(key)
            msg = "model: {}, field: {}".format(str(model), field)

            try:
                # These are DB model objects.
                obj = model._meta.get_field(field)
            except AttributeError as e:
                #These are choice objects.
                self.assertTrue(hasattr(model, field), msg)
            else:
                self.assertTrue(obj, msg)
