*************
Configuration
*************

1. Add ``dcolumn`` to your INSTALLED_APPS settings:

.. code::

    INSTALLED_APPS = (
        ...
        'dcolumn.dcolumns',
        )

2. Add the following code stanza to the settings file. The ``COLLECTIONS``
   key points to key value pairs where the key is the model name and the value
   is a unique name given to a collection set. This collection set is kept
   in the model named ``ColumnCollection``. As of now there is only a single
   asynchronous call to the internal API. It is by default only accessed by
   logged in users. You can change this behavior by setting
   ``INACTIVATE_API_AUTH`` to ``True``.

.. code::

    DYNAMIC_COLUMNS = {
        # The default key/value pairs for the ColumnCollection object to use
        # for all tables that use dcolumn. The key is the table name and the
        # value is the name used in the ColumnCollection record.
        'COLLECTIONS': {
            'Book': 'Book Current',
            'Author': 'Author Current',
            'Publisher': 'Publisher Current',
            'Promotion': 'Promotion Current',
            },
        # To allow anybody to access the API set to True.
        'INACTIVATE_API_AUTH': False,
        }

3. If you want authorization on the API you will need to set the standard
   Django setting 'LOGIN_URL' to something reasonable.

.. code::

    # Change the URL below to your login path.
    LOGIN_URL = "/admin/"

4. To define page location of each new fields that you enter into the
   ``DynamicColumn`` table pass a tuple of tuples with the first variable as
   the key and the second variable as the value. They would be reference as
   ``css.top``, ``css.center``, etc.

.. code::

    dcolumn_manager.register_css_containers(
           (('top', 'top-container'),
            ('center', 'center-container'),
            ('bottom', 'bottom-container')
            ))

5. The models need to subclass the ``CollectionBase`` model base class from
   dcolumn. The model manager needs to subclass ``StatusModelManagerMixin``
   and also needs to implement two methods named ``dynamic_column`` and
   ``get_choice_map``. See the example code.

6. The ``CollectionBaseManagerBase`` manager base class from dcolumn should
   also be sub-classed to pick up a few convenience methods. This is not
   mandatory.

7. Any forms used with a dynamic column model will need to subclass
   ``CollectionFormMixin``. You do not need to subclass ``forms.ModelForm``,
   this is done for you already by ``CollectionFormMixin``.

8. Any views need to subclass ``CollectionCreateUpdateViewMixin`` which must
   be before the class-based view that you will use. Once again see the example
   code.

********
Do Not's
********

Once you have registered the choices or models with
``dcolumn_manager.register_choice()`` do not change it, as the numeric value
is stored in ``DynamicColumn`` table rows. So obviously if you really really
really need to change it you can, but you must manually modify the
``Relation`` in all the affected rows in the ``DynamicColumn`` table.

You will see that this is all rather simple and you'll need to write very
little code to support DynamicColumns.

If you need to hardcode any of the slugs elsewhere in your code then you
definitely need to set the 'Preferred Slug' field to your desired slug. If
you do not do this the slug will track any changes made to the 'Name' fields
which could break your code. The only caveat is that the slug will now track
the 'Preferred Slug' field, so don't change it after your code is using the
slug value. I've put this out of the way and hidden in the admin 'Status'
section of the 'Dynamic Columns' entries.
