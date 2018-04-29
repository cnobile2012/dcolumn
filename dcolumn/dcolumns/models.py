# -*- coding: utf-8 -*-
#
# dcolumn/dcolumns/models.py
#
from __future__ import unicode_literals

"""
Dynamic Column dependent models.
"""
__docformat__ = "restructuredtext en"

import logging
import datetime
from dateutil import parser
from collections import OrderedDict

from django.db import models
from django.utils import six
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from dcolumn.common import create_field_name
from dcolumn.common.choice_mixins import BaseChoice
from dcolumn.common.model_mixins import (
    UserModelMixin, TimeModelMixin, StatusModelMixin, StatusModelManagerMixin,
    ValidateOnSaveMixin)

from .manager import dcolumn_manager

log = logging.getLogger('dcolumns.dcolumns.models')


#
# DynamicColumn
#
class DynamicColumnManager(StatusModelManagerMixin):
    """
    Supplies methods to the DynamicColumn objects instance.
    """

    def get_fk_slugs(self):
        """
        This method returns a dict of the relation model foreign key name
        and slug.

        :rtype: A dict of ``{<relation class name>: <slug>, ...}``.
        """
        result = {}

        for record in self.active():
            if record.value_type == self.model.CHOICE:
                name = dcolumn_manager.choice_relation_map.get(record.relation)
                result[name] = record.slug

        return result


@python_2_unicode_compatible
class DynamicColumn(TimeModelMixin, UserModelMixin, StatusModelMixin,
                    ValidateOnSaveMixin):
    """
    This model defines all the fields used in models that implement dynamic
    columns.
    """
    BOOLEAN = 1
    CHOICE = 2
    DATE = 3
    DATETIME = 4
    FLOAT = 5
    NUMBER = 6
    TEXT = 7
    TEXT_BLOCK = 8
    TIME = 9
    VALUE_TYPES = (
        (BOOLEAN, _("Boolean")),
        (CHOICE, _("Choice")),
        (DATE, _("Date")),
        (DATETIME, _("Date Time")),
        (FLOAT, _("Floating Point")),
        (NUMBER, _("Number")),
        (TEXT, _("Text")),
        (TEXT_BLOCK, _("Text Block")),
        (TIME, _("Time")),
        )
    VALUE_TYPES_MAP = dict(VALUE_TYPES)
    NO = False
    YES = True
    YES_NO = (
        (NO, _("No")),
        (YES, _("Yes"))
        )

    name = models.CharField(
        verbose_name=_("Name"), max_length=50,
        help_text=_("Enter a column name."))
    preferred_slug = models.SlugField(
        verbose_name=_("Preferred Slug"), null=True, blank=True,
        help_text=_("If you don't want the slug to change when the name "
                    "changes enter a slug here. However, if you change this "
                    "field the slug will track it."))
    slug = models.SlugField(
        verbose_name=_("Slug"), editable=False,
        help_text=_("This field is normally created from the name field, "
                    "however, if you want to prevent it from changing when "
                    "the name changes enter a preferred slug above."))
    value_type = models.IntegerField(
        verbose_name=_("Value Type"), choices=VALUE_TYPES,
        help_text=_("Choose the value type."))
    relation = models.IntegerField(
        verbose_name=_("Choice Relation"), null=True, blank=True,
        help_text=_("Choose the Choice Relation Type."))
    required = models.BooleanField(
        verbose_name=_("Required Field"), choices=YES_NO, default=NO,
        help_text=_("If this field is required based on business rules then "
                    "choose 'Yes'."))
    store_relation = models.BooleanField(
        verbose_name=_("Store Relation Value"), choices=YES_NO, default=NO,
        help_text=_("Store the literal value not the primary key of the "
                    "relation (used when choices change often). The most "
                    "common usage is the default 'No', to not store."))
    location = models.CharField(
        verbose_name=_("Display Location"), max_length=50,
        help_text=_("Choose a display location."))
    order = models.PositiveSmallIntegerField(verbose_name='Display Order')

    objects = DynamicColumnManager()

    def relation_producer(self):
        """
        Produces a ``CHOICE`` relation that is used in the Django admin.

        :rtype: The ``CHOICE`` relation or empty string.
        """
        result = ''

        if self.relation is not None:
            result = dcolumn_manager.choice_relation_map.get(self.relation, '')

        return result
    relation_producer.short_description = _("Relation")

    def collection_producer(self):
        """
        Produces a ``Collection`` name that is used in the Django admin.

        :rtype: A comma separated list of ``Collection`` names.
        """
        collections = [format_html('<span>{}</span>', c.name)
                       for c in self.column_collection.all()]
        return format_html_join(
            mark_safe('<br/>'), '{}', ((c,) for c in collections))
    collection_producer.short_description = _("Collections")

    def clean(self):
        """
        Validate the proper operation between the slug and preferred_slug
        fields and the relation and value_type fields.
        """
        # If we have a preferred_slug set the slug with it.
        if self.preferred_slug:
            self.preferred_slug = create_field_name(self.preferred_slug)
            self.slug = self.preferred_slug
        else:
            self.slug = create_field_name(self.name)

        # Test that if the value_type is set to CHOICE that the relation
        # is also set.
        if ((self.value_type == self.CHOICE and not self.relation) or
            (self.relation and self.value_type != self.CHOICE)):
            msg = _("Must choose CHOICE type and relation.")
            log.warning(msg)
            raise ValidationError({'relation': [msg]})

    def save(self, *args, **kwargs):
        """
        Be sure the complete MRO has their saves called.
        """
        super(DynamicColumn, self).save(*args, **kwargs)

    def __str__(self):
        return "{} ({})".format(
            self.name, dcolumn_manager.css_container_map.get(
                self.location, ''))

    class Meta:
        ordering = ('location', 'order', 'name',)
        verbose_name = _("Dynamic Column")
        verbose_name_plural = _("Dynamic Columns")

    def get_choice_relation_object_and_field(self):
        """
        Gets the model class object and the field passed in when
        ``dcolumn_manager.register_choice`` was configured. If this
        ``DynamicColumn`` was not used for a choice model then a tuple of
        two Nones are returned.

        Example of Output::

          (example_site.books.models.Promotion, 'name')

          or

          (None, None)

        :rtype: tuple
        """
        return dcolumn_manager.get_relation_model_field(self.relation)


#
# ColumnCollection
#
class ColumnCollectionManager(StatusModelManagerMixin):
    """
    Manager for the ``ColumnCollection`` model.
    """

    def get_column_collection(self, name, unassigned=False):
        """
        Get the query set for the named collection. If unassigned is True
        add the unassigned dynamic columns to the query set.

        :param name: Name of the column collection.
        :type name: str
        :param unassigned: Also get items that are not assigned to a column
                           collection yet.
        :type unassigned: bool
        :rtype: A queryset of objects that inherit ``CollectionBase``.
        :raises ColumnCollection.DoesNotExist: If the collection name is not
                                               found and unassigned is False.
        """
        log.debug("Collection name: %s, unassigned: %s", name, unassigned)
        queryset = self.none()

        try:
            queryset = self.active().get(
                related_model__iexact=name).dynamic_column.active()
        except self.model.DoesNotExist as e:
            if not unassigned:
                raise e

        if unassigned:
            queryset |= DynamicColumn.objects.active().filter(
                column_collection=None)

        return queryset

    def serialize_columns(self, name, obj=None, by_slug=False):
        """
        Serialize the ``DynamicColumn`` for the ``name`` of this collection
        in an OrderedDict. When a model that inherits ``CollectionBase`` is
        passed in as ``obj`` its set of ``KeyValue`` objects value are also
        included. OrderedDict items can be keyed by either a `pk` or `slug`.

        :param name: Name of the collection.
        :type name: str
        :param obj: Optional model object that inherits from
                    ``CollectionBase``.
        :type obj: object
        :param by_slug: If False the OrderedDict items are keyed by the
                        dynamic column's ``pk``, if True the dynamic
                        column's ``slug`` is used.
        :type by_slug: bool
        :rtype: An OrderedDict of serialized ``KeyValue`` values and their
                ``DynamicColumn`` meta data.
        """
        records = self.get_column_collection(name)
        result = OrderedDict()

        if obj:
            key_value_map = obj.serialize_key_values()

        if by_slug:
            key = 'slug'
        else:
            key = 'pk'

        for record in records:
            rec = result.setdefault(getattr(record, key), {})
            rec['pk'] = record.pk
            rec['name'] = record.name
            rec['slug'] = record.slug
            rec['value_type'] = record.value_type

            if record.relation:
                rec['relation'] = record.relation
                rec['store_relation'] = record.store_relation

            rec['required'] = record.required
            location = record.location
            # We convert the list to a dict because css_container_map may
            # not be keyed with integers.
            rec['location'] = dict(dcolumn_manager.css_containers).get(
                location, '')
            rec['order'] = record.order
            if obj: rec['value'] = key_value_map.get(record.pk, '')

        return result

    def get_active_relation_items(self, name):
        """
        Get a list of all active relation type choice items. The list is
        made up of the names of each item.

        :param name: Name of the ``ColumnCollection``.
        :type name: str
        :rtype: A ``list`` of all ``CHOICE`` items including both model and
                choice items.
        """
        records = self.get_column_collection(name)
        return [dcolumn_manager.choice_relation_map.get(record.relation)
                for record in records if record.relation]

    def get_collection_choices(self, name, use_pk=False):
        """
        Returns a set of choices for a list of options on an HTML select
        tag. Normally the slug is returned as the option value, however if
        `use_pk` is `True` then the value attribute will get the pk of the
        record.

        :param name: Name of the ``ColumnCollection``.
        :type name: str
        :param use_pk: If ``False`` (default) slugs are used else if
                       ``True`` PKs are used.
        :type use_pk: bool
        :rtype: A list of tuples. ``[(<slug or pk>, <KeyValue name>), ...]``
        """
        records = self.get_column_collection(name)
        choices = [(use_pk and r.pk or r.slug, r.name) for r in records]
        return choices


@python_2_unicode_compatible
class ColumnCollection(TimeModelMixin, UserModelMixin, StatusModelMixin,
                       ValidateOnSaveMixin):
    """
    This model defines the collection of ``DynamicColumn`` objects in this
    set.
    """

    name = models.CharField(
        verbose_name=_("Name"), unique=True, max_length=50,
        help_text=_("Enter a unique name for this record."))
    dynamic_column = models.ManyToManyField(
        DynamicColumn, verbose_name=_("Dynamic Columns"),
        related_name='column_collection')
    related_model = models.CharField(
        verbose_name=_("Related Model"), unique=True, max_length=50,
        help_text=_("Choose the related model."))

    objects = ColumnCollectionManager()

    def save(self, *args, **kwargs):
        """
        Be sure the complete MRO has their saves called.
        """
        super(ColumnCollection, self).save(*args, **kwargs)

    def __str__(self):
        return "{}-{}".format(self.name, self.related_model)

    class Meta:
        ordering = ('name',)
        verbose_name = _("Column Collection")
        verbose_name_plural = _("Column Collections")

    def process_dynamic_columns(self, dcs):
        """
        This method adds or removes ``DynamicColumn`` objects to the
        collection.

        :param dcs: A list of ``DynamicColumn`` objects.
        """
        if dcs:
            new_pks = [inst.pk for inst in dcs]
            old_pks = [inst.pk for inst in self.dynamic_column.all()]
            rem_pks = list(set(old_pks) - set(new_pks))
            # Remove unwanted dynamic_columns.
            self.dynamic_column.remove(
                *self.dynamic_column.filter(pk__in=rem_pks))
            # Add new dynamic_columns.
            add_pks = list(set(new_pks) - set(old_pks))
            new_dcs = DynamicColumn.objects.filter(pk__in=add_pks)
            self.dynamic_column.add(*new_dcs)


#
# CollectionBase
#
class CollectionBaseManager(models.Manager):
    """
    The manager class for any model that inherits ``CollectionBase``.
    """

    def model_objects(self, active=True):
        """
        Returns a list of all objects on this model.

        :param active: If ``True`` (default) only active records will be
                       returned else if ``False`` all records will be
                       returned.
        :type active: bool
        :rtype: Django queryset.
        """
        if hasattr(self, 'active'):
            result = self.active(active=active)
        else: # pragma: no cover
            # If overridden and active method was not defined.
            result = self.all()

        return result

    def get_choices(self, field, active=True, comment=True, sort=True):
        """
        Returns choices that can be used in HTML select options.

        :param field: The field of the choice that is used to populate the
                      list.
        :type field: str
        :param active: If ``True`` only active records will be returned
                       else if ``False`` all records will be returned.
        :type active: bool
        :param comment: Defaults to ``True`` prepending a choice header to
                        the list.
        :type comment: bool
        :param sort: Defaults to ``True`` sorting results, a ``False`` will
                     turn off sorting, however, if the model sorts this may
                     have no effect.
        :type sort: bool
        :rtype: A list of tuples suitable for use in HTML select option
                tags.
        """
        choices = [(obj.pk, getattr(obj, field))
                   for obj in self.model_objects(active=active)]

        if sort:
            choices.sort(key=lambda x: x[1])

        if comment:
            choices.insert(
                0, (0, _("Please choose a {}").format(self.model.__name__)))

        return choices

    def get_value_by_pk(self, pk, field):
        """
        Returns the value from 'field' using the pk as the key.

        :param pk: The key of the object.
        :type pk: int or str
        :param field: The field of the choice the value is taken from.
        :type field: str
        :rtype: Value from the ``field`` on the object.
        :raises CollectionBase.DoesNotExist: If the `Dcolumn` model object was
                                             not found.
        """
        value = ''

        if int(pk) != 0:
            try:
                obj = self.get(pk=pk)
            except self.model.DoesNotExist as e:
                msg = _("Access to PK %s failed, %s")
                log.error(msg, pk, e)
                raise e
            else:
                try:
                    value = getattr(obj, field)
                except (AttributeError, TypeError) as e:
                    msg = _("The field value '%s' is not on object '%s'")
                    log.error(msg, field, obj)
                    raise e

        return value

    def get_all_slugs(self):
        """
        Returns all ``DynamicColumn`` slug names relative to this model.

        :rtype: List of slugs.
        """
        result = []
        obj = self.select_related('column_collection').first()

        if obj:
            kvs = obj.column_collection.dynamic_column.values_list(
                'slug', flat=True).order_by('slug')
            result[:] = list(kvs)

        return result

    def get_all_fields(self):
        """
        Returns all model field names.

        :rtype: List of fields.
        """
        return [field.name for field in self.model._meta.get_fields()
                if 'collection' not in field.name and
                field.name != 'keyvalues']

    def get_all_fields_and_slugs(self):
        """
        Returns all field names and the ``DynamicColumn`` slugs in a sorted
        list.

        :rtype: List of all field and slugs.
        """
        result = self.get_all_slugs() + self.get_all_fields()
        result.sort()
        return result


class CollectionBase(TimeModelMixin, UserModelMixin, StatusModelMixin):
    YES = _("yes")
    NO = _("no")
    YES_NO = (YES, NO, "yes", "no")
    TRUE = _("true")
    FALSE = _("false")
    TRUE_FALSE = (TRUE, FALSE, "true", "false")

    column_collection = models.ForeignKey(
        ColumnCollection, on_delete=models.CASCADE,
        verbose_name=_("Column Collection"),
        help_text=_("Choose the version of the dynamic columns you want "
                    "for all Collections."))

    def __init__(self, *args, **kwargs):
        super(CollectionBase, self).__init__(*args, **kwargs)
        self.__save_deferred = []

    def save(self, *args, **kwargs):
        """
        Be sure the complete MRO has their saves called.
        """
        super(CollectionBase, self).save(*args, **kwargs)

    def serialize_key_values(self, by_slug=False):
        """
        Returns a dict of the ``DynamicColumn`` PK and the ``KeyValue``
        value.

        :param by_slug: If False a dict of items are keyed by the dynamic
                        column's ``pk``, if True the dynamic column's
                        ``slug`` is used.
        :type by_slug: bool
        :rtype: Dict
        """
        result = {}

        if by_slug:
            field = 'slug'
        else:
            field = 'pk'

        return {
            getattr(kv.dynamic_column, field):
            self.get_key_value(kv.dynamic_column.slug, choice_raw=True)
            for kv in self.keyvalues.select_related('dynamic_column').all()
            }

    def get_dynamic_column(self, slug):
        """
        Gets the ``DynamicColumn`` instance given the slug.

        :param slug: The ``DynamicColumn`` slug value.
        :type slug: str
        :rtype: ``DynamicColumn`` model instance.
        :raises DynamicColumn.DoesNotExist: If the `DynamicColumn` model
                                            object was not found.
        :raises KeyValue.DoesNotExist: If the `KeyValue` model object was not
                                       found.
        """
        try:
            dc = self.column_collection.dynamic_column.get(slug=slug)
        except DynamicColumn.DoesNotExist as e:
            log.error("DynamicColumn with slug '%s' does not exist.", slug)
            # Cannot get a dynamic column if not in a collection.
            dc = None

        return dc

    def get_key_value(self, slug, field=None, choice_raw=False):
        """
        Return the ``KeyValue`` object value for the ``DynamicColumn`` slug.

        :param slug: The ``DynamicColumn`` slug.
        :type slug: str
        :param field: Only used with CHOICE objects. Defaults to the field
                      passed to the dcolumn_manager.register_choice(choice,
                      relation_num, field) during configuration. The
                      'field' argument allows the return of a different
                      field on the CHOICE objects, but must be a valid
                      member object on the model.
        :type field: str or None
        :param choice_raw: Only works with ``dc.CHOICE`` type. A ``False``
                           indicates normal operation, whereas a ``True``
                           will return the `pk`.
        :type choice_raw: bool
        :rtype: String value from a ``KeyValue`` object.
        :raises ValueError: Invalid combination of parameters.
        :raises AttributeError: If a bad field is passed in.
        :raises TypeError: If wrong type is passed in.
        """
        try:
            obj = self.keyvalues.select_related(
                'dynamic_column').get(dynamic_column__slug=slug)
        except self.keyvalues.model.DoesNotExist:
            log.error("Could not find value for slug '%s'.", slug)
            value = ''
        else:
            dc = obj.dynamic_column

            if dc.value_type == dc.CHOICE and obj.value:
                value = self._is_get_choice(dc, obj.value, field, choice_raw)
            elif dc.value_type == dc.TIME and obj.value:
                value = self._is_get_time(dc, obj.value)
            elif dc.value_type == dc.DATE and obj.value:
                value = self._is_get_date(dc, obj.value)
            elif dc.value_type == dc.DATETIME and obj.value:
                value = self._is_get_datetime(dc, obj.value)
            elif dc.value_type == dc.BOOLEAN and obj.value:
                value = self._is_get_boolean(dc, obj.value)
            elif dc.value_type == dc.NUMBER and obj.value:
                value = self._is_get_number(dc, obj.value)
            elif dc.value_type == dc.FLOAT and obj.value:
                value = self._is_get_float(dc, obj.value)
            elif dc.value_type in (dc.TEXT, dc.TEXT_BLOCK) and obj.value:
                value = obj.value
            else: # pragma: no cover
                # This should never happen. An invalid value_type will
                # raise a ValidationError when the DynamicColumn is
                # created.
                value = obj.value

        return value

    def _is_get_choice(self, dc, value, field, choice_raw):
        if dc.store_relation or choice_raw:
            result = int(value) if value.isdigit() else value
        else:
            model, m_field = dc.get_choice_relation_object_and_field()

            if not field:
                field = m_field

            if model and field: # value should be a pk--str(pk)
                result = model.objects.get_value_by_pk(value, field)
            else: # pragma: no cover
                self._raise_exception(dc, value, field=field)

        return result

    def _is_get_time(self, dc, value):
        dt = self._is_get_datetime(dc, value)
        return datetime.time(
            hour=dt.hour, minute=dt.minute, second=dt.second,
            microsecond=dt.microsecond, tzinfo=dt.tzinfo)

    def _is_get_date(self, dc, value):
        dt = self._is_get_datetime(dc, value)
        return datetime.date(year=dt.year, month=dt.month, day=dt.day)

    def _is_get_datetime(self, dc, value):
        try:
            return parser.parse(value)
        except ValueError:
            self._raise_exception(dc, value)

    def _is_get_boolean(self, dc, value):
        if value.isdigit():
            result = 0 if int(value) == 0 else 1
        elif value.lower() in self.TRUE_FALSE:
            result = value.lower() in (self.TRUE, 'true')
        elif value.lower() in self.YES_NO:
            result = value.lower() in (self.YES, 'yes')
        else:
            self._raise_exception(dc, value)

        return result

    def _is_get_number(self, dc, value):
        if value.isdigit():
            result = int(value)
        else:
            self._raise_exception(dc, value)

        return result

    def _is_get_float(self, dc, value):
        if value.replace('.', '').isdigit():
            result = float(value)
        else:
            self._raise_exception(dc, value)

        return result

    def save_deferred(self):
        for obj in self.__save_deferred:
            obj.collection = self
            obj.save()

    def set_key_value(self, slug, value, field=None, obj=None, force=False,
                      defer=False):
        """
        This method sets an arbitrary key/value object, it will create a
        new objects or updated a pre-existing object.

        If the argument ``value`` contains the value 'increment' or
        'decrement' the value associated with the slug will be
        incremented or decremented.

        :param slug: The slug associated with a ``KeyValue`` object.
        :type slug: str
        :param value: Can be the actual value to set in a ``KeyValue``
                      object, or a model that inherits
                      ``CollectionBase`` or ``BaseChoice``.
        :type value: string or CollectionBase object
        :param field: Only used with ``CHOICE`` objects. Used to set the
                      value on the ``KeyValue`` object. If this keyword
                      argument is not set the default field will be used
                      when the ``dcolumn_manager.register_choice(choice,
                      relation_num, field)`` was configured.
        :type field: str or None
        :param obj: A ``KeyValue`` object.
        :type obj: ``KeyValue`` object
        :param force: Default is ``False``, do not save empty strings else
                      ``True`` save empty strings only.
        :type force: bool
        :param defer: Defer saving the KeyValue record. ``False`` is
                      default.
        :type defer: bool
        :raises ValueError: Invalid combination of parameters.
        :raises KeyValue.DoesNotExist: If the `KeyValue` model object was
                                       not found.
        """
        if (force and value == '') or value not in (None, ''):
            dc = self.get_dynamic_column(slug)

            if dc:
                if dc.value_type == dc.CHOICE:
                    value = self._is_set_choice(dc, value, field)
                elif dc.value_type in (dc.TIME, dc.DATE, dc.DATETIME):
                    value = self._is_set_datetime(dc, value)
                elif (dc.value_type == dc.NUMBER and
                      value in ('increment', 'decrement')):
                    pass
                elif dc.value_type == dc.BOOLEAN:
                    value = self._is_set_boolean(dc, value)
                elif dc.value_type == dc.FLOAT:
                    value = self._is_set_float(dc, value)
                elif dc.value_type == dc.NUMBER:
                    value = self._is_set_number(dc, value)
                elif (dc.value_type in (dc.TEXT, dc.TEXT_BLOCK) and
                      isinstance(value, six.string_types)):
                    pass
                else: # pragma: no cover
                    # This should never happen. An invalid value_type
                    # will raise a ValidationError when the DynamicColumn
                    # is created.
                    self._raise_exception(dc, value)

                created = False

                if not obj:
                    try:
                        obj = self.keyvalues.get(collection=self,
                                                 dynamic_column=dc)
                    except KeyValue.DoesNotExist:
                        obj = KeyValue(collection=self, dynamic_column=dc)
                        created = True

                if not created:
                    if 'increment' == value and obj.value.isdigit():
                        value = str(int(obj.value) + 1)
                    elif 'decrement' == value and obj.value.isdigit():
                        value = str(int(obj.value) - 1)

                obj.value = value

                if defer:
                    self.__save_deferred.append(obj)
                else:
                    obj.save()
            else:
                msg = "Could not find DynamicColumn for slug '{}'.".format(
                    slug)
                log.error(msg)
                raise ValueError(msg)
        else:
            msg = ("Could not process the data as passed to {}, "
                   "slug: {}, value: {}, force: {}").format(
                self.set_key_value.__name__, slug, value, force)
            log.error(msg)
            raise ValueError(msg)

    def _is_set_choice(self, dc, value, field):
        model, m_field = dc.get_choice_relation_object_and_field()

        if not field:
            field = m_field

        if dc.store_relation and value and field:
            result = getattr(value, field)
        elif isinstance(value, (CollectionBase, BaseChoice)): # Normal mode
            result = getattr(value, 'pk')
        elif isinstance(value, six.string_types):
            if value.isdigit() or value == '':
                result = value
            else:
                self._raise_exception(dc, value, field=field)
        elif isinstance(value, six.integer_types):
            result = str(value)
        else: # pragma: no cover
            self._raise_exception(dc, value, field=field)

        return result

    def _is_set_datetime(self, dc, value):
        if isinstance(value, (datetime.time, datetime.date,
                              datetime.datetime)):
            result = value.isoformat()
        elif isinstance(value, six.string_types):
            try:
                dt = parser.parse(value)
            except ValueError as e:
                self._raise_exception(dc, value, except_msg=e)
            else:
                result = value
        else:
            self._raise_exception(dc, value)

        return result

    def _is_set_boolean(self, dc, value):
        if isinstance(value, bool):
            result = str(value)
        elif isinstance(value, six.integer_types):
            result = str(0 if value == 0 else 1)
        elif isinstance(value, six.string_types):
            if (value.lower() in self.TRUE_FALSE or
                value.lower() in self.YES_NO):
                result = value
            elif value.isdigit():
                result = str(0 if int(value) == 0 else 1)
            else:
                self._raise_exception(dc, value)
        else:
            self._raise_exception(dc, value)

        return result

    def _is_set_float(self, dc, value):
        if isinstance(value, float):
            result = str(value)
        elif isinstance(value, six.integer_types):
            result = str(float(value))
        elif (isinstance(value, six.string_types) and
              value.replace('.', '').isdigit()):
            result = str(float(value))
        else:
            self._raise_exception(dc, value)

        return result

    def _is_set_number(self, dc, value):
        if isinstance(value, six.integer_types):
            result = str(value)
        elif isinstance(value, six.string_types) and value.isdigit():
            result = value
        else:
            self._raise_exception(dc, value)

        return result

    def _raise_exception(self, dc, value, field='(Not applicable)',
                         except_msg=''):
        msg = _("Invalid value {}, should be of type {}, with field: {}, "
                "{}.").format(value, DynamicColumn.VALUE_TYPES_MAP.get(
            dc.value_type), field, except_msg)
        log.error(msg)
        raise ValueError(msg)


#
# KeyValue
#
class KeyValueManager(models.Manager):
    pass


@python_2_unicode_compatible
class KeyValue(ValidateOnSaveMixin):
    collection = models.ForeignKey(
        CollectionBase, on_delete=models.CASCADE,
        verbose_name=_("Collection Type"), related_name='keyvalues')
    dynamic_column = models.ForeignKey(
        DynamicColumn, on_delete=models.CASCADE,
        verbose_name=_("Dynamic Column"), related_name='keyvalues')
    value = models.TextField(verbose_name=_("Value"), null=True, blank=True)

    objects = KeyValueManager()

    def save(self, *args, **kwargs):
        """
        Be sure the complete MRO has their saves called.
        """
        log.debug("KeyValue pk: %s,  collection: %s, dynamic_column: %s, "
                  "value: %s, args: %s, kwargs: %s", self.pk, self.collection,
                  self.dynamic_column, self.value, args, kwargs)
        super(KeyValue, self).save(*args, **kwargs)

    def __str__(self):
        return self.dynamic_column.name

    class Meta:
        ordering = ('dynamic_column__location', 'dynamic_column__order',)
        verbose_name = _("Key Value")
        verbose_name_plural = _("Key Values")
