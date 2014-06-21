#
# dcolumn/common/model_mixins.py
#

import re
import logging

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

log = logging.getLogger('dcolumn.models')


#
# UserModel
#
class UserModelMixin(models.Model):
    user = models.ForeignKey(
        User, verbose_name=_("Updater"), db_index=True, editable=False,
        related_name="%(app_label)s_%(class)s_updater_related",
        help_text=_("The last user to modify this record."))
    creator = models.ForeignKey(
        User, verbose_name=_("Creator"), db_index=True, editable=False,
        related_name="%(app_label)s_%(class)s_creator_related",
        help_text=_("The user  who created this record."))

    class Meta:
        abstract = True


#
# TimeModel
#
class TimeModelMixin(models.Model):
    ctime = models.DateTimeField(
        verbose_name=_("Date Created"), auto_now_add=True,
        help_text=_("The date and time of creation."))
    mtime = models.DateTimeField(
        verbose_name=_("Last Modified"), auto_now=True,
        help_text=_("The date and time last modified."))

    class Meta:
        abstract = True


#
# StatusModel
#
class StatusModelManagerMixin(models.Manager):

    def active(self, active=True):
        return self.filter(active=active)


class StatusModelMixin(models.Model):
    active = models.BooleanField(
        verbose_name=_("Active"), default=True,
        help_text=_("If checked the record is active."))

    class Meta:
        abstract = True
