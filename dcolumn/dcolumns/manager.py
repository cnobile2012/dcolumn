# -*- coding: utf-8 -*-
#
# dcolumn/dcolumns/manager.py
#

import logging
import warnings

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.db.models.query import QuerySet

from dcolumn.common.deprication import RemovedInDColumns100Warning

log = logging.getLogger('dcolumns.dcolumns.manager')


class DynamicColumnManager(object):
    """
    This class manages the dynamic columns.
    """
    __slots__ = ('__shared_state', '_relations', '_relation_map',
                 '_relation_numbers', '_choice_map', '_css_containers',
                 '_css_container_map', '__dict__',)
    __shared_state = {}
    _relations = []
    _relation_numbers = set()
    _choice_map = {}
    _css_containers = []
    _css_container_map = {}

    def __init__(self):
        """
        Constructor creates the Borg pattern.
        """
        self.__dict__ = self.__shared_state

    def register_choice(self, choice, relation_num, field):
        """
        Register choice field types. These can be Foreign Key or
        multiple-choice non-database columns. ManyToMany is not supported
        at this time.

        :Parameters:
          choice : ClassType
            This can be either a Django model class or choice class. A choice
            class mimics a model class so that this manager can work with them
            as if they were Django model classes.

          relation_num : int
            A numeric identifier for the `choice` used as the HTML select
            option value.

          field : str
            A field from the model or choice object used as the HTML select
            option text.
        """
        if relation_num in self._relation_numbers:
            msg = ("Invalid relation number {} is already used. [choice: {}, "
                   "field: {}]").format(relation_num, choice, field)
            log.critical(msg)
            raise ValueError(msg)

        if (not hasattr(choice, 'objects') or
            not hasattr(choice.objects, 'model_objects')):
            msg = ("Invalid 'choice' object '{}', must have a "
                   "'model_objects' manager class method.").format(choice)
            log.critical(msg)
            raise AttributeError(msg)

        self._check_field(choice, field)
        self._relation_numbers.add(relation_num)
        self._relations.append((relation_num, choice.__name__))
        self._choice_map[choice.__name__] = (choice, field)
        log.debug("choice: %s, relation_num: %s, field: %s, relations: %s, "
                  "choice_map: %s", choice, relation_num, field,
                  self._relations, self._choice_map)

    def _unregister_choice(self, choice):
        """
        Unregister choice from the manager (Used for testing only, should not
        be used in code).
        """
        _choice, field = self._choice_map.get(choice.__name__, (None, None))
        relation_num = dict([(v, k) for k, v in self._relations]).get(
            choice.__name__)

        if _choice and field and relation_num:
            self._choice_map.pop(_choice.__name__)
            self._relations.remove((relation_num, _choice.__name__))
            self._relation_numbers.remove(relation_num)
        else:
            msg = "Tried to remove an invalid choice object {}.".format(choice)
            log.error(msg)
            raise ValueError(msg)

    def _check_field(self, choice, field):
        """
        Test that the specified field is a member object on the instantiated
        class object.

        :Parameters:
          choice : ClassType
            This can be either a Django model or choice object. A choice object
            mimics a model class so that this manager can work with them
            as if they were Django models.
          field : str
            A field from the model or choice object used as the HTML select
            option text.
        """
        obj = choice()

        if not hasattr(obj, field):
            msg = "The '{}' object does not have the field '{}'".format(
                choice.__name__, field)
            log.critical(msg)
            raise AttributeError(msg)

    @property
    def choice_relations(self):
        """
        A property that returns the HTML select option choices.

        :Returns:
          A list of the choices.
        """
        if len(self._relations) and self._relations[0][0] != 0:
            self._relations.sort(cmp=lambda x,y: cmp(x[1].lower(),
                                                     y[1].lower()))
            self._relations.insert(0, (0, _("Choose a Relation")))

        return self._relations

    @property
    def choice_relation_map(self):
        """
        A property that returns a dict (map) of the choices.

        :Returns:
          A dict of the choices. {num, <object name>, ...} The key is the
          number given when added with the register_choice method. The value
          is the string representation of the choice object.
        """
        return dict(self._relations)

    @property
    def choice_map(self):
        """
        A property that returns a dict (map). This property is used internally
        by `dcolumn`.

        :Returns:
          A dict where the key is the choice name (model or choice type) and
          the value is a tuple of the model/choice object and the field.
        """
        return self._choice_map

    def register_css_containers(self, container_list):
        """
        Register the CSS container objects. This method is usually called in
        the settings file.

        :Parameters:
          container_list : list or tuple
            A list of the CSS classes or ids that will determine the location
            on the page of the various dynamic columns.
        """
        if isinstance(container_list, (list, tuple)):
            if len(container_list) <= 0:
                msg = ("Must supply at least one CSS container. The format "
                       "can be in either of these formats: "
                       "('container_top', 'container_bottom',) or "
                       "(('top', 'container_top'), "
                       "('bottom', 'container_bottom'))") # Deprication
                log.critical(msg)
                raise TypeError(msg)

            self._css_container_map.clear()

            if isinstance(container_list[0], (list, tuple)):
                self._css_containers += list(container_list)
                self._css_container_map.update(dict(self._css_containers))
            else: # This method will be deprecated in version 1.0
                warnings.warn(
                    "Deprecation Warning: The enumeration method of "
                    "generating the display location will be deprecated "
                    "with the release of version 1.0.0.",
                    RemovedInDColumns100Warning)
                self._css_containers += [
                    (key, css) for key, css in enumerate(container_list)]
                self._css_container_map.update(dict(self._css_containers))
        else:
            msg = ("Invalid container_list type '{}', should be either a list "
                   "of tuple.").format(type(container_list))
            log.critical(msg)
            raise TypeError(msg)

    def _unregester_css_containers(self, container_list):
        """
        Unregister css containers from the manager (Used for testing only,
        should not be used in code).
        """
        for item in container_list:
            self._css_containers.remove(item)

        self._css_container_map.clear()
        self._css_container_map.update(dict(self._css_containers))

    @property
    def css_containers(self):
        """
        A property that returns a list of tuples where the key is the
        template variable name and the CSS container class.

        :Returns:
          A list of tuples where the tuple is (template var, css class)
        """
        return self._css_containers

    @property
    def css_container_map(self):
        """
        A property that returns a dict where the key is the CSS container
        number and the value is the CSS class or id. This property should be
        used in templates to designate location in the HTML.

        :Returns:
          A dict of the CSS containers.
        """
        return self._css_container_map

    def get_collection_name(self, model_name):
        """
        Gets the `ColumnCollection` name of the model name. The model name can
        be all lowercase without underscores or the camel case class name.

        :Parameters:
          model_name : str
            The dynamic column model name.

        :Returns:
          The `ColumnCollection` name.
        """
        paths = [app for app in settings.INSTALLED_APPS
                 if 'django.contrib' not in app]
        paths = ['{}.models'.format(p) for p in paths]
        result = obj = None

        for path in paths:
            module = __import__(path, globals(), locals(), -1)

            for name in dir(module):
                if model_name == name or model_name == name.lower():
                    try:
                        obj = getattr(module, name).objects.select_related(
                            'column_collection__name').all()
                    except AttributeError:
                        pass

                    if isinstance(obj, QuerySet) and obj.count() > 0:
                        obj = obj[0]

                        if hasattr(obj, 'column_collection'):
                            result = obj.column_collection.name
                            break
                    elif obj is None:
                        break
                    else:
                        log.error("No records in model %s.", name)

        if obj is None:
            msg = _("Invalid model name: {}".format(model_name))
            log.error(msg)
            raise ValueError(msg)

        return result

    @property
    def api_auth_state(self):
        """
        Gets the value of settings.DYNAMIC_COLUMNS.INACTIVATE_API_AUTH.
        """
        return settings.DYNAMIC_COLUMNS.get('INACTIVATE_API_AUTH', False)

    def get_relation_model_field(self, relation):
        """
        Gets the model object and the field used in the HTML select option
        text value. e.g. (example_site.books.models.Author, 'name')

        :Parameters:
          relation : int
            The value in the `DynamicColumn` relation field.

        :Returns:
          The model object and field used in the HTML select option text value.
        """
        return self.choice_map.get(self.choice_relation_map.get(relation),
                                   (None, None))

dcolumn_manager = DynamicColumnManager()
