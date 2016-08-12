#
# example_site/books/choices.py
#
from __future__ import unicode_literals

"""
The objects in this module mimic database models, so they will work properly
in the ChoiceManager class.
"""

from django.utils.encoding import python_2_unicode_compatible

from dcolumn.common.choice_mixins import BaseChoice, BaseChoiceManager
from dcolumn.dcolumns.manager import dcolumn_manager


#
# Language
#
class LanguageManager(BaseChoiceManager):
    VALUES = ('Chinese', 'English', 'Portuguese', 'Russian', 'Japanese',)
    FIELD_LIST = ('pk', 'name',)

    def __init__(self):
        super(LanguageManager, self).__init__()


@python_2_unicode_compatible
class Language(BaseChoice):
    pk = 0
    name = ''

    objects = LanguageManager()

    def __str__(self):
        return self.name


dcolumn_manager.register_choice(Language, 1, 'name')
