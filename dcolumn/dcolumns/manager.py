#
# dcolumn/dcolumns/manager.py
#

import logging

from django.conf import settings

log = logging.getLogger(u'dcolumn.manage')


class DynamicColumnManager(object):

    def __init__(self):
        self._relation = []
        self._relation_map = None
        self._relation_numbers = set()
        self._choice_map = {}
        self._css_containers = []
        self._css_container_map = {}

    def register_choice(self, choice, relation_num, field):
        """
        Register choice field types. These can be Foreign Key or
        multiple-choice columns.

        :Parameters:
          choice : `ClassType`
            This can be either a Django model or choice object. A choice object
            mimics a model class so that this manager can work with them
            as if they were Django models.

          relation_num : `int`
            A numeric identifier for the `choice` used as the HTML select
            option value.

          field : `str`
            A field from the model or choice object used as the HTML select
            option text.
        """
        if relation_num in self._relation_numbers:
            msg = u"Invalid 'relation_num' {} is already used.".format(
                relation_num)
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
        self._relation.append((relation_num, choice.__name__))
        self._choice_map[choice.__name__] = (choice, field)

    def _test_field(self, choice, field):
        obj = choice()

        if not hasattr(obj, field):
            msg = u"The '{}' object does not have the field '{}'".format(
                choice.__name__, field)
            log.critical(msg)
            raise AttributeError(msg)

    @property
    def choice_relation(self):
        """
        A property that returns the HTML select choices.

        :Returns:
          A list of the choices.
        """
        return self._relation

    @property
    def choice_relation_map(self):
        """
        A property that returns a dict (map) of the choices.

        :Returns:
          A dict of the choices.
        """
        if not self._relation_map:
            self._relation_map = dict(self._relation)

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
          container_list : `list` or `tuple`
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

    def get_default_column_name(self, model_name):
        return settings.DYNAMIC_COLUMNS.get(u'ITEM_NAMES',
                                            {}).get(model_name, u'')

    def get_api_auth_state(self):
        return settings.DYNAMIC_COLUMNS.get(u'INACTIVATE_API_AUTH', False)

dcolumn_manager = DynamicColumnManager()
