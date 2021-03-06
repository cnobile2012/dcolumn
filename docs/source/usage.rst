*****
Usage
*****

Models and Model Managers
=========================
The models you create that use DColumn need to be a subclass of the
``CollectionBase`` model class and optionally ``ValidateOnSaveMixin``
which will call the model's ``clean`` method.

Your model managers needs to subclass ``CollectionBaseManager`` and
optionally ``StatusModelManagerMixin`` which supplies extra methods to the
manager.

.. code::

    from dcolumn.dcolumns.models import (
        CollectionBase, CollectionBaseManager)
    from dcolumn.common.model_mixins import (
        StatusModelManagerMixin, ValidateOnSaveMixin)
    from dcolumn.dcolumns.manager import dcolumn_manager

    class MyNewClassManager(CollectionBaseManager,
                            StatusModelManagerMixin):
        pass

    class MyNewClass(CollectionBase, ValidateOnSaveMixin):
        name = models.CharField(max_length=250)

        objects = MyNewClassManager()

        def clean(self):
            ...

    dcolumn_manager.register_choice(MyNewClass, 1, 'name')

The predefined fields on ``CollectionBase`` are:
  * *column_collection*--ForeignKey to the ``ColumnCollection`` model.
  * *creator*--The user object that created this record.
  * *created*--A DateTimeField of when the record was created.
  * *updater*--The user that last updated this record.
  * *updated*--A DateTimeField of when the record was last updated.
  * *active*--BooleanField indicating if this record is currently active.

Views
=====
Views need to subclass ``CollectionCreateUpdateViewMixin`` or
``CollectionDetailViewMixin``. These must be first in the MRO before the
class-based view that you will use. See
:example-code:`views.py <books/views.py#L22>` and
:example-code:`views.py <books/views.py#L54>` for example code.

.. code::

    from django.views.generic import CreateView, UpdateView, DetailView
    from dcolumn.dcolumns.views import (
        CollectionCreateUpdateViewMixin, CollectionDetailViewMixin)

    class MyNewCreateView(CollectionCreateUpdateViewMixin, CreateView):
        ...

    class MyNewUpdateView(CollectionCreateUpdateViewMixin, UpdateView):
        ...

    class MyNewDetailView(CollectionCreateUpdateViewMixin, DetailView):
        ...

Forms
=====
Forms need to subclass ``CollectionBaseFormMixin``. Add any dcolumn fields
to your form. The ``CollectionBaseFormMixin`` is a ``forms.ModelForm``
form so you should not need to add the fields from your model unless
changes need to be made as is usually done in Django. Be sure to add the
``fields`` and ``exclude`` from the mixin to your ``fields`` and
``exclude`` in the Meta class.
See :example-code:`forms.py#L32 <books/forms.py>` for example code.

.. code::

    from dcolumn.dcolumns.forms import CollectionBaseFormMixin
    from .models import MyNewClass

    class MyNewForm(CollectionBaseFormMixin):
        name = forms.CharField(
            max_length=250, strip=True, required=True)
        address_1 = forms.CharField(
            max_length=250, strip=True, required=False)
        address_2 = forms.CharField(
            max_length=250, strip=True, required=False)
        city = forms.CharField(
            max_length=250, strip=True, required=False)
        state = forms.CharField(
            max_length=250, strip=True, required=False)
        country = forms.CharField(
            max_length=250, strip=True, required=False)
        postal_code = forms.CharField(
            max_length=250, strip=True, required=False)

        class Meta:
            model = MyNewClass
            fields = ['name', 'address_1', 'address_2', 'city', 'state',
                      'country', 'postal_code',
                     ] + CollectionBaseFormMixin.Meta.fields
            exclude = ['your_exclude_field',
                      ] + CollectionBaseFormMixin.Meta.exclude

Admin
=====
The ``column_collection`` field **must** be included in your admin
``fieldsets`` or ``fields`` member objects.

.. code::

   class MyAdmin(admin.ModelAdmin):
       fieldsets = (
           (None, {'fields': ('...', 'column_collection', '...',)}),
           )

Pseudo Models (Choices)
=======================
If the *Choice* mechanism is used the pseudo models that you build need to
subclass ``BaseChoice`` and the model managers need to subclass
``BaseChoiceManager``.

These pseudo models let you create a list of choices somewhat similar to
the standard Django choice that can be used in Django model fields.

There are two ways to set the ``VALUES`` member object in the manager
class. The first method permits only one field in the pseudo model
and the second method permits multiple fields.
See :example-code:`choices.py<books/choices.py#L20>` and
:dcolumn-code:`test_dcolumns_manager.py
<dcolumns/tests/test_dcolumns_manager.py#L25>` for example code.

.. code::

    VALUES = ('Green', 'Red', 'Blue',)
    FIELD_LIST = ('color',)

or

.. code::

    VALUES = (('Arduino', 'Mega2560'), ('Raspberry Pi', 'B+'),)
    FIELD_LIST = ('hardware', 'model',)

All pseudo models will automatically define a ``pk`` field.

.. code::

    from dcolumn.common.choice_mixins import BaseChoice, BaseChoiceManager
    from dcolumn.dcolumns.manager import dcolumn_manager

    class MyNewPseudoClassManager(BaseChoiceManager):
        VALUES = ('Green', 'Red', 'Blue',)
        FIELD_LIST = ('color',)

        def __init__(self):
            super(MyNewPseudoClassManager, self).__init__()

    class MyNewPseudoClass(BaseChoice):
        pk = 0
        color = ''

        objects = MyNewPseudoClassManager()

        def __str__(self):
            return self.color

    dcolumn_manager.register_choice(MyNewPseudoClass, 2, 'color')

Remember when registering a `Dcolumn` model or a pseudo model to increment
the second argument as shown above. No two can have the same value. A
``ValueError`` will be raised if you use the same number more than once.

.. warning::

  Once you have registered the models and choices with
  ``dcolumn_manager.register_choice()`` it is not a good idea to change
  them, as the numeric values are stored in the ``DynamicColumn`` table.
  So with that said, if you really need to change them you can, but you
  must manually modify the ``Relation`` field for all affected rows in
  the ``DynamicColumn`` table through the admin.

  If you need to hardcode any of the slugs elsewhere in your code then you
  definitely need to set the *Preferred Slug* field in the admin under
  **Status** to your desired slug. If you do not do this the slug will
  track any changes made to the *Name* field which could break code that
  depends on the slug value. The only caveat is that the slug will now
  track the *Preferred Slug* field, so don't change it after your code is
  using the slug value.

Optional Mixins
===============
Optionally any of your models and managers other than the ones that use
*DColumn* can subclass a few mixins.

.. code::

    from dcolumn.common.model_mixins import (
        UserModelMixin, TimeModelMixin, StatusModelMixin,
        StatusModelManagerMixin, ValidateOnSaveMixin)

* UserModelMixin

  Adds ``creator`` and ``updater`` ``ForeignKey`` fields from your User
  model to your model. See ``UserAdminMixin`` below on how to populate
  these fields in your admin. It is your responsibility to populate these
  fields in places other than the admin. See below for one method on how
  to do this.

  First put the request object in the form from your view. Then populate
  the fields in the your form's ``save`` method.

.. code::

    class MyNewView(...):

        ...

        def get_initial(self):
            """
            Provides initial data to forms.
            """
            return {'request': self.request}

.. code::

    class MyNewForm(forms.ModelForm):

        ...

        def save(self, commit=True):
            request = self.initial.get('request')

            if request:
                inst.updater = request.user

                # Populate the creator only on new records.
                if not hasattr(inst, 'creator') or not inst.creator:
                    inst.creator = request.user
                    inst.active = True

* UserAdminMixin

  Saves the ``request.user`` to the ``creator`` and ``updater`` in your
  admin when ``UserModelMixin`` is used.

* TimeModelMixin

  Adds ``created`` and ``updated`` ``DateTimeField`` fields to your
  models. This mixin will save the UTC aware time in the two fields.

* StatusModelMixin

  Adds an ``active`` ``BooleanField`` field to your models. See the above
  code snippet on how to populate the active field in the form's ``save``
  method.

* StatusModelManagerMixin

  Adds a DB access method to your model manager. See
  :dcolumn-code:`model_mixins.py<common/model_mixins.py#L154>` for how it
  is implemented.

* ValidateOnSaveMixin

  Calls the clean method on the model. This should be the last class
  inherited in your model. The one farthermost on the right.

.. code::

    class MyNewModel(..., ValidateOnSaveMixin):
        ...

        def clean(self):
            ...
