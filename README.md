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

 2. Add the following code stanza to the settings file. The 'COLLECTIONS' key
    points to key value pairs where the key is the model name and the value
    is a unique name given to a collection set. This collection set is kept
    in the model named 'ColumnCollection'. As of now there is only a single
    asynchronous call to the internal API. It is by default only accessed by
    logged in users. You can change this behavior by setting
    'INACTIVATE_API_AUTH' to 'True'.

    # DCOLUMN config
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

    a. dcolumn_manager.register_css_containers(
           (u'top-container', u'center-container', u'bottom-container'))

    b. dcolumn_manager.register_css_containers(
           ((u'top', u'top-container'),
            (u'center', u'center-container'),
            (u'bottom', u'bottom-container')))

 5. The models need to subclass the `CollectionBase` object from dcolumn. The
    model manager needs to subclass `StatusModelManagerMixin` and also needs
    to impliment a method named `dynamic_column`. See the example code 

 6. Any forms used with a dynamic column model will need to subclass
    `CollectionFormMixin`. You do not need to subclass `forms.ModelForm`, this
    is done for you already by `CollectionFormMixin`.

 7. Any views need to subclass `CollectionCreateUpdateViewMixin` which must be
    before the class-based view that you will use. Once again see the example
    code.

You will see that this is all rather simple and you'll need to write very
little code to support DynamicColumns.

Feel free to contact me at: carl.nobile@gmail.com
