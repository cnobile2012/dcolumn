********
Overview
********

Django Support
--------------
At the time of this writing DColumn supports Django 3.x and probably back
to 2.0. The biggest issue with supporting older versions of Django is with
the new way urlpatterns is used. However, **Django DColumns** presupposes that
you are building an application from scratch, so you should use the latest
versions of Django and Python also.

Python Support
--------------
Python 3.5 and 3.6 are supported.

What is Django DColumn?
-----------------------
*DColumn* is a Django plugin that lets the developer add columns to a model
dynamically. In other words through the admin. It does this in the same way
that the admin uses an inline model. Matter-of-fact that is exactly how the
additional columns are displayed in the admin. The only addition is some
special JavaScript that converts the column type to the type you have
previously set it to.

How it Works
------------
Creating new columns can be done, because any type of field can be represented
as a string. There are two methods defined on any model that is a *DColumn*
model that will do conversion in and out of the data type you have set.

Recursion
---------
If you define a model as a *DColumn* model it can be included as a field in
another model that is also defined as a *DColumn* model.

.. warning::

   As of Version 2.0 **Django DColumns** is no longer backwards compatible
   with previous versions. It now needs to use fields defined in user forms.
   The more recent releases of Django would not work with the old way Dcolumns
   had previously handled fields. The current implementation is actually
   better as it is now more consistent with how Django does things.
