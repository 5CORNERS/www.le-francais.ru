# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-01 12:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0077_auto_20190401_1229'),
    ]

    operations = [
        migrations.AddField(
            model_name='adunit',
            name='page_type',
            field=models.CharField(blank=True, choices=[('lesson_a1', 'Lesson A1'), ('lesson_a2', 'Lesson A2'), ('lesson_b2', 'Lesson_B2'), ('lesson_page', 'Lesson Page'), ('page_with_sidebar', '"Page with sidebar"'), ('article_page', 'Article Page'), ('index_page', 'Title Page'), ('conjugation_index', 'Conjugation Title'), ('conjugation_verb', 'Conjugation Verb'), ('none', 'None')], default=None, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='adunit',
            name='placement',
            field=models.CharField(blank=True, choices=[('sidebar', 'Sidebar'), ('none', 'None'), ('resume_top', 'Resume Top'), ('resume_bottom', 'Resume Bottom'), ('revision_top', 'Revision Top'), ('revision_bottom', 'Revision Bottom')], default=None, max_length=20, null=True),
        ),
    ]
