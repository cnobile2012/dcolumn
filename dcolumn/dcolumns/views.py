#
# dcolumn/dcolumns/views.py
#

import logging

from django.shortcuts import render
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator

from dcolumn.common.view_mixins import JSONResponseMixin
from dcolumn.common.decorators import dcolumn_login_required
from .models import DynamicColumn, ColumnCollection
from .manager import dcolumn_manager

log = logging.getLogger('dcolumn.views')


class ContextDataMixin(object):

    def get_dynamic_column_context_data(self, class_name=u'', **kwargs):
        context = {}
        fk_slugs = DynamicColumn.objects.get_fk_slugs()
        name = dcolumn_manager.get_collection_name(class_name)

        for model_name in ColumnCollection.objects.get_active_relation_items(
            name):
            model, field = dcolumn_manager.choice_map.get(model_name)
            objects = context.setdefault(u'dynamicColumns', {})
            values = [(r.pk, getattr(r, field))
                      for r in model.objects.dynamic_column()]
            values.insert(0, (0, "Choose a value"))
            objects[fk_slugs.get(model_name)] = values
            log.debug("model_name: %s, model: %s, field: %s, fk_slugs: %s, "
                      "values: %s", model_name, model, field, fk_slugs, values)

        log.debug("context: %s", context)
        return context

    def get_relation_context_data(self, class_name=u'', obj=None, **kwargs):
        form = kwargs.get(u'form')

        if form:
            relations = form.get_display_data()
        else:
            name = dcolumn_manager.get_collection_name(class_name)
            relations = ColumnCollection.objects.serialize_columns(
                name, obj=obj)

        log.debug("relations: %s", relations)
        return {u'relations': relations}


#
# CollectionAJAXView
#
class CollectionAJAXView(JSONResponseMixin, TemplateView, ContextDataMixin):
    http_method_names = ('get',)

    @method_decorator(dcolumn_login_required)
    def dispatch(self, *args, **kwargs):
        return super(CollectionAJAXView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Get context data for the KeyValue objects.

        Do not call super on get_context_data, it puts self into the context
        which is not valid JSON.
        """
        log.debug("kwargs: %s", kwargs)
        context = {u'valid': True}

        try:
            context.update(self.get_dynamic_column_context_data(**kwargs))
            context.update(self.get_relation_context_data(**kwargs))
        except Exception, e:
            context[u'valid'] = False
            context[u'message'] = "Error occured: {}".format(e)
            log.error(context[u'message'], exc_info=True)

        return context

collection_ajax_view = CollectionAJAXView.as_view()


#
# CollectionCreateUpdateViewMixin
#
class CollectionCreateUpdateViewMixin(ContextDataMixin):

    def get_initial(self):
        return {'request': self.request}

    def get_context_data(self, **kwargs):
        """
        Get context data for the KeyValue objects.
        """
        kwargs[u'class_name'] = self.model.__name__
        context = super(CollectionCreateUpdateViewMixin,
                        self).get_context_data(**kwargs)
        context.update(self.get_dynamic_column_context_data(**kwargs))
        context.update(self.get_relation_context_data(**kwargs))
        context.update({u'css': dcolumn_manager.css_container_map})
        return context


#
# CollectionDetailViewMixin
#
class CollectionDetailViewMixin(ContextDataMixin):

    def get_context_data(self, **kwargs):
        """
        Get context data for the KeyValue objects.
        """
        kwargs[u'class_name'] = self.model.__name__
        context = super(CollectionDetailViewMixin,
                        self).get_context_data(**kwargs)
        context.update(self.get_dynamic_column_context_data(**kwargs))
        context.update(self.get_relation_context_data(
            obj=self.object, **kwargs))
        context.update({u'css': dcolumn_manager.css_container_map})
        return context
