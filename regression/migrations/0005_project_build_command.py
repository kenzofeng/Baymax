# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-08 08:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regression', '0004_remove_project_svn'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='build_command',
            field=models.CharField(default='', max_length=250),
            preserve_default=False,
        ),
    ]
