# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-09 02:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('regression', '0050_auto_20160309_1014'),
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