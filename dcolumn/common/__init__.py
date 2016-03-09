# -*- coding: utf-8 -*-
#
# dcolumn/common/__init__.py
#
"""
Implementation class.
"""
__docformat__ = "restructuredtext en"


#
# ChoiceManagerImplementation
#
class ChoiceManagerImplementation(object):
    """
    Manditory methods that must be defined in both choice models and Django
    models.
    """

    def get_value_by_pk(self, pk, field=None):
        raise NotImplementedError("Must implement 'get_value_by_pk'.")

    def get_choices(self, field, comment=True):
        raise NotImplementedError("Must implement 'get_choices'.")

    def model_objects(self, active=True):
        raise NotImplementedError("Must implement 'model_objects'.")
