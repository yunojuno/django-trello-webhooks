# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CallbackEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField()),
                ('event_type', models.CharField(max_length=50)),
                ('event_payload', jsonfield.fields.JSONField(default=dict)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Webhook',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trello_model_id', models.CharField(help_text='The id of the model being watched.', max_length=24)),
                ('trello_id', models.CharField(help_text='Webhook id returned from Trello API.', max_length=24, blank=True)),
                ('description', models.CharField(help_text='Description of the webhook.', max_length=500, blank=True)),
                ('auth_token', models.CharField(help_text='The Trello API user auth token.', max_length=64)),
                ('created_at', models.DateTimeField(blank=True)),
                ('last_updated_at', models.DateTimeField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='callbackevent',
            name='webhook',
            field=models.ForeignKey(to='trello_webhooks.Webhook'),
            preserve_default=True,
        ),
    ]
