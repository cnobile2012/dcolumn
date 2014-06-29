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

    def get_dynamic_column_context_data(self, obj=None):
        context = {}
        fk_slugs = DynamicColumn.objects.get_fk_slugs()

        for name in ColumnCollection.objects.get_active_relation_items():
            model, field = dcolumn_manager.choice_map.get(name)
            objects = context.setdefault(u'dynamicColumns', {})
            values = [(r.pk, getattr(r, field))
                      for r in model.objects.dynamic_column()]
            values.insert(0, (0, "Choose a value"))
            objects[fk_slugs.get(name)] = values

        return context

    def get_relation_context_data(self, obj=None, **kwargs):
        form = kwargs.get(u'form')

        if form:
            relations = form.get_display_data()
        else:
            relations = ColumnCollection.objects.serialize_columns(obj=obj)

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
        Get context data for the Parent KeyValue objects.

        Do not call super on get_context_data, it puts self into the context
        which is not valid JSON.
        """
        context = {u'valid': True}

        try:
            context.update(self.get_dynamic_column_context_data())
            context.update(self.get_relation_context_data(**kwargs))
        except Exception, e:
            context[u'valid'] = False
            context[u'message'] = "Error occured: {}".format(e)

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
        Get context data for the Parent KeyValue objects.
        """
        context = super(ParentCreateView, self).get_context_data(**kwargs)
        context.update(self.get_dynamic_column_context_data())
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
        context = super(CollectionViewMixin, self).get_context_data(**kwargs)
        context.update(self.get_dynamic_column_context_data())
        context.update(self.get_relation_context_data(
            obj=self.object, **kwargs))
        context.update({u'css': dcolumn_manager.css_container_map})
        return context
