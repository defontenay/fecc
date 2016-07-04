# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20151208_0706'),
    ]

    operations = [
        migrations.CreateModel(
            name='Global',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('value', models.CharField(max_length=20)),
            ],
        ),
    ]
