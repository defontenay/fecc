# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_global'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Global',
        ),
    ]
