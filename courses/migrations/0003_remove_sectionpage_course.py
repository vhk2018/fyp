# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-01-02 16:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_auto_20190103_0027'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sectionpage',
            name='course',
        ),
    ]