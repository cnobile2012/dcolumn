# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-31 02:38
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectionBase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(help_text='The date and time of creation.', verbose_name='Date Created')),
                ('updated', models.DateTimeField(help_text='The date and time last updated.', verbose_name='Last Updated')),
                ('active', models.BooleanField(default=True, help_text='If checked the record is active.', verbose_name='Active')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ColumnCollection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(help_text='The date and time of creation.', verbose_name='Date Created')),
                ('updated', models.DateTimeField(help_text='The date and time last updated.', verbose_name='Last Updated')),
                ('active', models.BooleanField(default=True, help_text='If checked the record is active.', verbose_name='Active')),
                ('name', models.CharField(help_text='Enter a unique name for this record.', max_length=50, unique=True, verbose_name='Name')),
                ('creator', models.ForeignKey(editable=False, help_text='The user who created this record.', on_delete=django.db.models.deletion.CASCADE, related_name='dcolumns_columncollection_creator_related', to=settings.AUTH_USER_MODEL, verbose_name='Creator')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'Column Collection',
                'verbose_name_plural': 'Column Collections',
            },
        ),
        migrations.CreateModel(
            name='DynamicColumn',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(help_text='The date and time of creation.', verbose_name='Date Created')),
                ('updated', models.DateTimeField(help_text='The date and time last updated.', verbose_name='Last Updated')),
                ('active', models.BooleanField(default=True, help_text='If checked the record is active.', verbose_name='Active')),
                ('name', models.CharField(help_text='Enter a column name.', max_length=50, verbose_name='Name')),
                ('preferred_slug', models.SlugField(blank=True, help_text="If you don't want the slug to change when the name changes enter a slug here. However, if you change this field the slug will track it.", null=True, verbose_name='Preferred Slug')),
                ('slug', models.SlugField(editable=False, help_text='This field is normally created from the name field, however, if you want to prevent it from changing when the name changes enter a preferred slug above.', verbose_name='Slug')),
                ('value_type', models.IntegerField(choices=[(1, 'Boolean'), (2, 'Choice'), (3, 'Date'), (4, b'Date Time'), (5, 'Floating Point'), (6, 'Number'), (7, 'Text'), (8, 'Text Block'), (9, b'Time')], help_text='Choose the value type.', verbose_name='Value Type')),
                ('relation', models.IntegerField(blank=True, help_text='Choose the Choice Relation Type.', null=True, verbose_name='Choice Relation')),
                ('required', models.BooleanField(choices=[(False, 'No'), (True, 'Yes')], default=False, help_text="If this field is required based on business rules then choose 'Yes'.", verbose_name='Required Field')),
                ('store_relation', models.BooleanField(choices=[(False, 'No'), (True, 'Yes')], default=False, help_text="Store the literal value not the primary key of the relation (used when choices change often). The most common usage is the default 'No', to not store.", verbose_name='Store Relation Value')),
                ('location', models.CharField(choices=[(b'author_top', b'author-top'), (b'author_center', b'author-center'), (b'author_bottom', b'author-botton'), (b'book_top', b'book-top'), (b'book_center', b'book-center'), (b'book_bottom', b'book-bottom'), (b'promotion_top', b'promotion-top'), (b'promotion_center', b'promotion-center'), (b'promotion_bottom', b'promotion-bottom'), (b'publisher_top', b'publisher-top'), (b'publisher_center', b'publisher-center'), (b'publisher_bottom', b'publisher-bottom')], help_text='Choose a display location.', max_length=50, verbose_name='Display Location')),
                ('order', models.PositiveSmallIntegerField(verbose_name=b'Display Order')),
                ('creator', models.ForeignKey(editable=False, help_text='The user who created this record.', on_delete=django.db.models.deletion.CASCADE, related_name='dcolumns_dynamiccolumn_creator_related', to=settings.AUTH_USER_MODEL, verbose_name='Creator')),
                ('updater', models.ForeignKey(editable=False, help_text='The last user to update this record.', on_delete=django.db.models.deletion.CASCADE, related_name='dcolumns_dynamiccolumn_updater_related', to=settings.AUTH_USER_MODEL, verbose_name='Updater')),
            ],
            options={
                'ordering': ('location', 'order', 'name'),
                'verbose_name': 'Dynamic Column',
                'verbose_name_plural': 'Dynamic Columns',
            },
        ),
        migrations.CreateModel(
            name='KeyValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField(blank=True, null=True, verbose_name='Value')),
                ('collection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='keyvalue_pairs', to='dcolumns.CollectionBase', verbose_name='Collection Type')),
                ('dynamic_column', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='keyvalue_pairs', to='dcolumns.DynamicColumn', verbose_name='Dynamic Column')),
            ],
            options={
                'ordering': ('dynamic_column__location', 'dynamic_column__order'),
                'verbose_name': 'Key Value',
                'verbose_name_plural': 'Key Values',
            },
        ),
        migrations.AddField(
            model_name='columncollection',
            name='dynamic_column',
            field=models.ManyToManyField(related_name='column_collection', to='dcolumns.DynamicColumn', verbose_name='Dynamic Column'),
        ),
        migrations.AddField(
            model_name='columncollection',
            name='updater',
            field=models.ForeignKey(editable=False, help_text='The last user to update this record.', on_delete=django.db.models.deletion.CASCADE, related_name='dcolumns_columncollection_updater_related', to=settings.AUTH_USER_MODEL, verbose_name='Updater'),
        ),
        migrations.AddField(
            model_name='collectionbase',
            name='column_collection',
            field=models.ForeignKey(help_text='Choose the version of the dynamic columns you want for all Collections.', on_delete=django.db.models.deletion.CASCADE, to='dcolumns.ColumnCollection', verbose_name='Column Collection'),
        ),
        migrations.AddField(
            model_name='collectionbase',
            name='creator',
            field=models.ForeignKey(editable=False, help_text='The user who created this record.', on_delete=django.db.models.deletion.CASCADE, related_name='dcolumns_collectionbase_creator_related', to=settings.AUTH_USER_MODEL, verbose_name='Creator'),
        ),
        migrations.AddField(
            model_name='collectionbase',
            name='updater',
            field=models.ForeignKey(editable=False, help_text='The last user to update this record.', on_delete=django.db.models.deletion.CASCADE, related_name='dcolumns_collectionbase_updater_related', to=settings.AUTH_USER_MODEL, verbose_name='Updater'),
        ),
    ]
