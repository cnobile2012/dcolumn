#
# dcolumn/common/model_mixins.py
#

__docformat__ = "restructuredtext en"

import re
import logging
from datetime import datetime
from dateutil.tz import tzutc

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

log = logging.getLogger('dcolumn.models')


#
# UserModel
#
class UserModelMixin(models.Model):
    """
    Abstract model mixin used in the model classes to provide user and
    creator fields.
    """

    user = models.ForeignKey(
        User, verbose_name=_("Modifier"), db_index=True, editable=False,
        related_name="%(app_label)s_%(class)s_updater_related",
        help_text=_("The last user to modify this record."))
    creator = models.ForeignKey(
        User, verbose_name=_("Creator"), db_index=True, editable=False,
        related_name="%(app_label)s_%(class)s_creator_related",
        help_text=_("The user  who created this record."))

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Save is here to assure that save is executed throughout the MRO.
        """
        super(UserModelMixin, self).save(*args, **kwargs)

    def _user_producer(self):
        """
        Primary use is in the admin class to supply the user's full name.
        """
        return self.user.get_full_name()
    _user_producer.short_description = _("Updater")

    def _creator_producer(self):
        """
        Primary use is in the admin class to supply the creator's full name.
        """
        return self.creator.get_full_name()
    _creator_producer.short_description = _("Creator")


#
# TimeModel
#
class TimeModelMixin(models.Model):
    """
    Abstract model mixin used in the model classes to supply ctime and mtime
    fields.
    """

    ctime = models.DateTimeField(
        verbose_name=_("Date Created"),
        help_text=_("The date and time of creation."))
    mtime = models.DateTimeField(
        verbose_name=_("Last Modified"),
        help_text=_("The date and time last modified."))

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Permit the disabling of the ctime and mtime.
        """
        if not kwargs.pop(u'disable_ctime', False) and self.ctime is None:
            self.ctime = datetime.now(tzutc())

        if not kwargs.pop(u'disable_mtime', False):
            self.mtime = datetime.now(tzutc())

        log.debug("kwargs: %s, ctime: %s, mtime: %s",
                  kwargs, self.ctime, self.mtime)
        super(TimeModelMixin, self).save(*args, **kwargs)


#
# StatusModel
#
class StatusModelManagerMixin(models.Manager):
    """
    Manager mixin for the StatusModelMixin abstract model.
    """

    def active(self, active=True):
        """
        Return as default only active database objects.

        :Parameters:
          active : `bool`
            If `True` return only active records else if `False` return
            non-active records. If `None` return all records.
        """
        query = []

        if active is not None:
            query.append(Q(active=active))

        return self.filter(*query)


class StatusModelMixin(models.Model):
    """
    Abstract model mixin used in the model classes to supply the active field.
    """

    active = models.BooleanField(
        verbose_name=_("Active"), default=True,
        help_text=_("If checked the record is active."))

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Save is here to assure that save is executed throughout the MRO.
        """
        super(StatusModelMixin, self).save(*args, **kwargs)
