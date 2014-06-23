#
# dcolumn/dynamic_columns/manage.py
#

import logging

log = logging.getLogger(u'dcolumn.manage')


class ChoiceManager(object):

    def __init__(self):
        self._relation = []
        self._relation_map = None
        self._relation_numbers = set()
        self._choice_map = {}
        self._css_containers = []
        self._css_container_map = {}

    def register_choice(self, choice, relation_num, field):
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
        return self._relation

    @property
    def choice_relation_map(self):
        if not self._relation_map:
            self._relation_map = dict(self._relation)

        return self._relation_map

    @property
    def choice_map(self):
        return self._choice_map

    def register_css_containers(self, container_list):
        if isinstance(container_list, (list, tuple)):
            if len(container_list) <= 0:
                msg = (u"Must supply at least one CSS container. The format "
                       u"can be in either of these formats: "
                       u"(u'container_top', u'container_bottom',) or "
                       u"((u'top', u'container_top'), "
                       u"(u'bottom', u'container_bottom'))")
                log.critical(msg)
                raise TypeError(msg)

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
        return self._css_containers

    @property
    def css_container_map(self):
        return self._css_container_map

choice_manager = ChoiceManager()
