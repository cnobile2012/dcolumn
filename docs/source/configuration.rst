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
