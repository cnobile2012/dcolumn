# -*- coding: utf-8 -*-
#
# dcolumn/dcolumns/views.py
#
"""
Dynamic Column dependent views.
"""
__docformat__ = "restructuredtext en"

import logging

from django.db.transaction import atomic
from django.forms import formset_factory
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from dcolumn.common.view_mixins import JSONResponseMixin
from dcolumn.common.decorators import dcolumn_login_required
from .models import DynamicColumn, ColumnCollection
from .manager import dcolumn_manager

log = logging.getLogger('dcolumns.dcolumns.views')


class ContextDataMixin(object):
    """
    Mixin for context data.
    """
    formset_class = None

    def get_dynamic_column_context_data(self, **kwargs):
        """
        Generates the data needed for HTML select option tags. This data is
        in a dict keyed by ``dynamicColumns`` giving it a namespace in the
        context. The slug for each ``CHOICE`` object is the key to the list
        used for the option tags.

        Example of Output::

          {'dynamicColumns': {
           u'author': [(0, 'Choose a value'),
                       (17, u'Jeremy Blum'),
                       (5, u'John Iovine'),
                       (23, u'Lauren Darcey & Shane Conder'),
                       (25, u'Peter Gasston'),
                       (6, u'Rajaram Regupathy'),
                       (7, u'Richard Stones'),
                       (15, u'Ruth Suehle & Tom Callaway'),
                       (8, u'Toby Segaran')],
           u'language': [(0, 'Choose a value'),
                         (1, 'Chinese'),
                         (2, 'English'),
                         (3, 'Portuguese'),
                         (4, 'Russian'),
                         (5, 'Japanese')],
           ...}
          }

        :rtype: dict
        """
        context = {}
        fk_slugs = DynamicColumn.objects.get_fk_slugs()
        name = kwargs.pop('class_name', None) # Used in AJAX call only.

        if not name:
            name = dcolumn_manager.get_collection_name(self.model.__name__)

        for model_name in ColumnCollection.objects.get_active_relation_items(
            name):
            model, field = dcolumn_manager.choice_map.get(model_name)
            objects = context.setdefault('dynamicColumns', {})
            values = [(r.pk, getattr(r, field))
                      for r in model.objects.model_objects()]
            values.insert(0, (0, "Choose a value"))
            objects[fk_slugs.get(model_name)] = values
            log.debug("model_name: %s, model: %s, field: %s, fk_slugs: %s, "
                      "values: %s", model_name, model, field, fk_slugs, values)

        log.debug("context: %s", context)
        return context

    def get_relation_context_data(self, obj=None, form=None, **kwargs):
        """
        Generates an OrderedDict of meta data needed to determine how the
        values of a ``KeyValue`` is to interpreted. If ``obj`` is supplied
        and ``form`` is not supplied values from the ``KeyWord`` objects
        will be included in the list of meta data. If ``form`` is supplied
        the meta data will be taken from the Django form exclusively.

        Example of Output::

          OrderedDict([
            (19,
              {'location': 'book-bottom',
               'name': 'Promotion',
               'order': 1,
               'pk': 19,
               'relation': 2,
               'required': False,
               'slug': 'promotion',
               'store_relation': True,
               'value_type': 2}),
            (20,
              {'location': 'book-center',
               'name': 'Language',
               'order': 6,
               'pk': 20,
               'relation': 1,
               'required': False,
               'slug': 'language',
               'store_relation': False,
               'value_type': 2}),
            ...])

        :param obj: Optional model object that inherits from
                    ``CollectionBase``.
        :type obj: object
        :param form: Optional form object.
        :type form: Django Form object.
        :rtype: OrderedDict
        """
        if form:
            relations = form.relations
        else:
            name = kwargs.pop('class_name', None) # Used in AJAX call only.
            by_slug = kwargs.pop('by_slug', False)

            if not name:
                name = dcolumn_manager.get_collection_name(self.model.__name__)

            relations = ColumnCollection.objects.serialize_columns(
                name, obj=obj, by_slug=by_slug)

        log.debug("relations: %s", relations)
        return {'relations': relations}


#
# CollectionAJAXView
#
class CollectionAJAXView(JSONResponseMixin, TemplateView, ContextDataMixin):
    """
    Web service endpoint used in the Django admin to format ``KeyValue``
    values as per the ``DynamicColumn`` meta data.
    """
    http_method_names = ('get',)

    @method_decorator(dcolumn_login_required)
    def dispatch(self, *args, **kwargs):
        """
        Django view dispatch decorated for login requierments.
        """
        return super(CollectionAJAXView, self).dispatch(*args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        # Remove the view object--it cannot be serialized and we don't
        # need it.
        context.pop('view', None)
        return self.render_to_json_response(context, **response_kwargs)

    def get_data(self, **context):
        """
        Get context data for the ``KeyValue`` objects.

        Do not call super on get_context_data, it puts self into the
        context which is not valid JSON.
        """
        log.debug("context: %s", context)
        context['valid'] = True

        try:
            context.update(self.get_dynamic_column_context_data(**context))
            context.update(self.get_relation_context_data(**context))
        except Exception as e:
            context['valid'] = False
            context['message'] = "Error occurred: {}".format(e)
            log.error(context['message'], exc_info=True)

        return context

collection_ajax_view = CollectionAJAXView.as_view()


#
# CollectionCreateUpdateViewMixin
#
class CollectionCreateUpdateViewMixin(ContextDataMixin):
    """
    This mixin is needed by any create or update view where the view is
    associated with a model that inherits ``CollectionBase``.
    """

    def get_initial(self):
        """
        Provides initial data to forms.
        """
        return {'request': self.request, 'parent_instance': self.object}

    def get_context_data(self, **kwargs):
        """
        Get context data for the ``KeyValue`` objects.
        """
        context = super(CollectionCreateUpdateViewMixin, self
                        ).get_context_data(**kwargs)
        context.update(self.get_dynamic_column_context_data(**kwargs))
        context.update(self.get_relation_context_data(
            obj=self.object, **kwargs))
        context.update({'css': dcolumn_manager.css_container_map})
        return context


#
# CollectionDetailViewMixin
#
class CollectionDetailViewMixin(ContextDataMixin):
    """
    This mixin is needed by any detail view where the view is associated
    with a model that inherits ``CollectionBase``.
    """
    def get_context_data(self, **kwargs):
        """
        Get context data for the ``KeyValue`` objects.
        """
        context = super(
            CollectionDetailViewMixin, self).get_context_data(**kwargs)
        context.update(self.get_dynamic_column_context_data(**kwargs))
        context.update(self.get_relation_context_data(
            obj=self.object, **kwargs))
        context.update({'css': dcolumn_manager.css_container_map})
        return context
