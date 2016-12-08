*************
Configuration
*************

IMPORT dcolumn_manager
======================
At the top of your settings import ``dcolumn_manager``.

.. code::

    from dcolumn.dcolumns.manager import dcolumn_manager



INSTALLED_APPS
==============
Add ``dcolumn`` to your INSTALLED_APPS settings:

.. code::

    INSTALLED_APPS = (
        ...
        'dcolumn.dcolumns',
        )

LOGIN_URL
=========
If you want authorization on the API you will need to set the standard Django
setting ``LOGIN_URL`` to something reasonable.


.. code::

    # Change the URL below to your login path.
    LOGIN_URL = "/admin/"

DColumns Config
===============
To define page location for each field that you enter into the ``DynamicColumn``
table pass a tuple of tuples with the first variable as the key and the second
variable as the value. They would be referenced in your templates as CSS
classes ``{{css.top}}``, ``{{css.center}}``, etc. You can add as many of
these as you wish. The first object of the tuple becomes a variable so these
names must conform to standard Python variable characters.
See :example-html:`GitHub <books/book_create_view.html>` for an example of
template usage.

.. code::

    dcolumn_manager.register_css_containers(
           (('top', 'top-container'),
            ('center', 'center-container'),
            ('bottom', 'bottom-container')
            ))

The following stanza when put in the settings file will enable customization to
`DColumns`. As of now there is only a single variable used and it defines an API
call. By default only logged in users can assess this call. You can change this
behavior by setting ``INACTIVATE_API_AUTH`` to ``True``. This stanza in the
settings is optional at this time.

.. code::

    DYNAMIC_COLUMNS = {
        # To allow anybody to access the API set to True.
        'INACTIVATE_API_AUTH': False,
        }

Setting the URLs
================
The master ``urls.py`` file needs to have added the following line for the
admin to work properly::

    urlpatterns = [
        ...,
	url(r'^dcolumns/', include('dcolumn.dcolumns.urls')),
        ...,
	]
