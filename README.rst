====================================
Django Tool to Create Dynamic Fields
====================================

.. image:: http://img.shields.io/pypi/v/django-dcolumns.svg
   :target: https://pypi.python.org/pypi/django-dcolumns
   :alt: PyPI Version

.. image:: http://img.shields.io/travis/cnobile2012/dcolumn/master.svg
   :target: http://travis-ci.org/cnobile2012/dcolumn
   :alt: Build Status

.. image:: http://img.shields.io/coveralls/cnobile2012/dcolumn/master.svg
   :target: https://coveralls.io/r/cnobile2012/dcolumn
   :alt: Test Coverage

.. image:: https://img.shields.io/pypi/dm/django-dcolumns.svg
   :target: https://pypi.python.org/pypi/django-dcolumns
   :alt: PyPI Downloads

********
Overview
********

DColumn is a Django plugin that lets the developer add columns to a model
dynamically. It does this in the same way that the admin uses an inline model
matter-of-fact that is exactly how the additional columns are displayed in
the admin. The only exception is that there is special JavaScript that
converts the column type to the type you have previously set it to.

This can be done, because any type of field can be represented as a string.
There are two methods on any model you define as a Dcolumn model that does
conversion in and out of the type you have set.

.. todo::
   Add a reference to readthedocs.org.

.. warning::
   Version 1.0 is a complete rewrite of Django DColumns and is NOT backwards
   compatible with previous versions.

********
Provides
********

1. ``DynamicColumn`` model to define the type of fields you want.
2. ``ColumnCollection`` model to group collections of fields for different
   models that inherit ``CollectionBase``.
3. ``KeyValue`` model that stores the field data.
4. An instance of the ``DynamicColumnManager`` that manages the system. The
   instance is ``dcolumn_manager``.
5. A ``CollectionBaseFormMixin`` to use in the forms you define for the
   models that inherit ``CollectionBase``.
6. A template tag (``auto_display``) to create the HTML for the defined
   fields. This tag will can create both an input or display type field.
7. A template tag (``single_display``) which rturns a context variable of
   your choice converted to the appropreate data type.
8. A template tag (``combine_contexts``) used to combine two context
   variables. This is most often used to get the Django field error messages.


Feel free to contact me at: carl dot nobile at gmail.com
