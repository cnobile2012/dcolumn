#
# dcolumn/common/view_mixins.py
#

import logging, json
from django.http import HttpResponse

log = logging.getLogger('dcolumn.views')


class JSONResponseMixin(object):
    """
    A mixin that can be used to render a JSON response.
    """
    response_class = HttpResponse

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        response_kwargs['content_type'] = 'application/json'
        return self.response_class(self.convert_context_to_json(context),
                                   **response_kwargs)

    def convert_context_to_json(self, context):
        """
        Convert the context dictionary into a JSON object
        """
        return json.dumps(context)


class AjaxableResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """
    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        #log.debug("data: %s", data)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)

        if self.request.is_ajax():
            return self.render_to_json_response(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)

        if self.request.is_ajax():
            data = {'pk': self.object.pk}
            return self.render_to_json_response(data)
        else:
            return response
