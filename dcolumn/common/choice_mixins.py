#
# dcolumn/common/choice_mixins.py
#

import logging
import inspect

from django.utils.translation import ugettext_lazy as _

from dcolumn.common import ChoiceManagerImplementation

log = logging.getLogger('dcolumn.choices')


#
# InspectChoice
#
class InspectChoice(object):

    def __init__(self):
        self._path, self._caller_name = self._caller_info(skip=4)

    def _caller_info(self, skip=2):
        """
        Get a name of a caller in the format module.class.method.

        :Parameters:
          skip : `int`
            Specifies how many levels of stack to skip while getting caller
            name. skip=1 means 'who calls me', skip=2 'who calls my caller'
            etc.

        An empty string is returned if skipped levels exceed stack height

        See: https://gist.github.com/techtonik/2151727
        """
        stack = inspect.stack()
        start = 0 + skip

        if len(stack) < start + 1:
            return u''

        parentframe = stack[start][0]    
        name_list = []
        module = inspect.getmodule(parentframe)
        # `modname` can be None when frame is executed directly in console
        # TODO(techtonik): consider using __main__

        if module:
            name_list.append(module.__name__)

        # detect classname
        if u'self' in parentframe.f_locals:
            # I don't know any way to detect call from the object method
            # XXX: there seems to be no way to detect static method call--it
            # will be just a function call
            name_list.append(parentframe.f_locals[u'self'].__class__.__name__)

        codename = parentframe.f_code.co_name

        if codename != u'<module>':  # top level usually
            name_list.append( codename ) # function or a method

        del parentframe
        #log.debug("name_list: %s", name_list)
        return name_list

    @classmethod
    def set_model(self, method):
        """
        A decorator to set the choice/model object of the calling class.
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
    VALUES = None
    FIELD_LIST = None

    def __init__(self):
        super(BaseChoiceManager, self).__init__()
        self.containers = []
        self.container_map = {}

        if not self.VALUES:
            raise TypeError(_(u"Must set the '_VALUES' object to valid "
                              u"choices for the container object."))

        if not self.FIELD_LIST and len(self.FIELD_LIST) > 1:
            raise TypeError(_(u"Must provide fields to populate for your "
                              u"choices."))

    @InspectChoice.set_model
    def dynamic_column(self):
        if not self.containers:
            for pk, values in enumerate(self.VALUES, start=1):
                obj = self.model()
                setattr(obj, self.FIELD_LIST[0], pk)

                if isinstance(values, (tuple, list)):
                    for idx in xrange(len(values)):
                        setattr(obj, self.FIELD_LIST[idx+1], values[idx])
                else:
                    setattr(obj, self.FIELD_LIST[1], values)

                self.containers.append(obj)

            self.container_map.update(dict([(cont.pk, cont)
                                            for cont in self.containers]))

        return self.containers

    def get_value_by_pk(self, pk, field=None):
        self.dynamic_column()
        value = u''
        pk = int(pk)

        if pk != 0:
            try:
                obj = self.container_map.get(pk)
                value = getattr(obj, field)
            except AttributeError as e:
                log.error("Access to PK %s failed, %s", pk, e)

        return value

    def get_choices(self, field, comment=True):
        choices = [(obj.pk, getattr(obj, field))
                   for obj in self.dynamic_column()]

        if comment:
            choices.insert(
                0, (0, _("Please choose a {}".format(self.model.__name__))))

        return choices

    def get_choice_map(self, field):
        return dict([(getattr(obj, field), obj.pk)
                     for obj in self.dynamic_column()])
