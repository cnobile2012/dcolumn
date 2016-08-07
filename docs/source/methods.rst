*********************
Functions and Methods
*********************

What follows is a description of the functions and methods that can be used
on the various modules and classes in *DColumn*.

Models and Managers
===================

DynamicColumnManager
--------------------
+--------------+-----------+--------------------------------------------------+
| Method Name  | Arguments | Description                                      |
+==============+===========+==================================================+
| get_fk_slugs | None      | Returns all dynamic column slugs that have a     |
|              |           | `value_type` of `CHOICE`. These include all      |
|              |           | Django models and the pseudo models.             |
+--------------+-----------+--------------------------------------------------+

DynamicColumn
-------------
+--------------------------+-----------+--------------------------------------+
| Method Name              | Arguments | Description                          |
+==========================+===========+======================================+
| relation_producer        | None      | Returns a string of the relation if  |
|                          |           | any for this instance. Used in the   |
|                          |           | admin.                               |
+--------------------------+-----------+--------------------------------------+
| collection_producer      | None      | Returns a list of the collection     |
|                          |           | names for this instance. Used in the |
|                          |           | admin.                               |
+--------------------------+-----------+--------------------------------------+
| get_choice_relation      | None      | Returns a tuple of the model object  |
| _object_and_field        |           | and the field used in the HTML select|
|                          |           | option.                              |
+--------------------------+-----------+--------------------------------------+

ColumnCollectionManager
-----------------------
+-----------------------+--------------+--------------------------------------+
| Method Name           | Arguments    | Description                          |
+=======================+==============+======================================+
| get_column_collection | `name`       | A positional argument. The name of   |
|                       |              | the column collection.               |
|                       +--------------+--------------------------------------+
|                       | `unassigned` | Keyword argument defaults to         |
|                       |              | `False`, if `True` gets the items    |
|                       |              | that are assigned to the collection  |
|                       |              | name plus any unassigned items.      |
|                       +--------------+--------------------------------------+
|                       |              | Returns a column collection.         |
+-----------------------+--------------+--------------------------------------+
| serialize_columns     | `name`       | A positional argument. The name of   |
|                       |              | the column collection.               |
|                       +--------------+--------------------------------------+
|                       | `obj`        | A keyword argument that defaults to  |
|                       |              | `None` otherwise an instance of a    |
|                       |              | ``CollectionBase`` inherited model.  |
|                       +--------------+--------------------------------------+
|                       | `by_slug`    | A keyword argument that defaults to  |
|                       |              | `False` causing keys to be a ``pk``  |
|                       |              | else `True` causing keys to be a     |
|                       |              | ``slug``.                            |
|                       +--------------+--------------------------------------+
|                       |              | Returns a serialized version of the  |
|                       |              | dynamic columns.                     |
+-----------------------+--------------+--------------------------------------+
| get_active_relation   | `name`       | A positional argument. The name of   |
| _items                |              | the column collection.               |
|                       +--------------+--------------------------------------+
|                       |              | Returns a list of dynamic columns    |
|                       |              | that have a `value_type` of          |
|                       |              | ``CHOICE``.                          |
+-----------------------+--------------+--------------------------------------+
| get_collection_choices| `name`       | A positional argument. The name of   |
|                       |              | the column collection.               |
|                       +--------------+--------------------------------------+
|                       | `use_pk`     | A keyword argument defaults to       |
|                       |              | `False`, if `True` returns the       |
|                       |              | ``pk`` instead of the slug as the    |
|                       |              | HTML select option value.            |
|                       +--------------+--------------------------------------+
|                       |              | Returns a list of tuples that can be |
|                       |              | used for HTML select options.        |
+-----------------------+--------------+--------------------------------------+

ColumnCollection
----------------
+-----------------------+--------------+--------------------------------------+
| Method Name           | Arguments    | Description                          |
+=======================+==============+======================================+
|process_dynamic_columns| `dcs`        | A list of ``DynamicColumn`` objects  |
|                       |              | which are inserted in the            |
|                       |              | ``dynamic_column`` ManyToMany object.|
|                       +--------------+--------------------------------------+
|                       |              | No return value.                     |
+-----------------------+--------------+--------------------------------------+

CollectionBaseManagerBase
-------------------------
+--------------------------+-----------+--------------------------------------+
| Method Name              | Arguments | Description                          |
+==========================+===========+======================================+
| model_objects            | `active`  | A keyword argument. This value if    |
|                          |           | ``True`` (default) only active       |
|                          |           | records will be returned else if     |
|                          |           | ``False`` all records will be        |
|                          |           | returned.                            |
|                          +-----------+--------------------------------------+
|                          |           | Returns a Django queryset.           |
+--------------------------+-----------+--------------------------------------+
| get_choices              | `field`   | A positional argument. This value    |
|                          |           | is the field in a model or pseudo    |
|                          |           | model that is used in the list of    |
|                          |           | choices.                             |
|                          +-----------+--------------------------------------+
|                          | `active`  | A keyword argument. This value if    |
|                          |           | ``True`` only active reords will be  |
|                          |           | returned else if ``False`` all       |
|                          |           | records will be returned.            |
|                          +-----------+--------------------------------------+
|                          | `comment` | A keyword argument. This value if    |
|                          |           | ``True`` causes the choice list to be|
|                          |           | prepended with a message.            |
|                          +-----------+--------------------------------------+
|                          |           | Returns a list of tuples that can be |
|                          |           | used for HTML select options.        |
+--------------------------+-----------+--------------------------------------+
| get_value_by_pk          | `pk`      | A positional argument. This value is |
|                          |           | the ``pk`` of a represents any       |
|                          |           | instance of a ``CollectionBase``     |
|                          |           | inherited model.                     |
|                          +-----------+--------------------------------------+
|                          | `field`   | A positional argument. This value is |
|                          |           | the field on a model or pseudo model |
|                          |           | that a value is returned from.       |
|                          +-----------+--------------------------------------+
|                          |           | Returns the value from the ``field`` |
|                          |           | on the object.                       |
+--------------------------+-----------+--------------------------------------+
| get_all_slugs            | None      | Returns a list of all slugs.         |
+--------------------------+-----------+--------------------------------------+
| get_all_fields           | None      | Returns a list of all model fields.  |
+--------------------------+-----------+--------------------------------------+
| get_all_fields_and_slugs | None      | Returns a list of all model fields   |
|                          |           | and slugs.                           |
+--------------------------+-----------+--------------------------------------+

CollectionBase
--------------
+----------------------+-----------+------------------------------------------+
| Method Name          | Arguments | Description                              |
+======================+===========+==========================================+
| serialize_key_values | `by_slug` | A keyword argument. This value if        |
|                      |           | ``False`` a dict of items are keyed by   |
|                      |           | the dynamic column's ``pk``, if ``True`` |
|                      |           | the dynamic column's ``slug`` is used.   |
|                      +-----------+------------------------------------------+
|                      |           | Returns a dictionary of ``KeyValue``     |
|                      |           | items.                                   |
+----------------------+-----------+------------------------------------------+
| get_dynamic_column   | `slug`    | A positional argument. This slug         |
|                      |           | represents any instance of a             |
|                      |           | ``CollectionBase`` inherited model.      |
|                      +-----------+------------------------------------------+
|                      |           | Returns the DynamicColumn instance       |
|                      |           | relitive to this model instance.         |
+----------------------+-----------+------------------------------------------+
| get_key_value        | `slug`    | A positional argument. This value        |
|                      |           | represents any ``DynamicColumn`` object. |
|                      +-----------+------------------------------------------+
|                      | `field`   | A keyword argument indicating the field  |
|                      |           | to use in a model or pseudo model.       |
|                      |           | Defaults to ``None``.                    |
|                      +-----------+------------------------------------------+
|                      |           | Returns the coersed value of a           |
|                      |           | ``KeyValue`` object.                     |
+----------------------+-----------+------------------------------------------+
| set_key_value        | `slug`    | A positional argument. This value        |
|                      |           | represents any ``DynamicColumn`` object. |
|                      +-----------+------------------------------------------+
|                      | `value`   | A positional argument. Can be the actual |
|                      |           | value to set in a ``KeyValue`` object, or|
|                      |           | a model that inherits ``CollectionBase`` |
|                      |           | or ``BaseChoice``.                       |
|                      +-----------+------------------------------------------+
|                      | `field`   | A keyword argument, indication the field |
|                      |           | used in a model or pseudo model. Defaults|
|                      |           | to ``None``.                             |
|                      +-----------+------------------------------------------+
|                      | `force`   | A keyword argument. The default is       |
|                      |           | ``False``, indicating that empty strings |
|                      |           | or ``None`` objects are not saved else   |
|                      |           | ``True`` causes empty strings only to be |
|                      |           | saved.                                   |
+----------------------+-----------+------------------------------------------+
|                      |           | No Return value. Sets a value on a       |
|                      |           | ``keyValue`` object.                     |
+----------------------+-----------+------------------------------------------+

KeyValueManager
---------------
There are no user methods on the `KeyValueManager` model manager at this time.

KeyValue
--------
There are no user methods on the `KeyValue` model at this time.

DynamicColumnManager
====================
This is not the model manager mentioned above. The `DynamicColumnManager` holds
all the relevant states of the system and should be the first place you come
when you need to know something about the system.

+--------------------------+------------------+-------------------------------+
| Method Name              | Arguments        | Description                   |
+==========================+==================+===============================+
| register_choice          | `choice`         | A positional argument. This   |
|                          |                  | can be either a Django model  |
|                          |                  | or pseudo model class object. |
|                          +------------------+-------------------------------+
|                          | `relation_num`   | A positional argument. This   |
|                          |                  | value is a numeric identifier |
|                          |                  | used as the HTML select option|
|                          |                  | value.                        |
|                          +------------------+-------------------------------+
|                          | `field`          | A positional argument. This   |
|                          |                  | value is a string used as the |
|                          |                  | HTML select option text value.|
|                          +------------------+-------------------------------+
|                          |                  | No return value.              |
+--------------------------+------------------+-------------------------------+
| choice_relations         | Property         | Returns a list of choices.    |
+--------------------------+------------------+-------------------------------+
| choice_relation_map      | Property         | Returns a dictionary of       |
|                          |                  | choices.                      |
+--------------------------+------------------+-------------------------------+
| choice_map               | Property         | Returns a dictionary where the|
|                          |                  | key is the Django or pseudo   |
|                          |                  | model name and the value is a |
|                          |                  | tuple of the choice model     |
|                          |                  | object and the relevant field |
|                          |                  | name.                         |
+--------------------------+------------------+-------------------------------+
| register_css_containers  | `container_list` | A positional argument and is a|
|                          |                  | list of the CSS classes or ids|
|                          |                  | that will determine the       |
|                          |                  | location on the page of the   |
|                          |                  | various dynamic columns.      |
|                          +------------------+-------------------------------+
|                          |                  | No returns value.             |
+--------------------------+------------------+-------------------------------+
| css_containers           | Property         | Returns a list of tuples where|
|                          |                  | the tuple is (num, text).     |
+--------------------------+------------------+-------------------------------+
| css_container_map        | Property         | Returns a dictionary of the   |
|                          |                  | CSS containers.               |
+--------------------------+------------------+-------------------------------+
| get_collection_name      | `model_name`     | A positional argument. The    |
|                          |                  | name of the column collection.|
|                          +------------------+-------------------------------+
|                          |                  | Returns the                   |
|                          |                  | ``ColumnCollection`` instance |
|                          |                  | name.                         |
+--------------------------+------------------+-------------------------------+
| get_api_auth_state       | Property         | Returns the value of          |
|                          |                  | ``DYNAMIC_COLUMNS``           |
|                          |                  | ``.INACTIVATE_API_AUTH``      |
+--------------------------+------------------+-------------------------------+
| get_relation_model_field | `relation`       | A positional argument and is  |
|                          |                  | the value in the              |
|                          |                  | ``DynamicColumn`` relation    |
|                          |                  | field.                        |
|                          +------------------+-------------------------------+
|                          |                  | Returns the field used in the |
|                          |                  | HTML select option text value.|
+--------------------------+------------------+-------------------------------+

Template Tags
=============
There are three template tags that can be used. These tags will help with
displaying the proper type of fields in your templates.

auto_display
------------
The `auto_display` tag displays the dynamic columns in your template as either
form elements or `span` elements. This tag takes one positional argument and
three keyword arguments. Please look at the example code on
:example-html:`GitHub <books/book_create_view.html>` for usage.

 1. relation `dict`

     A dictionary representing the meta data for a specific field. This data
     is a single value dict that can be found in the context as `relations`.

 2. prefix `str`

     Defaults to an empty string, but can be used to put a common prefix on all
     tag `id` and `name` attributes. Not often used.

 3. option `(list, tuple)` or `dict`

     Used only for Django model or pseudo model type fields, but can be passed
     into the template tag for all types and will be ignored if not needed. The
     entire ``dynamicColumns`` `dict` from the context can be passed in or just
     the specific field's data `list` or `tuple`.

 4. display `bool`

     This keyword argument is either `True` or `False`. `False` is the default
     and generates `input` or `select` tags for form data. If `True`  `span`
     tags are generated for detail pages where no forms would generally be
     used.

single_display
--------------
The `single_display` tag displays a single slug based on a ``CollectionBase``
derived model. This tag could often be used in list templates. Please look at
the example code on :example-html:`GitHub <books/book_list_view.html>` for
usage.

 1. obj `model instance`

     A model instance that is derived from ``CollectionBase``.

 2. slug `str`

     The `slug` from a DynamicColumn record.

 3. as `str`

     A manditory delimiter keyword used to define the next argument.

 4. name `str`

     The variable name created in the context that will hold the value of the
     slug. ex. If the slug is ``first-name`` the context variable could be
     ``first_name``.

combine_contexts
----------------
The `combine_contexts` tag combines two context variables. This would often be
used to get the template error from a form for a specific slug. ex. The
combination of `form.error` and `relation.slug` would give you the error for a
form `input` element. Please look at the example code on
:example-html:`GitHub <books/book_create_view.html>` for usage.

 1. obj `instance object`

     Any instance object that has member objects.

 2. variable `member object`

     Reference to any member object on the `obj`.
