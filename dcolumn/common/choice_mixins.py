# -*- coding: utf-8 -*-
#
# dcolumn/common/choice_mixins.py
#

"""
Dynamic Column dependent choice mixins.
"""
__docformat__ = "restructuredtext en"

import logging
import inspect

from django.utils.translation import ugettext_lazy as _

from dcolumn.common import ChoiceManagerImplementation

log = logging.getLogger('dcolumns.common.choices')


#
# InspectChoice
#
class InspectChoice(object):
    """
    This class does introspection on a non-model ``CHOICE`` object. It should
    not be necessary to use this class outside of DColumns itself.
    """

    def __init__(self):
        self._path, self._caller_name = self._caller_info(skip=4)

    def _caller_info(self, skip=2):
        """
        Get a name of a caller in the format module.class.method.

        :param skip: Specifies how many levels of stack to skip while getting
                     caller name. skip=1 means 'who calls me', skip=2 'who
                     calls my caller' etc.
        :type skip: int
        :rtype: A list or empty string

        An empty string is returned if skipped levels exceed stack height.

        See: https://gist.github.com/techtonik/2151727
        """
        stack = inspect.stack()
        start = 0 + skip

        if len(stack) < start + 1:
            return ''

        parentframe = stack[start][0]    
        name_list = []
        module = inspect.getmodule(parentframe)
        # `modname` can be None when frame is executed directly in console
        # TODO(techtonik): consider using __main__

        if module:
            name_list.append(module.__name__)

        # detect classname
        if 'self' in parentframe.f_locals:
            # I don't know any way to detect call from the object method
            # XXX: there seems to be no way to detect static method call--it
            # will be just a function call
            name_list.append(parentframe.f_locals['self'].__class__.__name__)

        codename = parentframe.f_code.co_name

        if codename != '<module>':  # top level usually
            name_list.append( codename ) # function or a method

        del parentframe
        #log.debug("name_list: %s", name_list)
        return name_list

    @classmethod
    def set_model(self, method):
        """
        A decorator to set the choice/model object of the calling class.

        :param method: The method name to be decorated.
        :type method: str
        :rtype: The enclosed function embedded in this method.
        """
        def wrapper(this):
            modules = __import__(this._path, globals(), locals(),
                                 (this._caller_name,), -1)
            this.model = getattr(modules, this._caller_name)
            return method(this)

        # Make the wrapper look like the decorated method.
        wrapper.__name__ = method.__name__
        wrapper.__dict__ = method.__dict__
        wrapper.__doc__ = method.__doc__
        return wrapper


#
# BaseChoiceManager
#
class BaseChoiceManager(InspectChoice, ChoiceManagerImplementation):
    """
    This class must be used in any non-django model ``CHOICE`` object.
    """
    VALUES = None
    FIELD_LIST = None

    def __init__(self):
        super(BaseChoiceManager, self).__init__()
        self.containers = []
        self.container_map = {}

        if not self.VALUES:
            raise TypeError(_("Must set the 'VALUES' object to valid "
                              "choices for the container object."))

        if 'pk' in self.FIELD_LIST:
            self.FIELD_LIST = list(self.FIELD_LIST)
            self.FIELD_LIST.remove('pk')

        if not self.FIELD_LIST or not len(self.FIELD_LIST) >= 1:
            raise TypeError(_("Must provide fields to populate for your "
                              "choices."))

    @InspectChoice.set_model
    def model_objects(self):
        """
        This method creates and returns the choice objects the first time it
        is run, on subsequent runs it just returns the objects.

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

    def get_value_by_pk(self, pk, field):
        """
        Calls model_objects() to be sure the choice objects are created, then
        returns the value from the `field` argument based on the 'pk' argument.

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
                obj = self.container_map.get(pk)
            except AttributeError as e:
                log.error("Access to PK %s failed, %s", pk, e)
            else:
                if hasattr(obj, field):
                    value = getattr(obj, field)
                else:
                    log.error("The field value '%s' is not on object '%s'",
                              field, obj)

        return value

    def get_choices(self, field, comment=True):
        """
        Calls model_objects() to be sure the choice objects are created, then
        returns a list appropriate for HTML select option tags.

        :param field: The field of the choice that is used to populate the list.
        :type field: str
        :param comment: Defaults to ``True`` prepending a choice header to the
                        list.
        :type comment: bool
        :rtype: A list of tuples suitable for use in HTML select option tags.

        """
        choices = [(obj.pk, getattr(obj, field))
                   for obj in self.model_objects()]
        choices.sort(key=lambda x: x[1])

        if comment:
            choices.insert(
                0, (0, _("Please choose a {}").format(self.model.__name__)))

        return choices
