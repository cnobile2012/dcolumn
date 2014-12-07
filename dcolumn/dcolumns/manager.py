#
# dcolumn/dcolumns/manager.py
#

import logging

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

log = logging.getLogger(u'dcolumn.manager')


class DynamicColumnManager(object):
    """
    This class manages the dynamic columns.
    """
    __shared_state = {}
    _relations = [(0, "---------")]
    _relation_map = None
    _relation_numbers = set()
    _choice_map = {}
    _css_containers = []
    _css_container_map = {}

    def __init__(self):
        self.__dict__ = self.__shared_state

    def register_choice(self, choice, relation_num, field):
        """
        Register choice field types. These can be Foreign Key or
        multiple-choice non-database columns. ManyToMany is not supported
        at this time.

        :Parameters:
          choice : ClassType
            This can be either a Django model or choice object. A choice object
            mimics a model class so that this manager can work with them
            as if they were Django models.

          relation_num : int
            A numeric identifier for the `choice` used as the HTML select
            option value.

          field : str
            A field from the model or choice object used as the HTML select
            option text.
        """
        if relation_num in self._relation_numbers:
            msg = (u"Invalid relation number {} is already used. [choice: {}, "
                   u"field: {}]").format(relation_num, choice, field)
            log.critical(msg)
            raise ValueError(msg)

        if (not hasattr(choice, 'objects') or
            not hasattr(choice.objects, 'dynamic_column')):
            msg = (u"Invalid 'choice' object '{}', must have a "
                   u"'dynamic_column' manager class method.").format(choice)
            log.critical(msg)
            raise AttributeError(msg)

        self._test_field(choice, field)
        self._relation_numbers.add(relation_num)
        self._relations.append((relation_num, choice.__name__))
        self._choice_map[choice.__name__] = (choice, field)
        log.debug("choice: %s, relation_num: %s, field: %s, relations: %s, "
                  "choice_map: %s", choice, relation_num, field,
                  self._relations, self._choice_map)

    def _test_field(self, choice, field):
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
            msg = u"The '{}' object does not have the field '{}'".format(
                choice.__name__, field)
            log.critical(msg)
            raise AttributeError(msg)

    @property
    def choice_relations(self):
        """
        A property that returns the HTML select tag choices.

        :Returns:
          A list of the choices.
        """
        return self._relations

    @property
    def choice_relation_map(self):
        """
        A property that returns a dict (map) of the choices.

        :Returns:
          A dict of the choices.
        """
        if not self._relation_map:
            self._relation_map = dict(self._relations)

        return self._relation_map

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
                msg = (u"Must supply at least one CSS container. The format "
                       u"can be in either of these formats: "
                       u"(u'container_top', u'container_bottom',) or "
                       u"((u'top', u'container_top'), "
                       u"(u'bottom', u'container_bottom'))")
                log.critical(msg)
                raise TypeError(msg)

            self._css_container_map.clear()

            if isinstance(container_list[0], (list, tuple)):
                self._css_container_map.update(dict(container_list))
                self._css_containers[:] = [
                    (key, css) for key, css in enumerate(
                        [css for name, css in container_list])]
            else:
                self._css_container_map.update(
                    {name: css for name, css in enumerate(container_list)})
                self._css_containers[:] = [
                    (key, css) for key, css in enumerate(container_list)]

    @property
    def css_containers(self):
        """
        A property that returns the CSS container classes or ids and is used
        internally as a choice to location in the DynamicColumn model.

        :Returns:
          A list of tuples where the tuple is (num, text)
        """
        return self._css_containers

    @property
    def css_container_map(self):
        """
        A property that returns a dict where the key is the CSS container
        number and the value is the CSS class or id. This property should be
        used in templates to desgnate location in the HTML.

        :Returns:
          A dict of the CSS containers.
        """
        return self._css_container_map

    def get_collection_name(self, model_name):
        """
        Gets the `ColumnCollection` instance name.

        :Parameters:
          model_name : str
            The key name used in the `settings.DYNAMIC_COLUMNS.COLLECTIONS`.

        :Returns:
          The `ColumnCollection` instance name.
        """
        model_name = model_name.lower()
        item_names = dict([
            (k.lower(), v)
            for k, v in settings.DYNAMIC_COLUMNS.get(u'COLLECTIONS').items()])

        if model_name not in item_names:
            msg = _("Invalid model name: {}".format(model_name))
            raise KeyError(msg)

        return item_names.get(model_name, u'')

    def get_api_auth_state(self):
        """
        Gets the value of settings.DYNAMIC_COLUMNS.INACTIVATE_API_AUTH.
        """
        return settings.DYNAMIC_COLUMNS.get(u'INACTIVATE_API_AUTH', False)

    def get_relation_model_field(self, relation):
        """
        Gets the model object and the field used in the HTML select option
        text value. e.g. (example_site.books.models.Author, u'name')

        :Parameters:
          relation : int
            The value in the `DynamicColumn` relation field.

        :Returns:
          The model object and field used in the HTML select option text value.
        """
        return self.choice_map.get(self.choice_relation_map.get(relation))

dcolumn_manager = DynamicColumnManager()
