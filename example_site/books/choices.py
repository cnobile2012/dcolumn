#
# example_site/books/choices.py
#

"""
The objects in this module mimic database models, so they will work properly
in the ChoiceManager class.
"""

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


class Language(BaseChoice):
    pk = 0
    name = ''

    objects = LanguageManager()

    def __str__(self):
        return self.name.encode('utf-8')


dcolumn_manager.register_choice(Language, 1, 'name')
