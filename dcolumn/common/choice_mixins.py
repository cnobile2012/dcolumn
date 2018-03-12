# -*- coding: utf-8 -*-
#
# dcolumn/common/choice_mixins.py
#

"""
Dynamic Column dependent choice mixins.
"""
__docformat__ = "restructuredtext en"

import logging


from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils import six

from . import ChoiceManagerImplementation
from .decorators import InspectChoice

log = logging.getLogger('dcolumns.common.choices')


#
# BaseChoiceManager
#
class BaseChoiceManager(InspectChoice, ChoiceManagerImplementation):
    """
    This class must be used in any non-django model ``CHOICE`` object.

    .. note::

      The ``PK`` field is manditory, however it does not need to be put
      into the ``FIELD_LIST`` object. It will be removed before processing
      if found. The list could look like this:
      ``('pk', 'name', 'version',)`` or ``('name', 'version',)``.

      There are two ways to populate the ``VALUES`` object in a choice
      model.

        1. A flat list of objects as such: ``('Good', 'Better',)``

        2. List in list as such:
           ``(('Arduino', 'Mega2560'), ('Raspberry Pi', 'B+'),)``

      The second method permits more than one fields whereas the first
      method permits only one field. In neither case does the ``PK`` count
      as a field.

      Both the ``FIELD_LIST`` and ``VALUES`` objects can be either a
      ``list`` or ``tuple``.
    """
    VALUES = []
    FIELD_LIST = []

    def __init__(self):
        super(BaseChoiceManager, self).__init__()
        self.containers = []
        self.container_map = {}

        if not self.VALUES:
            raise TypeError(_("Must set the '{}' object to valid choices "
                              "for the container object.").format('VALUES'))

        if 'pk' in self.FIELD_LIST:
            self.FIELD_LIST = list(self.FIELD_LIST)
            self.FIELD_LIST.remove('pk')

        if not self.FIELD_LIST or not len(self.FIELD_LIST) >= 1:
            raise TypeError(_("Must provide fields to populate for your "
                              "choices."))

    @InspectChoice.set_model
    def model_objects(self):
        """
        This method creates and returns the choice objects the first time
        it is run, on subsequent runs it returns the stored objects.

        :rtype: A list of non-django model ``CHOICE`` objects.
        """
        if not self.containers:
            for pk, values in enumerate(self.VALUES, start=1):
                obj = self.model()
                setattr(obj, 'pk', pk)

                if isinstance(values, (tuple, list)):
                    for idx in range(len(values)):
                        setattr(obj, self.FIELD_LIST[idx], values[idx])
                else:
                    setattr(obj, self.FIELD_LIST[0], values)

                self.containers.append(obj)

            self.container_map.update(dict([(cont.pk, cont)
                                            for cont in self.containers]))

        return self.containers

    all = model_objects

    @InspectChoice.set_model
    def get(self, **kwargs):
        fields = self.FIELD_LIST + ['pk']
        assert kwargs, "Cannot execute a query with no arguments."
        valid = all([f in fields for f in kwargs.keys()])
        assert valid, "Invalid field name, not all '{}' are in '{}'.".format(
            list(kwargs.keys()), fields)
        result = []

        for obj in self.model_objects():
            found = all([
                getattr(obj, field) == (
                    int(value)
                    if isinstance(value, six.string_types) and value.isdigit()
                    else value)
                for field, value in kwargs.items()])
            if found: result.append(obj)

        num = len(result)

        if num == 0:
            raise ObjectDoesNotExist(
                "{} matching query does not exist.".format(
                    self.model.__name__))
        elif num > 1: # pragma: no cover
            raise MultipleObjectsReturned(
                "get() returned more than one {} -- it returned {}!".format(
                    self.model.__name__, num))

        return result[0]

    def get_value_by_pk(self, pk, field):
        """
        Calls model_objects() to be sure the choice objects are created,
        then returns the value from the `field` argument based on the
        'pk' argument.

        :param pk: The key of the object.
        :type pk: int or str
        :param field: The field of the choice the value is taken from.
        :type field: str
        :rtype: Value from the ``field`` on the object.
        """
        self.model_objects()
        value = ''
        pk = int(pk)

        if pk != 0:
            try:
                obj = self.container_map[pk]
            except KeyError as e:
                msg = _("Access to PK %s failed, %s")
                log.error(ugettext(msg), pk, e)
                raise e
            else:
                try:
                    value = getattr(obj, field)
                except AttributeError as e:
                    msg = _("The field value '%s' is not on object '%s'")
                    log.error(ugettext(msg), field, obj)
                    raise e

        return value

    def get_choices(self, field, comment=True, sort=True):
        """
        Calls model_objects() to be sure the choice objects are created,
        then returns a list appropriate for HTML select option tags.

        :param field: The field of the choice that is used to populate the
                      list.
        :type field: str
        :param comment: Defaults to ``True`` prepending a choice header to
                        the list.
        :type comment: bool
        :param sort: Defaults ro ``True`` sorting the results, a ``False``
                     will turn off sorting.
        :type sort: bool
        :rtype: A list of tuples suitable for use in HTML select option
                tags.
        """
        choices = [(obj.pk, ugettext(getattr(obj, field)))
                   for obj in self.model_objects()]

        if sort:
            choices.sort(key=lambda x: x[1])

        if comment:
            choices.insert(
                0, (0, _("Please choose a {}").format(self.model.__name__)))

        return choices


class BaseChoice(object):
    """
    We need a base class for all Choice types so we can dynamically find
    them.
    """
    pass
