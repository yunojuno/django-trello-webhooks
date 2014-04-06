# -*- coding: utf-8 -*-
# trello_webhooks forms
from django import forms
from django.utils.safestring import mark_safe

from trello_webhooks.models import Webhook


class TrelloTokenWidget(forms.TextInput):
    # Special form element that renders a 'new token' link next to the input
    def __init__(self, *args, **kwargs):
        super(TrelloTokenWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        attrs['size'] = 85
        html = super(TrelloTokenWidget, self).render(name, value, attrs=attrs)
        html += u"&nbsp;<a onclick='getTrelloToken()' href='#'>Get new token</a>"
        return mark_safe(html)


class WebhookForm(forms.ModelForm):
    class Meta:
        model = Webhook
        exclude = []
    auth_token = forms.CharField(widget=TrelloTokenWidget())
