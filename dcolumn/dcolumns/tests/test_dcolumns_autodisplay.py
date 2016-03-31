# -*- coding: utf-8 -*-
#
# dcolumn/dcolumns/tests/test_dcolumns_autodisplay.py
#
# WARNING: These unittests can only be run from within the original test
#          framework from https://github.com/cnobile2012/dcolumn.
#

from StringIO import StringIO

from django.test import TestCase
from django.template import Template, Context

from example_site.books.models import Author, Book, Promotion, Publisher
from dcolumn.dcolumns.models import DynamicColumn

from ..views import ContextDataMixin
from .test_dcolumns_models import BaseDcolumns


class ViewMixinTest(ContextDataMixin):
    model = None
    object = None

    def get_context_data(self, **kwargs):
        context = {}
        context.update(self.get_dynamic_column_context_data(**kwargs))
        context.update(self.get_relation_context_data(
            obj=self.object, **kwargs))
        return context


class TestAutoDisplay(BaseDcolumns):

    def __init__(self, name):
        super(TestAutoDisplay, self).__init__(name)

    def setUp(self):
        super(TestAutoDisplay, self).setUp()

    def _setup_template(self, model, object, prefix=None, options=None,
                        display=None):
        # Setup the context.
        vmt = ViewMixinTest()
        vmt.model = model
        vmt.object = object
        context = Context(vmt.get_context_data())
        # Run the test.
        buff = StringIO()
        buff.write("{% load autodisplay %}")
        buff.write("{% for relation in relations.values %}")
        p = " prefix={}".format(prefix) if prefix is not None else ''
        o = " options={}".format(options) if options is not None else ''
        d = " display={}".format(display) if display is not None else ''
        cmd = ("{{% auto_display relation{}{}{} %}}").format(p, o, d)
        buff.write(cmd)
        buff.write("{% endfor %}")
        template = buff.getvalue()
        buff.close()
        tr = Template(template)
        return context, tr.render(context)

    def test_BOOLEAN_display(self):
        """
        Test that the BOOLEAN type displays correctly.
        """
        #self.skipTest("Temporarily skipped")
        # Create database objects.
        dc0 = self._create_dynamic_column_record(
            "Ignore", DynamicColumn.BOOLEAN, 'book_top', 1)
        book, b_cc, b_values = self._create_book_objects(extra_dcs=[dc0])
        value = 'FALSE'
        kv0 = self._create_key_value_record(book, dc0, value)
        b_values[dc0.slug] = kv0.value
        context, result = self._setup_template(Book, book, display=True)
        msg = "Result: {}, context: {}, values: {}".format(
            result, context, b_values)
        self.assertEqual(result.count('span'), 4, msg)
        self.assertTrue("No" in result, msg)





