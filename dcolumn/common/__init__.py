#
# dcolumn/common/__init__.py
#
"""
Implementation class.

by: Carl J. Nobile

email: carl.nobile@gmail.com
"""
__docformat__ = "restructuredtext en"


#
# ChoiceManagerImplementation
#
class ChoiceManagerImplementation(object):
    """
    Manditory defined method.
    """

    def get_value_by_pk(self, pk, field=None):
        raise NotImplementedError("Must implement 'get_value_by_pk'.")

    def get_choices(self, field, comment=True):
        raise NotImplementedError("Must implement 'get_choices'.")

    def dynamic_column(self, active=True):
        raise NotImplementedError("Must implement 'dynamic_column'.")

    def get_choice_map(self, field, active=True):
        raise NotImplementedError("Must implement 'get_choice_map'.")
