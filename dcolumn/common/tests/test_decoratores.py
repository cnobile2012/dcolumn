# -*- coding: utf-8 -*-
#
# dcolumn/common/tests/test_decorators.py
#
# WARNING: These unittests can only be run from within the original test
#          framework from https://github.com/cnobile2012/dcolumn.
#

import types

from django.test import TestCase

from dcolumn.common.decorators import dcolumn_login_required, InspectChoice
from django.conf import settings


class TestDecorators(TestCase):

    def __init__(self, name):
        super(TestDecorators, self).__init__(name)

    def test_dcolumn_login_required(self):
        """
        Test that the login decorator functions correctly.
        """
        #self.skipTest("Temporarily skipped")
        # Test with login required dcolumn_manager.api_auth_state == False
        response = dcolumn_login_required()
        msg = "response: {}".format(response)
        self.assertTrue(isinstance(response, types.FunctionType), msg)
        # Test with no login required dcolumn_manager.api_auth_state == True
        settings.DYNAMIC_COLUMNS['INACTIVATE_API_AUTH'] = True
        response = dcolumn_login_required()
        # Turn authentication back on.
        settings.DYNAMIC_COLUMNS['INACTIVATE_API_AUTH'] = False
        msg = "response: {}".format(response)
        self.assertTrue(response == None, msg)
