#
# example_site/books/choices.py
#

"""
The objects in this module mimic database models, so they will work in the
ChoiceManager class.
"""

from dcolumn.common.choice_mixins import BaseChoiceManager
from dcolumn.dcolumns.manager import dcolumn_manager


#
# Language
#
class LanguageManager(BaseChoiceManager):
    _VALUES = (u'Chinese', u'English', u'Russian', u'Japanese',)

    def __init__(self):
        super(LanguageManager, self).__init__()


class Language(object):
    pk = 0
    name = u''

    objects = LanguageManager()

dcolumn_manager.register_choice(Language, 1, u'name')
