# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-14 02:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('regression', '0024_auto_20151211_1731'),
    ]

    operations = [
        migrations.AddField(
            model_name='job_tests',
            name='status',
            field=models.CharField(choices=[(b'r', b'running'), (b'd', b'done'), (b'e', b'error'), (b'w', b'waitting')], default='', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='job_tests',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='regression.Job'),
        ),
    ]