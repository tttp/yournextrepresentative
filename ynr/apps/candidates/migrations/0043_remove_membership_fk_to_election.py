# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2018-05-15 15:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0043_remove_simple_popolo_field'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='membershipextra',
            name='election',
        ),
    ]
