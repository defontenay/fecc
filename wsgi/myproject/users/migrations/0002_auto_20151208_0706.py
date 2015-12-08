# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='slack_id',
            new_name='slack',
        ),
        migrations.AddField(
            model_name='user',
            name='error',
            field=models.CharField(default=' ', max_length=100),
            preserve_default=False,
        ),
    ]
