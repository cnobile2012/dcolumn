********
Overview
********

Django Support
--------------
At the time of this writing DColumn supports Django 1.9.10 and probably back
to 1.8.0. The biggest issue with supporting older versions of Django is with
the new way urlpatterns is used.

Python Support
--------------
Python 2.7, 3.4, 3.5 and 3.5-dev are supported.

What is Django DColumn?
-----------------------
*DColumn* is a Django plugin that lets the developer add columns to a model
dynamically. It does this in the same way that the admin uses an inline model.
Matter-of-fact that is exactly how the additional columns are displayed in
the admin. The only addition is some special JavaScript that converts the column
type to the type you have previously set it to.

How it Works
------------
Creating new columns can be done, because any type of field can be represented
as a string. There are two methods defined on any model that is a *DColumn*
model that will do conversion in and out of the data type you have set.

Recursion
---------
If you define a model as a *DColumn* model it can be included as a field in
another model defined as a *DColumn* model.

.. warning::

   Version 1.0 of *DColumn* is a complete rewrite and is **NOT** backwards
   compatible with previous versions.