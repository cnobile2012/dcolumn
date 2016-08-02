*************
Configuration
*************

1. Add ``dcolumn`` to your INSTALLED_APPS settings:

.. code::

    INSTALLED_APPS = (
        ...
        'dcolumn.dcolumns',
        )

2. Add the following code stanza to the settings file. As of now there
   is only a single API call to the internal API. It is by default only
   accessed by logged in users. You can change this behavior by setting
   ``INACTIVATE_API_AUTH`` to ``True``.

.. code::

    DYNAMIC_COLUMNS = {
        # To allow anybody to access the API set to True.
        'INACTIVATE_API_AUTH': False,
        }

3. If you want authorization on the API you will need to set the standard
   Django setting 'LOGIN_URL' to something reasonable.

.. code::

    # Change the URL below to your login path.
    LOGIN_URL = "/admin/"

4. To define page location for each field that you enter into the
   ``DynamicColumn`` table pass a tuple of tuples with the first variable as
   the key and the second variable as the value. They would be reference as
   ``css.top``, ``css.center``, etc. You can add as many of these as you wish.
   The first object of the tuple becomes a variable so these names must
   conform to standard Python variable characters.

.. code::

    dcolumn_manager.register_css_containers(
           (('top', 'top-container'),
            ('center', 'center-container'),
            ('bottom', 'bottom-container')
            ))

5. The models you create that use DColumn need to be a subclass of the
   ``CollectionBase`` model base class. Your model managers needs to subclass
   ``CollectionBaseManager``

.. code::

    from dcolumn.dcolumns.models import CollectionBase, CollectionBaseManager

6. Optionally any of your models and managers can subclass a few mixins.

.. code::

    from dcolumn.common.model_mixins import (
        UserModelMixin, TimeModelMixin, StatusModelMixin,
        StatusModelManagerMixin, ValidateOnSaveMixin)

* UserModelMixin--Adds a creator and updater ``ForeignKey`` fields to User
  on your model.
* TimeModelMixin--Adds a created and updated ``DateTimeField`` fields to your
  models.
* StatusModelMixin--Adds an active ``BooleanField`` field to your models.
* StatusModelManagerMixin--Adds a DB access method to your model manager.
* ValidateOnSaveMixin--Calls your clean method in the model. This should
  be the last class inherited in your model.

7. Any forms used with your models will need to subclass
   ``CollectionBaseFormMixin``. You do not need to subclass
   ``forms.ModelForm``, this is done for you already by
   ``CollectionBaseFormMixin``.

.. code::

    from dcolumn.dcolumns.forms import CollectionBaseFormMixin

8. Any views need to subclass ``CollectionCreateUpdateViewMixin`` or
   ``CollectionDetailViewMixin``. These must be first in the MRO before the
   class-based view that you will use. Once again see the example code.

.. code::

    from dcolumn.dcolumns.views import (
        CollectionCreateUpdateViewMixin, CollectionDetailViewMixin)

9. If the ``Choice`` mechanism is used the quasi models that you will build
   need to subclass ``BaseChoice`` in the models and ``BaseChoiceManager``
   in the managers.

.. code::

    from dcolumn.common.choice_mixins import BaseChoice, BaseChoiceManager

10. The final peice that needs to be configured is to register all you models
    and ``Choice`` models at the end of each file.

.. code::

    from dcolumn.dcolumns.manager import dcolumn_manager

    ...

    dcolumn_manager.register_choice(<model>, <num>, 'field')


.. warning::

  Once you have registered the models and choices with
  ``dcolumn_manager.register_choice()`` it is not a good idea to change it,
  as the numeric value is stored in the ``DynamicColumn`` table. So with that
  said, if you really need to change it you can, but you must manually modify
  the ``Relation`` field for all affected rows in the ``DynamicColumn`` table.

  If you need to hardcode any of the slugs elsewhere in your code then you
  definitely need to set the *Preferred Slug* field in the admin under
  **Status** to your desired slug. If you do not do this the slug will track
  any changes made to the *Name* field which could break code that depends on
  the slug value. The only caveat is that the slug will now track the
  *Preferred Slug* field, so don't change it after your code is using the slug
  value.
