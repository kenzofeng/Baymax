# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-10 03:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('regression', '0017_auto_20151210_1128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job_tests',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='regression.Job'),
        ),
    ]
