# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EventType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(help_text=b'The name of the event as sent from Trello.', max_length=30)),
                ('event_count', models.IntegerField(default=0, help_text=b'The count of times this event has been received - ignores the is_active attr.')),
                ('is_active', models.BooleanField(default=True, help_text='If True, send notification to HipChat, else ignore.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
