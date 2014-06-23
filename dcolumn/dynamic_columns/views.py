#
# dcolumn/dynamic_columns/views.py
#

import logging

from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator

from dcolumn.common.view_mixins import JSONResponseMixin
from dcolumn.common.decorators import dcolumn_login_required
from .models import DynamicColumn, DynamicColumnItem, Parent
from .forms import ParentForm
from .manage import choice_manager

log = logging.getLogger('dcolumn.views')


class ContextDataMixin(object):

    def get_dynamic_column_context_data(self, obj=None):
        context = {}
        fk_slugs = DynamicColumn.objects.get_fk_slugs()

        for name in DynamicColumnItem.objects.get_active_relation_items():
            model, field = choice_manager.choice_map.get(name)
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
            relations = DynamicColumnItem.objects.serialize_columns(obj=obj)

        log.debug("relations: %s", relations)
        return {u'relations': relations}


#
# DynamicColumnAJAXView
#
class DynamicColumnAJAXView(JSONResponseMixin, TemplateView, ContextDataMixin):
    http_method_names = ('get',)

    @method_decorator(dcolumn_login_required)
    def dispatch(self, *args, **kwargs):
        return super(DynamicColumnAJAXView, self).dispatch(*args, **kwargs)

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

dynamic_column_ajax_view = DynamicColumnAJAXView.as_view()


#
# ParentCreateView
#
class ParentCreateView(CreateView, ContextDataMixin):
    template_name = u'dynamic_columns/parent_create_view.html'
    form_class = ParentForm
    model = Parent

    def get_initial(self):
        return {'request': self.request}

    def get_context_data(self, **kwargs):
        """
        Get context data for the Parent KeyValue objects.
        """
        context = super(ParentCreateView, self).get_context_data(**kwargs)
        context.update(self.get_dynamic_column_context_data())
        context.update(self.get_relation_context_data(**kwargs))
        context.update({u'css': choice_manager.css_container_map})
        return context

    def get_success_url(self):
        url = self.object.get_absolute_url()
        url += '?created=true'
        return url

parent_create_view = ParentCreateView.as_view()


#
# ParentUpdateView
#
class ParentUpdateView(UpdateView, ContextDataMixin):
    template_name = u'dynamic_columns/parent_create_view.html'
    form_class = ParentForm
    model = Parent

    def get_initial(self):
        return {'request': self.request}

    def get_context_data(self, **kwargs):
        """
        Get context data for the Parent KeyValue objects.
        """
        context = super(ParentUpdateView, self).get_context_data(**kwargs)
        context.update(self.get_dynamic_column_context_data())
        context.update(self.get_relation_context_data(**kwargs))
        context.update({u'css': choice_manager.css_container_map})
        return context

    def get_success_url(self):
        url = self.object.get_absolute_url()
        url += '?updated=true'
        return url

parent_update_view = ParentUpdateView.as_view()


#
# ParentDetailView
#
class ParentDetailView(DetailView, ContextDataMixin):
    template_name = u'dynamic_columns/parent_detail_view.html'
    model = Parent

    def get_context_data(self, **kwargs):
        """
        Get context data for the Parent KeyValue objects.
        """
        context = super(ParentDetailView, self).get_context_data(**kwargs)
        context.update(self.get_dynamic_column_context_data())
        context.update(self.get_relation_context_data(
            obj=self.object, **kwargs))
        context.update({u'css': choice_manager.css_container_map})
        # Create actions if any.
        parent = kwargs.get(u'object')
        pk = parent and parent.id or 0
        actions = [
            {u'name': u'Create a New Record',
             u'url': reverse(u'parent-create')},
            {u'name': u'Edit this Record',
             u'url': reverse(u'parent-update', args=(pk,))},
            ]
        context[u'actions'] = actions
        # Create messages if any.
        info_message = {}

        for flag in (u'created', u'updated',):
            info_message[flag] = bool(self.request.GET.get(flag, u''))

        context[u'info_message'] = info_message
        return context

parent_detail_view = ParentDetailView.as_view()
