# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-04 14:51
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('axf', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wheel',
            name='isDelete',
        ),
    ]
