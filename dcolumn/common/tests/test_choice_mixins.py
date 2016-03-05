# -*- coding: utf-8 -*-
#
# dcolumn/common/tests/test_choice_mixins.py
#
# WARNING: These unittests can only be run from within the original test
#          framework from https://github.com/cnobile2012/dcolumn.
#

from django.test import TestCase

from dcolumn.common.choice_mixins import BaseChoiceManager


#
# TestSingleFieldChoice
#
class TestSingleFieldChoiceManager(BaseChoiceManager):
    VALUES = ('Good', 'Better',)
    FIELD_LIST = ('pk', 'name',)

    def __init__(self):
        super(TestSingleFieldChoiceManager, self).__init__()

class TestSingleFieldChoice(object):
    pk = 0
    name = ''

    objects = TestSingleFieldChoiceManager()


#
# TestMultipleFieldChoice
#
class TestMultipleFieldChoiceManager(BaseChoiceManager):
    VALUES = (('Arduino', 'Mega2560'), ('Raspberry Pi', 'B+'),)
    FIELD_LIST = ('pk', 'name', 'version',)

    def __init__(self):
        super(TestMultipleFieldChoiceManager, self).__init__()

class TestMultipleFieldChoice(object):
    pk = 0
    name = ''
    version = ''

    objects = TestMultipleFieldChoiceManager()


class TestChoiceMixins(TestCase):

    def __init__(self, name):
        super(TestChoiceMixins, self).__init__(name)

    def test_constructor_VALUES(self):
        """
        Test the constructor missing VALUES.
        """
        #self.skipTest("Temporarily skipped")
        # Test that TypeError is raise with no VALUES.
        with self.assertRaises(TypeError) as cm:
            class TestMissingVALUESChoiceManager(BaseChoiceManager):

                def __init__(self):
                    super(TestMissingVALUESChoiceManager, self).__init__()

            class TestMissingVALUESChoice(object):
                pk = 0
                name = ''

                objects = TestMissingVALUESChoiceManager()

    def test_constructor_FIELD_LIST(self):
        """
        Test the constructor missing FIELD_LIST.
        """
        #self.skipTest("Temporarily skipped")
        # Test that TypeError is raise with no FIELD_LIST
        with self.assertRaises(TypeError) as cm:
            class TestMissingFIELD_LISTChoiceManager(BaseChoiceManager):
                VALUES = ('Bad', 'Worse')

                def __init__(self):
                    super(TestMissingFIELD_LISTChoiceManager, self).__init__()

            class TestMissingFIELD_LISTChoice(object):
                pk = 0
                name = ''

                objects = TestMissingFIELD_LISTChoiceManager()

    def test_model_objects(self):
        """
        Test model_objects.
        """
        #self.skipTest("Temporarily skipped")
        # Test for single field choice object.
        tsfc = TestSingleFieldChoice()
        values = tsfc.objects.model_objects()
        msg = "Should be 2 objects, found {}".format(len(values))
        self.assertEqual(len(values), 2, msg)
        # Test for multi-field choice obect.
        tmfc = TestMultipleFieldChoice()
        values = tmfc.objects.model_objects()
        msg = "Should be 2 objects, found {}".format(len(values))
        self.assertEqual(len(values), 2, msg)

    def test_get_value_by_pk(self):
        """
        Test get_value_by_pk.
        """
        #self.skipTest("Temporarily skipped")
        # Test that single field choice returns the correct field.
        tsfc = TestSingleFieldChoice()
        found_value = tsfc.objects.get_value_by_pk(1, 'name')
        value = 'Good'
        msg = "Should be '{}', found {}".format(value, found_value)
        self.assertEqual(value, found_value, msg)
        # Test that multi field choice returns the correct field.
        tmfc = TestMultipleFieldChoice()
        found_value = tmfc.objects.get_value_by_pk(1, 'name')
        value = 'Arduino'
        msg = "Should be '{}', found {}".format(value, found_value)
        self.assertEqual(value, found_value, msg)
        found_value = tmfc.objects.get_value_by_pk(1, 'version')
        value = 'Mega2560'
        msg = "Should be '{}', found {}".format(value, found_value)
        self.assertEqual(value, found_value, msg)
        # Test invalid pk.
        with self.assertRaises(AttributeError) as cm:
            found_value = tmfc.objects.get_value_by_pk(3, 'name')
        # Test invalid field.
        with self.assertRaises(AttributeError) as cm:
            found_value = tmfc.objects.get_value_by_pk(1, 'bad_field')

    def test_get_choices(self):
        """
        Test get_choices.
        """
        #self.skipTest("Temporarily skipped")
        # Test that single field choice returns the correct field.
        tsfc = TestSingleFieldChoice()
        found_values = tsfc.objects.get_choices('name', comment=False)
        found_values = [v for k, v in found_values]
        values = ['Better', 'Good',]
        msg = "Should be '{}', found {}".format(values, found_values)
        self.assertEqual(values, found_values, msg)
        # Test that multi field choice returns the correct field.
        tmfc = TestMultipleFieldChoice()
        found_values = tmfc.objects.get_choices('version', comment=False)
        found_values = [v for k, v in found_values]
        values = ['B+', 'Mega2560',]
        msg = "Should be '{}', found {}".format(values, found_values)
        self.assertEqual(values, found_values, msg)
        # Test that the comment is returned.
        found_values = tsfc.objects.get_choices('name')
        found_values = dict(found_values)
        item = 'Please choose a TestSingleFieldChoice'
        msg = "Comment {}, found {}".format(item, found_values.get(0))
        self.assertEqual(item, found_values.get(0), msg)
