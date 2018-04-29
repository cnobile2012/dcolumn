# -*- coding: utf-8 -*-
#
# dcolumn/dcolumns/manager.py
#

"""
The DColumn manager uses the Borg pattern.
"""
__docformat__ = "restructuredtext en"

import logging
import warnings

from django.conf import settings
from django.utils.translation import ugettext, ugettext_lazy as _
from django.db.models.query import QuerySet

log = logging.getLogger('dcolumns.dcolumns.manager')


class DynamicColumnManager(object):
    """
    This class manages the dynamic columns.
    """
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

        :param choice: This can be either a Django model or sudo model class.
                       A choice class mimics a model class so that this manager
                       can work with them as if they were Django model classes.
        :type choice: ClassType
        :param relation_num: A numeric identifier for the `choice` used as the
                             HTML select option value.
        :type relation_num: int
        :param field: A field from the model or choice object used as the HTML
                      select option text.
        :type field: str
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
        Unregister choice from the manager.

        .. note::
            This is an undocumented method and should only be used for testing.

        :param choice: This is a ``CHOICE`` object not a string.
        :type choice: ``CHOICE`` object
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

        :param choice: This can be either a Django model or choice object. A
                       choice object mimics a model class so that this manager
                       can work with them as if they were Django models.
        :type choice: ClassType
        :param field: A field from the model or choice object used as the HTML
                      select option text.
        :raises AttributeError: If ``field`` is not an attribute of ``choice``.
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

        :rtype: A ``list`` of the choices.
        """
        if len(self._relations) and self._relations[0][0] != 0:
            self._relations.sort(key=lambda x: x[1].lower())
            self._relations.insert(0, (0, _("Choose a Relation")))

        return self._relations

    @property
    def choice_relation_map(self):
        """
        A property that returns a dict (map) of the choices.

        :rtype: A dict of the choices. ``{num, <object name>, ...}`` The key
                is the number given when added with the register_choice method.
                The value is the string representation of the choice object.
        """
        return dict(self._relations)

    @property
    def choice_map(self):
        """
        A property that returns a dict (map). This property is used internally
        by `dcolumn`.

        :rtype: A dict where the key is the choice name (model or choice type)
                and the value is a tuple of the model/choice object and the
                field.
        """
        return self._choice_map

    def register_css_containers(self, container_list):
        """
        Register the CSS container objects. This method is usually called in
        the settings file.

        .. note::
            The format that is put in the settings should be something like
            this: ``((<template var>, <CSS class name>), ...)``

            Example:
              ``(('top', 'container_top'), ('bottom', 'container_bottom'))``

        :param container_list: A list of the CSS classes that will determine
                               the location on the page of the various dynamic
                               columns.
        :type container_list: list or tuple
        :raises TypeError: If ``container_list`` is not a ``list`` or
                           ``tuple``.
        """
        if isinstance(container_list, (list, tuple)):
            if len(container_list) <= 0:
                msg = ("Must supply at least one CSS container. The format "
                       "should be in this formats: (('top', 'container_top'), "
                       "('bottom', 'container_bottom'))")
                log.critical(msg)
                raise TypeError(msg)

            self._css_container_map.clear()
            self._css_containers += list(container_list)
            self._css_container_map.update(dict(self._css_containers))
        else:
            msg = ("Invalid container_list type '{}', should be either a list "
                   "of tuple.").format(type(container_list))
            log.critical(msg)
            raise TypeError(msg)

    def _unregester_css_containers(self, container_list):
        """
        Unregister css containers from the manager.

        .. note::
            This is an undocumented method and should only be used for testing.

        :param container_list: A list of lists as in:
                               (('top', 'container_top'),
                                ('bottom', 'container_bottom')).
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

        :rtype: A list of tuples where the tuple is
                ``(<template var>, <CSS class name>)``.
        """
        return self._css_containers

    @property
    def css_container_map(self):
        """
        A property that returns a dict where the key is the CSS container
        number and the value is the CSS class or id. This property should be
        used in templates to designate location in the HTML.

        :rtype: A ``dict`` of the CSS container classes.
        """
        return self._css_container_map

    def get_collection_name(self, model_name):
        """
        Gets the ``ColumnCollection`` name of the model name. The model name
        can be all lowercase without underscores or the camel case class name.

        :param model_name: The dynamic column model name.
        :type model_name: str
        :rtype: A str representing the ``ColumnCollection`` name.
        :raises ValueError: If a ``ColumnCollection`` objects could not be
                            found.
        """
        result = None
        relation_names = [
            key for key, name in self.get_related_object_names(choose=False)]
        name = model_name.lower()

        if name in relation_names:
            result = name
        else:
            msg = _("The model '{}' must be in this list '{}' to be a valid "
                    "collection name.").format(name, relation_names)
            log.error(ugettext(msg))
            raise ValueError(msg)

        return result

    @property
    def api_auth_state(self):
        """
        Gets the value of settings.DYNAMIC_COLUMNS.INACTIVATE_API_AUTH. The
        state of this variable determines if the backend AJAX API needs
        authorization. The defaults is ``False`` indicating that authorization
        is active.

        :rtype: ``True`` or ``False``.
        """
        if hasattr(settings, 'DYNAMIC_COLUMNS'):
            result = settings.DYNAMIC_COLUMNS.get('INACTIVATE_API_AUTH', False)
        else:
            result = False

        return result

    def get_related_object_names(self, choose=True):
        """
        This method provides the models that inherit ``CollectionBase``
        and would usually be used in a drop down menu.

        :param choose: If ``True`` includes a choice text as first item, else
                       ``False`` the choice item is not included.
        :type choose: bool
        :rtype: A list of tuples.
        """
        from .models import CollectionBase

        related_names = [(ro.name, ro.related_model._meta.object_name)
                         for ro in CollectionBase._meta.related_objects
                         if ro.name != 'keyvalues']
        related_names.sort(key=lambda x: x[1])

        if choose:
            related_names.insert(0, (None, _("Choose a Related Model")))

        return related_names

    def get_relation_model_field(self, relation):
        """
        Gets the model class object and the field used in the HTML select
        option text value. e.g. (example_site.books.models.Author, 'name')

        :param relation: The value in the ``DynamicColumn`` relation field.
        :type relation: int
        :rtype: The model object and field used in the HTML select option text
                value.
        """
        return self.choice_map.get(self.choice_relation_map.get(relation),
                                   (None, None))

dcolumn_manager = DynamicColumnManager()
