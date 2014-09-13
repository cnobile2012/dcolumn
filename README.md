Django Tool to Create Dynamic Fields
====================================

This app would be used when designing your models. Any fields that need to be
indexed or are part of a primary key would be created normally in your model.
You can find example code at: https://github.com/cnobile2012/dcolumn

Basic Installation
------------------

 1. Add 'dcolumn' to your INSTALLED_APPS settings:

        INSTALLED_APPS = (
            ...
            'dcolumn.dcolumns',
            )

 2. Add the following code stanza to the settings file. The `COLLECTIONS` key
    points to key value pairs where the key is the model name and the value
    is a unique name given to a collection set. This collection set is kept
    in the model named `ColumnCollection`. As of now there is only a single
    asynchronous call to the internal API. It is by default only accessed by
    logged in users. You can change this behavior by setting
    `INACTIVATE_API_AUTH` to `True`.

        DYNAMIC_COLUMNS = {
            # The default key/value pairs for the ColumnCollection object to use
            # for all tables that use dcolumn. The key is the table name and the
            # value is the name used in the ColumnCollection record.
            u'COLLECTIONS': {
                u'Book': u'Book Current',
                u'Author': u'Author Current',
                u'Publisher': u'Publisher Current',
                },
            # To allow anybody to access the API set to True.
            u'INACTIVATE_API_AUTH': False,
            }

 3. If you want authorization on the API you will need to set the standard
    Django setting 'LOGIN_URL' to something reasonable.

        # Change the URL below to your login path.
        LOGIN_URL = u"/admin/"

 4. There are two ways to define page location of each new field that you
    enter into the system. The 1st way is to just pass a tuple of each CSS
    class. They are enumerated starting with 0 (zero). They would be
    referenced as `css.0`, `css.1`, etc. The 2nd way is to pass a tuple of
    tuples with the first variable as the key and the second variable as the
    value. They would be reference as `css.top`, `css.center`, etc.

        dcolumn_manager.register_css_containers(
               (u'top-container', u'center-container', u'bottom-container')
        )

        dcolumn_manager.register_css_containers(
               ((u'top', u'top-container'),
                (u'center', u'center-container'),
                (u'bottom', u'bottom-container'))
        )

 5. The models need to subclass the `CollectionBase` model base class from
    dcolumn. The model manager needs to subclass `StatusModelManagerMixin` and
    also needs to implement a method named `dynamic_column`. See the example
    code.

 6. The `CollectionBaseManagerBase` manager base class from dcolumn should also
    be sub-classed to pick up a few convenience methods. This is not mandatory.

 7. Any forms used with a dynamic column model will need to subclass
    `CollectionFormMixin`. You do not need to subclass `forms.ModelForm`, this
    is done for you already by `CollectionFormMixin`.

 8. Any views need to subclass `CollectionCreateUpdateViewMixin` which must be
    before the class-based view that you will use. Once again see the example
    code.

Functional Details
------------------



Do Not's
--------
Once you have registered the choices/models with `dcolumn_manager.register_choice()` do not change it, as the numeric value is stored in the `DynamicColumn` table. So obviously if you really really really need to change it you can, but you must manually modify the `Relation` in all the affected rows in the `DynamicColumn` table.

You will see that this is all rather simple and you'll need to write very little code to support DynamicColumns.

It is also not advisable to hardcode any of the slugs created when a dynamic column is created as these slugs can change if the display name changes in the record.

API Details
-----------

### Models and Managers

#### DynamicColumnManager
 1. get_fk_slugs
   * Takes no arguments
   * Returns all dynamic column slugs that have a `value_type` of `CHOICE`.
     These include all Django models and the Choice models.

#### DynamicColumn
There are no user methods on the `DynamicColumn` model at this time.

#### ColumnCollectionManager
 1. get_column_collection
   * `name` positional argument and is a collection name as defined in the
     DYNAMIC_COLUMNS.COLLECTIONS dictionary.
   * `unassigned` keyword argument defaults to `False`, if `True` gets the
     items that are assigned to the collection name plus any unassigned items.
   * Returns a column collection.
 2. serialize_columns
   * `name` positional argument and is a collection name as defined in the
     DYNAMIC_COLUMNS.COLLECTIONS dictionary.
   * `obj` keyword argument defaults to `None` otherwise an instance of a
     dynamic column enabled model.
   * Returns a serialized version of the dynamic columns.
 3. get_active_relation_items
   * `name` positional argument and is a collection name as defined in the
     DYNAMIC_COLUMNS.COLLECTIONS dictionary.
   * Returns a list of dynamic columns that have a `value_type` of CHOICE.
 4. get_collection_choices
   * `name` positional argument and is a collection name as defined in the
     DYNAMIC_COLUMNS.COLLECTIONS dictionary.
   * `use_pk` keyword argument defaults to `False`, if `True` returns the pk
     instead of the slug as the HTML select option value.
   * Returns a list of tuples that can be used for HTML select options.

#### ColumnCollection
There are no user methods on the `ColumnCollection` model at this time.

#### CollectionBaseManagerBase
 1. get_all_slugs
   * Takes no arguments
   * Returns a list of all slugs

 2. get_all_fields
   * Takes no arguments
   * Returns a list of all model fields.

 3. get_all_fields_and_slugs
   * Takes no arguments
   * Returns a list of all model fields and slugs.

#### CollectionBase
 1. serialize_key_value_pairs
   * Takes no arguments
   * Returns a dictionary where the key is the pk of a dynamic column and the
     value is the value of the keyvalue pair.
 2. set_key_value_pair
   * `slug` positional argument and is the slug of any dynamic column object.
   * `value` positional argument and is a value to be set on a keyvalue pair.
   * Returns nothing. Sets a value on a keyvalue pair object.

#### KeyValueManager
There are no user methods on the `KeyValueManager` manager at this time.

#### KeyValue
There are no user methods on the `KeyValue` model at this time.

### DynamicColumnManager



Feel free to contact me at: carl dot nobile at gmail.com
