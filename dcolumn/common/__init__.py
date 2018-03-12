# -*- coding: utf-8 -*-
#
# dcolumn/common/__init__.py
#
"""
Implementation class.
"""
__docformat__ = "restructuredtext en"

import re
from string import ascii_letters, digits

_DEFAULT_CHARS = ascii_letters + digits

__all__ = ('ChoiceManagerImplementation', 'create_field_name',)


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

    def get_choices(self, field, comment=True, sort=True):
        raise NotImplementedError("Must implement 'get_choices'.")

    def model_objects(self, active=True):
        raise NotImplementedError("Must implement 'model_objects'.")


def create_field_name(value):
    value = ''.join([c if c in _DEFAULT_CHARS else '_' for c in value])
    m = re.search(r'[_]{2,1000}', value)

    while m:
        start, stop = m.span() if m else (0, 0)
        s = value[start: stop]
        value = value.replace(s, '_')
        m = re.search(r'[_]{2,1000}', value)

    return value.lower()
