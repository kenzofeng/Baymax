# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-18 08:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('regression', '0045_auto_20151218_1645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job_test',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='regression.Job'),
        ),
        migrations.AlterField(
            model_name='log',
            name='job',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='regression.Job'),
        ),
    ]