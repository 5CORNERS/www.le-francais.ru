# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-03-30 15:17
from __future__ import unicode_literals

import annoying.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import json
import mass_mailer.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('host', models.CharField(max_length=64)),
                ('port', models.CharField(max_length=64)),
                ('username', models.CharField(max_length=64)),
                ('password', models.CharField(max_length=64)),
                ('use_tls', models.BooleanField()),
                ('use_ssl', models.BooleanField()),
                ('sender_email', models.EmailField(max_length=254, null=True)),
                ('sender_username', models.CharField(max_length=100, null=True)),
                ('messages_per_connection', models.IntegerField(default=35)),
                ('delay_between_connections', models.IntegerField(default=10, help_text='In seconds')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('template_subject', models.CharField(blank=True, max_length=64)),
                ('template_html', models.TextField(blank=True, help_text='You can ')),
                ('template_txt', models.TextField(blank=True)),
                ('from_username', models.CharField(max_length=64)),
                ('from_email', models.EmailField(max_length=254)),
                ('reply_to_username', models.CharField(blank=True, max_length=64, null=True)),
                ('reply_to_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('extra_headers', annoying.fields.JSONField(blank=True, default=dict, deserializer=json.loads, help_text='JSON Dict Format', serializer=annoying.fields.dumps)),
                ('created_datetime', models.DateTimeField(auto_now_add=True)),
                ('send_datetime', models.DateTimeField(null=True)),
                ('email_settings', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='mass_mailer.EmailSettings')),
            ],
        ),
        migrations.CreateModel(
            name='MessageLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sent_datetime', models.DateTimeField(auto_now_add=True)),
                ('result', models.IntegerField(choices=[(1, 'Success'), (2, 'Failure'), (3, "Didn't send")], default=3)),
                ('log_message', models.TextField(blank=True, null=True)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mass_mailer.Message')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('key', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('subscribed', models.BooleanField(default=True)),
                ('user', annoying.fields.AutoOneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='mailer_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UsersFilter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('filters', mass_mailer.models.ChoiceArrayField(base_field=models.CharField(choices=[('0', 'Users w/o activations'), ('1', 'Users with payments'), ('2', 'Payments w/o activations')], max_length=12), blank=True, default=list, size=None)),
                ('first_payment_was', models.DateField(null=True)),
                ('last_payment_was', models.DateField(null=True)),
                ('manual_email_list', models.TextField(blank=True, default=None, help_text='Comma-separated list of emails, for testing purposes.', max_length=1024, null=True)),
                ('ignore_subscriptions', models.BooleanField(default=False)),
                ('send_once', models.BooleanField(default=True)),
                ('blacklist', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='recipients_filter',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='mass_mailer.UsersFilter'),
        ),
        migrations.AddField(
            model_name='message',
            name='sent',
            field=models.ManyToManyField(blank=True, null=True, related_name='mass_mailer_received', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='message',
            name='was_sent_to',
            field=models.ManyToManyField(related_query_name='received_mass_mailer_messages', through='mass_mailer.MessageLog', to=settings.AUTH_USER_MODEL),
        ),
    ]
