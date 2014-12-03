# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trello_webhooks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='webhook',
            name='is_active',
            field=models.NullBooleanField(default=None),
            preserve_default=True,
        ),
    ]
