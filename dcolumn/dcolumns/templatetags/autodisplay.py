# -*- coding: utf-8 -*-
#
# dcolumn/dcolumns/templatetags/autodisplay.py
#

"""
Template tags used for displaying dynamic columns.
"""
__docformat__ = "restructuredtext en"

import os, logging, types
import datetime
from dateutil import parser

from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils import six

from dcolumn.dcolumns.models import DynamicColumn, KeyValue
from dcolumn.dcolumns.manager import dcolumn_manager

log = logging.getLogger('dcolumns.dcolumns.templatetags')
register = template.Library()


#
# auto_display
#
# NOTE: Formatting of the doc string is to conform with django docs not sphinx.
#
@register.tag(name='auto_display')
def auto_display(parser, token):
    """
    This tag returns an HTML element.

    Arguments::

      relation -- One object from the 'relations' template context object.
      prefix   -- A keyword argument who's value is used as a prefix to the
                  element id and name attributes.
      option   -- A keyword argument who's value is in the 'dynamicColumns'
                  context. The entire 'dynamicColumns' context can be supplied
                  or just the object for this relation.
      display  -- A keyword argument. If 'True' use <span> for all tags else
                  'False' use the default tag types.

    Assume data structures below for examples::

      {'dynamicColumns': {
        'book': [
          [0, 'Choose a value'],
          [2, 'HTML5 Pocket Reference'],
          [1, 'SQL Pocket Guide'],
          [3, 'Raspberry Pi Hacks']
          ]
        }
      }

      {'relations': {
        '1': {
          'name': 'Project ID',
          'required': false,
          'relation': null,
          'location': 'top-container',
          'value_type': 0,
          'order': 3,
          'value': '12345'
        },
      }

    Usage Examples::

      {% auto_display relation %}

      {% auto_display relation prefix=test- %}

      {% auto_display relation options=books %}

      {% auto_display relation options=books display=True %}

      {% auto_display relation prefix=test- options=dynamicColumns %}
    """
    tokens = token.split_contents()
    size = len(tokens)
    kwargs = {'prefix': '', 'options': None, 'display': 'False'}
    keywords = list(six.viewkeys(kwargs))
    keywords.sort()

    if size == 2:
        tag_name, relation = tokens
        kwargs = {}
    elif size == 3:
        tag_name, relation, value1 = tokens
        kwargs.update({k: v for k,d,v in [v.partition('=')
                                          for v in (value1,)]})
    elif size == 4:
        tag_name, relation, value1, value2 = tokens
        kwargs.update({k: v for k,d,v in [v.partition('=')
                                          for v in (value1, value2)]})
    elif size == 5:
        tag_name, relation, value1, value2, value3 = tokens
        kwargs.update({k: v for k,d,v in [v.partition('=')
                                          for v in (value1, value2, value3)]})
    else:
        msg = ("Invalid number of arguments should be 1 - 4, "
               "found: {}").format(size-1)
        raise template.TemplateSyntaxError(msg)

    if size > 2 and not all([key in keywords for key in kwargs]):
        msg = "Invalid keyword name, should be one of {}".format(keywords)
        raise template.TemplateSyntaxError(msg)

    return AutoDisplayNode(tag_name, relation, **kwargs)


class AutoDisplayNode(template.Node):
    """
    Node class for the `auto_display` tag.
    """
    RELATION_ERROR_MSG = _("Invalid relation object: ")
    OPTION_ERROR_MSG = _("Invalid option object: ")
    YES_NO = ((0, _('No')), (1, _('Yes')),)
    DISPLAY_TAG = '<span id="{}">{}</span>'
    STORE_WRAPPER = '<div class="storage-wrapper">{}{}</div>'
    ELEMENT_TYPES = {
        DynamicColumn.BOOLEAN: '<select id="{}" name="{}">\n',
        DynamicColumn.CHOICE: '<select id="{}" name="{}">\n',
        DynamicColumn.DATE: ('<input id="{}" type="date" name="{}" '
                             'value="{}" />'),
        DynamicColumn.DATETIME: ('<input id="{}" type="datetime" name="{}" '
                                 'value="{}" />'),
        DynamicColumn.FLOAT: ('<input id="{}" name="{}" type="text" '
                              'value="{}" />'),
        DynamicColumn.NUMBER: ('<input id="{}" name="{}" type="number" '
                               'value="{}" />'),
        DynamicColumn.TEXT: ('<input id="{}" name="{}" size="50" type="text" '
                             'value="{}" />'),
        DynamicColumn.TEXT_BLOCK: ('<textarea class="large-text-field" '
                                   'id="{}" name="{}">{}</textarea>\n'),
        DynamicColumn.TIME: ('<input id="{}" type="time" name="{}" '
                             'value="{}" />'),
        }

    def __init__(self, tag_name, relation, prefix='', options=None,
                 display='False'):
        self.tag_name = tag_name
        self.relation = template.Variable(relation)
        self.prefix = prefix
        self.fk_options = template.Variable(options) if options else None
        self.display = eval(display)

    def render(self, context):
        """
        Render the results in an HTML friendly way.

        :param context: The context as provided by django.
        :type context: dict
        :rtype: The HTML element rendered for a specific dynamic column slug.
        """
        try:
            relation = self.relation.resolve(context)
        except template.VariableDoesNotExist:
            relation = None

        log.debug(ugettext("relation: %s, display: %s"),
                  relation, self.display)

        if relation:
            value_type = relation.get('value_type')

            if self.display:
                elem = self.DISPLAY_TAG
            else:
                elem = self.ELEMENT_TYPES.get(value_type, '')

            attr = "{}{}".format(self.prefix, relation.get('slug'))

            # Choices are a special case since we need to determine
            # what the options will be.
            if value_type == DynamicColumn.CHOICE:
                if self.fk_options:
                    # The fk_options variable should always be found since it
                    # is tested for in the tag's function.
                    fk_options = self.fk_options.resolve(context)
                    options = self._find_options(relation, fk_options)

                    if self.display:
                        elem = self._find_value(elem, attr, options, relation)
                    else:
                        elem = self._add_options(elem, attr, options, relation)

                        if (relation.get('store_relation', False) and
                            'selected' not in elem):
                            tmp_elem = self._find_value(
                                self.DISPLAY_TAG, 'store-' + attr, {},
                                relation)
                            elem = self.STORE_WRAPPER.format(elem, tmp_elem)
                else:
                    elem = "<span>{}{}</span>".format(self.OPTION_ERROR_MSG,
                                                      self.fk_options)
            elif value_type == DynamicColumn.BOOLEAN:
                if self.display:
                    elem = self._find_value(elem, attr, self.YES_NO, relation)
                else:
                    elem = self._add_options(elem, attr, self.YES_NO, relation)
            elif self.display:
                elem = elem.format("id-" + attr, relation.get('value', ''))
            else:
                elem = elem.format("id-" + attr, attr,
                                   relation.get('value', ''))
        else:
            elem = "<span>{}{}</span>".format(self.RELATION_ERROR_MSG,
                                              relation)

        return mark_safe(elem)

    def _find_options(self, relation, fk_options):
        """
        Find the options for this relation.

        The fk_option argument can either be a list or tuple of a single
        set of ``CHOICE`` options or a complete set in a dict of all
        ``CHOICE`` options. In the latter case the options will be found
        in the full list.

        :param relation: The meta data for a dynamic column.
        :type relation: dict
        :param fk_options: Can be the list of a specific slug's display
                           options or the full ``dynamicColumns`` dict object.
        :type fk_options: list or dict
        :rtype: The list of options.
        """
        if isinstance(fk_options, (list, tuple,)):
            options = fk_options
        else:
            slug = relation.get('slug')
            options = fk_options.get(slug, {})

            if not slug or not options:
                msg = _('Invalid key for relation, {}').format(relation)
                log.error(ugettext(msg))
                raise template.TemplateSyntaxError(msg)

        log.debug(ugettext("relation: %s, fk_options: %s, options: %s"),
                  relation, fk_options, options)
        return options

    def _add_options(self, elem, attr, options, relation):
        """
        Find the value in the options if it exists and set the selected
        property on the appropriate option. In the case of a stored relation
        find the selected option by the actual value as the PK is not
        available in this case.

        :param elem: The HTML element.
        :type elem: str
        :param attr: Text object to be used when creating the element's
                     attributes.
        :type attr: str
        :param options: The options used when creating the HTML select element.
        :type options: list
        :param relation: The meta data for a dynamic column.
        :type relation: dict
        :rtype: The populated HTML element.
        """
        elem = elem.format("id-" + attr, attr)
        buff = six.StringIO(elem)
        buff.seek(0, os.SEEK_END)
        value = relation.get('value', '')

        # Get the ID if the value is stored not the pk.
        if relation.get('store_relation', False):
            value = [k for k, v in options if v == value]
            value = value[0] if len(value) > 0 else 0

        if (isinstance(value, six.string_types)
            and value.isdigit()): # pragma: no cover
            value = int(value)

        for k, v in options:
            s = ""

            if k == value and value != 0:
                s = " selected"

            buff.write('<option value="{}"{}>{}</option>\n'.format(k, s, v))

        buff.write('</select>\n')
        elem = buff.getvalue()
        buff.close()
        log.debug(ugettext("elem: %s, attr: %s, options: %s, relation: %s, "
                           "value: %s"), elem, attr, options, relation, value)
        return elem

    def _find_value(self, elem, attr, options, relation):
        """
        Produce the element filled with the value. This method is used only
        for display mode and the element is usually a <span>.

        :param elem: The HTML element.
        :type eleb: str
        :param attr: Text object to be used when creating the element's
                     attributes.
        :type attr: str
        :param options: The options used when creating the HTML select element.
        :type options: list
        :param relation: The meta data for a dynamic column.
        :type relation: dict
        :rtype: The populated HTML element.
        """
        log.debug(ugettext("elem: %s, attr: %s, options: %s, relation: %s"),
                  elem, attr, options, relation)
        value_type = relation.get('value_type')
        value = relation.get('value', '')
        key = None

        # Get the key (PK or slug) then with the key get the value.
        if relation.get('store_relation', False):
            if value == '0' or value == 0:
                value = ''
        else:
            if value_type == DynamicColumn.BOOLEAN:
                if isinstance(value, six.string_types): # pragma: no cover
                    if value.isdigit():
                        key = 0 if int(value) == 0 else 1
                    elif value.lower() in ('true', 'false'):
                        key = 0 if value.lower() == 'false' else 1
                else:
                    key = 0 if value == 0 else 1
            elif (isinstance(value, six.string_types)
                  and value.isdigit()): # pragma: no cover
                key = int(value)
            else:
                key = value

            value = dict(options).get(key, '')

        elem = elem.format("id-" + attr, value)
        return elem


#
# single_display
#
# NOTE: Formatting of the doc string is to conform with django docs not
#       Sphinx.
#
@register.tag(name='single_display')
def single_display(parser, token):
    """
    Returns a context variable containing a single value where the data
    type is based on the type of object. You will need to warp the result
    in an html tag of your choice.

    Arguments::

      obj  -- A CollectionBase derived model object.
      slug -- The slug for the DynamicColumn type.
      as   -- Manditory delimiter.
      name -- Name for context variable similar to the slug name.

    Usage Examples::

      {% single_display <object> <slug> as <context name>  %}

      {% single_display obj country as country %}
    """
    try:
        tag_name, obj, slug, delimiter, name = token.split_contents()
    except ValueError:
        msg = _("{} tag requires four arguments.").format(
            token.contents.split()[0])
        raise template.TemplateSyntaxError(msg)

    if delimiter != 'as':
        msg = _("The third argument must be the word 'as' found '{}'.").format(
            delimiter)
        raise template.TemplateSyntaxError(msg)

    return SingleDisplayNode(tag_name, obj, slug, name)


class SingleDisplayNode(template.Node):
    """
    Node class for the ``single_display`` tag.
    """
    _NO = _('No')
    _YES = _('Yes')

    def __init__(self, tag_name, obj, slug, name):
        self.tag_name = tag_name
        self.obj = template.Variable(obj)
        self.slug = slug
        self.name = name

    def render(self, context):
        """
        Render the results into the context.

        :param context: The context as provided by django.
        :type context: dict
        :rtype: empty string
        """
        try:
            obj = self.obj.resolve(context)
        except template.VariableDoesNotExist:
            msg = _("The model object does not exist in the context, "
                    "found '{}'").format(self.obj)
            log.warning(ugettext(msg))
            raise template.VariableDoesNotExist(msg)

        context[self.name] = obj.get_key_value(self.slug)
        return ''


#
# combine_contexts
#
# NOTE: Formatting of the doc string is to conform with django docs not Sphinx.
#
@register.tag(name='combine_contexts')
def combine_contexts(parser, token):
    """
    Combines two context variables. Helps make the HTML a little less
    cluttered.

    Arguments::

      obj      -- An object in the context that has member objects.
      variable -- A variable that defines a member object name.

    Usage Examples::

      {% combine_contexts form.errors relation.slug %}
    """
    try:
        tag_name, obj, variable = token.split_contents()
    except ValueError:
        msg = _("{} tag requires two arguments.")
        raise template.TemplateSyntaxError(
            msg.format(token.contents.split()[0]))

    return CombineContextsNode(tag_name, obj, variable)


class CombineContextsNode(template.Node):
    """
    Node class for the ``combine_contexts`` tag.
    """

    def __init__(self, tag_name, obj, variable):
        self.tag_name = tag_name
        self.obj = template.Variable(obj)
        self.variable = template.Variable(variable)

    def render(self, context):
        """
        Render the results as a template variable.

        :param context: The context as provided by django.
        :type context: dict
        :rtype: empty string
        """
        result = self.obj.resolve(context).get(self.variable.resolve(context))
        return result and result or ''
