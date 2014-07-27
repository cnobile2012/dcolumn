#
# dcolumn/common/choice_mixins.py
#

import logging
import inspect

from django.utils.translation import ugettext as _

log = logging.getLogger('dcolumn.choices')


#
# InspectChoice
#
class InspectChoice(object):

    def __init__(self):
        self._path, self._caller_name = self._caller_info(skip=4)

    def _caller_info(self, skip=2):
        """
        Get a name of a caller in the format module.class.method

        Arguments::
          skip `int`
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
class BaseChoiceManager(InspectChoice):
    _VALUES = None

    def __init__(self):
        super(BaseChoiceManager, self).__init__()
        self.containers = []
        self.container_map = {}

        if not self._VALUES:
            raise TypeError(_(u"Must set the '_VALUES' object to valid "
                              u"choices for the container object."))

    @InspectChoice.set_model
    def dynamic_column(self):
        if not self.containers:
            for pk, name in enumerate(self._VALUES, start=1):
                obj = self.model()
                obj.pk = pk
                obj.name = name
                self.containers.append(obj)

            self.container_map.update(dict([(cont.pk, cont)
                                            for cont in self.containers]))

        return self.containers

    def get_value_by_pk(self, pk):
        self.dynamic_column()
        value = u''
        pk = int(pk)

        if pk != 0:
            try:
                obj = self.container_map.get(pk)
                value = obj.name
            except AttributeError as e:
                log.error("Access to PK %s failed, %s", pk, e)

        return value
