# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-03-26 20:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcolumns', '0003_auto_20160308_2158'),
    ]

    operations = [
        migrations.AddField(
            model_name='columncollection',
            name='related_model',
            field=models.CharField(help_text='Choose the related model.', max_length=50,
                                   unique=True, verbose_name='Related Model'),
        ),
    ]