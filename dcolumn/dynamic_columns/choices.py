#
# dcolumn/dynamic_comumns/choices.py
#

"""
The objects in this module mimic database models, so they will work using
the same code as Foreign Keys.
"""


#
# Language
#
class LanguageContainer(object):
    pk = 0
    name = u''


class LanguageManager(object):

    def dynamic_column(self):
        languages = (u'Chinese', u'English', u'Russian', u'Japanese',)
        result = []

        for pk, name in enumerate(languages, start=1):
            lc = LanguageContainer()
            lc.pk = pk
            lc.name = name
            result.append(lc)

        return result


class Language(object):

    objects = LanguageManager()
