# -*- coding: utf-8 -*-
#
# dcolumn/dcolumns/tests/test_dcolumns_choice.py
#
# WARNING: These unittests can only be run from within the original test
#          framework from https://github.com/cnobile2012/dcolumn.
#

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from dcolumn.dcolumns.manager import DynamicColumnManager

from .test_dcolumns_manager import Country


class TestChoices(TestCase):

    def __init__(self, name):
        super(TestChoices, self).__init__(name)

    def test_model_objects(self):
        """
        Test that Choice objects get created properly.
        """
        #self.skipTest("Temporarily skipped")
        values = Country.objects.VALUES
        modal_objects = Country.objects.model_objects()
        msg = "modal_objects: {}, values: {}".format(modal_objects, values)
        self.assertEqual(len(modal_objects), len(values), msg)

        for model in modal_objects:
            self.assertTrue(model.name in dict(values), msg)

    def test_get_pk(self):
        """
        Test that the get method returns the correct object.
        """
        #self.skipTest("Temporarily skipped")
        values = Country.objects.VALUES
        obj = Country.objects.get(pk=3)
        msg = "get: {}, values: {}".format(obj, values)
        self.assertEqual(obj.language, dict(values).get('Brazil'), msg)

    def test_get_name(self):
        """
        Test that the get method returns the correct object.
        """
        #self.skipTest("Temporarily skipped")
        name = 'Brazil'
        values = Country.objects.VALUES
        obj = Country.objects.get(name=name)
        msg = "get: {}, values: {}".format(obj, values)
        self.assertEqual(obj.language, dict(values).get(name), msg)

    def test_get_DoesNotExist(self):
        """
        Test that the get method returns the correct object.
        """
        #self.skipTest("Temporarily skipped")
        name = 'XzXzXz'
        values = Country.objects.VALUES

        with self.assertRaises(ObjectDoesNotExist) as cm:
            obj = Country.objects.get(name=name)

        msg = "Country matching query does not exist."
        self.assertTrue(msg in str(cm.exception))

    def test_get_value_by_pk(self):
        """
        Test that the proper field is returned with the proper pk.
        """
        #self.skipTest("Temporarily skipped")
        values = Country.objects.VALUES
        objs = Country.objects.model_objects()

        for obj in objs:
            value = Country.objects.get_value_by_pk(obj.pk, 'name')
            msg = "value: {}, values: {}".format(value, values)
            self.assertEqual(value, obj.name, msg)

        for obj in objs:
            value = Country.objects.get_value_by_pk(obj.pk, 'language')
            msg = "value: {}, values: {}".format(value, values)
            self.assertEqual(value, obj.language, msg)

    def test_get_choices(self):
        """
        Test that the HTML select option values are returned properly.
        """
        #self.skipTest("Temporarily skipped")
        objs = Country.objects.model_objects()
        choices = Country.objects.get_choices('name')
        msg = "choices: {}, objs: {}".format(choices, objs)
        # Test that an HTML select option header is in the choices.
        self.assertTrue(0 in dict(choices), msg)

        # Test that all the objects are in the choices.
        for obj in objs:
            self.assertEqual(obj.name, dict(choices).get(obj.pk), msg)

        # Test that no HTML select option header is in the choices.
        choices = Country.objects.get_choices('name', comment=False)
        msg = "choices: {}, objs: {}".format(choices, objs)
        self.assertFalse(0 in dict(choices), msg)

        # Test that the language is in the choices instead of the country
        # name.
        choices = Country.objects.get_choices('language')
        msg = "choices: {}, objs: {}".format(choices, objs)

        # Test that all the objects are in the choices.
        for obj in objs:
            self.assertEqual(obj.language, dict(choices).get(obj.pk), msg)
