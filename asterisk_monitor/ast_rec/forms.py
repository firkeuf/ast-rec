# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from datetime import date, datetime
from models import ChannelList


class SearchForm(forms.Form):
    error_css_class = 'has-error'
    channel_choice = ChannelList().get_list()
    direction_choice = [('', ' Both'), ('incoming', '-> In'), ('phone', '<- Out')]
    disposition_choice = [('ANSWERED', 'Answered'),
                          ('NO ANSWER', 'No answer'),
                          ('BUSY', 'Busy'),
                          ('FAILED', 'Failed')
    ]

    src = forms.CharField(label=u'Source', max_length=50, required=False,
                          widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Source'}))
    dst = forms.CharField(label=u'Destination', max_length=50, required=False,
                          widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Destination'}))
    start_time = forms.DateTimeField(label=u'Start time', initial=date.today().strftime("%Y-%m-%d %H:%M"),
                                     required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    end_time = forms.DateTimeField(label=u'End time', initial=datetime.today().strftime("%Y-%m-%d %H:%M"),
                                   required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    channel = forms.MultipleChoiceField(label=u'Channel', choices=sorted(channel_choice), required=False,
                                        widget=forms.SelectMultiple(attrs={'id': 'channel-select'}))
    direction = forms.ChoiceField(label=u'Direction', choices=direction_choice, required=False,
                                  widget=forms.Select(attrs={'id': 'direction-select'}))
    disposition = forms.MultipleChoiceField(label=u'Disposition', choices=disposition_choice, required=False,
                                            widget=forms.SelectMultiple(attrs={'id': 'disposition-select'}))


class AuthForm(AuthenticationForm):
    username = forms.CharField(max_length=254, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Login'}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))