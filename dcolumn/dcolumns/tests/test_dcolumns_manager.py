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

from dcolumn.common.choice_mixins import BaseChoiceManager

from ..models import DynamicColumn, ColumnCollection, KeyValue

from .base_tests import BaseDcolumns


#
# Country
#
class CountryManager(BaseChoiceManager):
    VALUES = [
        ('China', 'Mandarin'),
        ('USA', 'English'),
        ('Brazil', 'Portuguese'),
        ('USSR', 'Russian'),
        ('Japan', 'Japanese'),
        ]
    FIELD_LIST = ['pk', 'name', 'language',]

    def __init__(self):
        super(CountryManager, self).__init__()


class Country(object):
    pk = 0
    name = ''
    language = ''

    objects = CountryManager()

    def __str__(self):
        return "{}--{}".format(
            self.name, self.language).decode(encoding='utf-8')


# Invalid choice model.
class InvalidChoice(object):
    pass


class TestManager(BaseDcolumns):

    def __init__(self, name):
        super(TestManager, self).__init__(name)

    def setUp(self):
        super(TestManager, self).setUp()

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
        self.assertEqual(len(methods), 11, msg)

    def test_register_choice(self):
        """
        There's no easy way to test this since the manager is a borg pattern
        and always has data loaded from the actual application. I've added an
        _unregister_choice method to get around these issues, but this method
        should never need to be used outside of tests.
        """
        #self.skipTest("Temporarily skipped")
        self.manager.register_choice(Country, 99, 'name')
        msg = "class: {}, relation_num: {}, field: {}".format(
            Country.__name__, 99, 'name')
        rel_map = dict(self.manager._relations)
        self.assertTrue(99 in rel_map, msg)
        self.assertTrue(rel_map.get(99) == Country.__name__, msg)
        self.assertTrue(99 in self.manager._relation_numbers, msg)
        self.assertTrue(Country.__name__ in self.manager._choice_map, msg)
        self.assertTrue(
            self.manager._choice_map.get(Country.__name__)[0] is Country, msg)
        self.assertTrue(
            self.manager._choice_map.get(Country.__name__)[1] == 'name', msg)
        #Test that an exception is raised if we try to use the same
        # relation_num.
        with self.assertRaises(ValueError) as cm:
            self.manager.register_choice(Country, 99, 'name')
        # Test that an exception is raised if we try to use an invalid choice
        # model.
        with self.assertRaises(AttributeError) as cm:
            self.manager.register_choice(InvalidChoice, 100, 'name')
        # Test thatan exception is raised when an invalid field is passed in.
        with self.assertRaises(AttributeError) as cm:
            self.manager.register_choice(Country, 101, 'bad_field')
        # Cleanup
        self.manager._unregister_choice(Country)

    def test__unregister_choice(self):
        """
        Test that the _unregister_choice method works.
        """
        #self.skipTest("Temporarily skipped")
        self.manager.register_choice(Country, 99, 'name')
        self.manager._unregister_choice(Country)
        msg = "class: {}, relation_num: {}, field: {}".format(
            Country.__name__, 99, 'name')
        rel_map = dict(self.manager._relations)
        self.assertTrue(99 not in rel_map, msg)
        self.assertTrue(rel_map.get(99) != Country.__name__, msg)
        self.assertTrue(99 not in self.manager._relation_numbers, msg)
        self.assertTrue(Country.__name__ not in self.manager._choice_map, msg)
        self.assertTrue(
            self.manager._choice_map.get(Country.__name__) is None, msg)
        self.assertTrue(
            self.manager._choice_map.get(Country.__name__) is None, msg)
        # Test that an exception is raised when trying to remove an invalid
        # choice model.
        with self.assertRaises(ValueError) as cm:
            self.manager._unregister_choice(InvalidChoice)

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
        count = len(keys) - 1 # Subtract the "Choose a Relation" option.
        msg = "keys: {}, result: {}".format(keys, result)
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
        and always has data loaded from the actual application. I've added an
        _unregister_css_containers method to get around these issues, but this
        method should never need to be used outside of tests.
        """
        #self.skipTest("Temporarily skipped")
        css_cont = (('andromeda_strain', 'andromeda-strain'),)
        self.manager.register_css_containers(css_cont)
        msg = "New css_cont: {}, Original css_containers: {}".format(
            css_cont, self.manager._css_containers)

        for item in css_cont:
            self.assertTrue(item in self.manager._css_containers, msg)

        css_cont_map = dict(css_cont)
        msg = "New css_cont_map: {}, Original css_container_map: {}".format(
            css_cont_map, self.manager._css_container_map)

        for key in css_cont_map:
            self.assertTrue(key in self.manager._css_container_map, msg)
            self.assertTrue(
                self.manager._css_container_map.get(key) == css_cont_map.get(
                    key), msg)

        # Test that an exception is raised when a zero length list or tuple
        # container_list passed in.
        with self.assertRaises(TypeError) as cm:
            self.manager.register_css_containers([])
        # Test that an exception is raised with an invalid container_list type.
        with self.assertRaises(TypeError) as cm:
            self.manager.register_css_containers('bad container type')
        # Cleanup
        self.manager._unregester_css_containers(css_cont)

    def test__unregister_css_containers(self):
        """
        Test that the _unregister_css_containers method works.
        """
        #self.skipTest("Temporarily skipped")
        css_cont = (('andromeda_strain', 'andromeda-strain'),)
        self.manager.register_css_containers(css_cont)
        self.manager._unregester_css_containers(css_cont)
        msg = "New css_cont: {}, Original css_containers: {}".format(
            css_cont, self.manager._css_containers)

        for item in css_cont:
            self.assertTrue(item not in self.manager._css_containers, msg)

        css_cont_map = dict(css_cont)
        msg = "New css_cont_map: {}, Original css_container_map: {}".format(
            css_cont_map, self.manager._css_container_map)

        for key in css_cont_map:
            self.assertTrue(key not in self.manager._css_container_map, msg)
            self.assertTrue(self.manager._css_container_map.get(key) is None,
                            msg)

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
                name = self.manager.get_collection_name(model)

        # Test a valid model, but with no collection raises an exception.
        with self.assertRaises(ValueError) as cm:
            name = self.manager.get_collection_name('AuthorX')

        # Test for correct models, both model class names and names all
        # lowercase.
        dc0 = self._create_dynamic_column_record(
            'New Field', DynamicColumn.TEXT, 'author_top', 1)
        cc0 = self._create_column_collection_record('Author Current', [dc0])
        dcr0 = self._create_dcolumn_record(Author, cc0,
                                           **{'name': 'Carl Nobile'})
        model_map = {'Author': 'author',
                     'author': 'author',
                     }

        for model, expected_name in model_map.items():
            name = self.manager.get_collection_name(model)
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

    def test_get_related_object_names(self):
        """
        Test that the model list is returned.
        """
        #self.skipTest("Temporarily skipped")
        # Test that we have data
        result = self.manager.get_related_object_names()
        msg = "result: {}".format(result)
        self.assertEqual(len(result), 5, msg)
        # Test without the choose item.
        result = self.manager.get_related_object_names(choose=False)
        msg = "result: {}".format(result)
        self.assertEqual(len(result), 4, msg)

    def test_get_relation_model_field(self):
        """
        Test that passing the correct numericvalue returns a tuple of the
        relation (model) path and the field to key on.
        """
        #self.skipTest("Temporarily skipped")
        # Test get_relation_model_field
        for key in self.manager.choice_relation_map:
            if key == 0: continue # Skip the "Choose a Relation" option.
            model, field = self.manager.get_relation_model_field(key)
            msg = "model: {}, field: {}".format(str(model), field)

            try:
                # These are DB model objects.
                obj = model._meta.get_field(field)
            except AttributeError as e:
                # These are choice objects.
                self.assertTrue(hasattr(model, field), msg)
            else:
                self.assertTrue(obj, msg)

        # Test that (None, None) are returned when an invalid key is passed.
        model, field = self.manager.get_relation_model_field(100)
        msg = "model: {}, field: {}".format(model, field)
        self.assertEqual(model, None, msg)
        self.assertEqual(field, None, msg)
