#
# example_site/books/choices.py
#

"""
The objects in this module mimic database models, so they will work properly
in the ChoiceManager class.
"""

from dcolumn.common.choice_mixins import BaseChoiceManager
from dcolumn.dcolumns.manager import dcolumn_manager


#
# Language
#
class LanguageManager(BaseChoiceManager):
    VALUES = (u'Chinese', u'English', u'Portuguese', u'Russian', u'Japanese',)
    FIELD_LIST = (u'pk', u'name',)

    def __init__(self):
        super(LanguageManager, self).__init__()


class Language(object):
    pk = 0
    name = u''

    objects = LanguageManager()

dcolumn_manager.register_choice(Language, 1, u'name')
