# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-28 12:39
from __future__ import unicode_literals

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0057_auto_20180723_2139'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lessonpage',
            name='invisible_dictionary',
        ),
        migrations.AddField(
            model_name='lessonpage',
            name='mail_archive',
            field=wagtail.core.fields.StreamField([('paragraph', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('document', wagtail.core.blocks.StructBlock([('url', wagtail.core.blocks.CharBlock()), ('page', wagtail.core.blocks.IntegerBlock(required=False))])), ('html', wagtail.core.blocks.RawHTMLBlock()), ('audio', wagtail.core.blocks.StructBlock([('url', wagtail.core.blocks.CharBlock()), ('downloadable', wagtail.core.blocks.BooleanBlock(required=False))])), ('video', wagtail.core.blocks.StructBlock([('source', wagtail.core.blocks.CharBlock()), ('poster', wagtail.core.blocks.CharBlock(required=False))])), ('translations', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock([('word', wagtail.core.blocks.RichTextBlock(required=True)), ('translation', wagtail.core.blocks.RichTextBlock(required=True))]), template='blocks/transcriptions.html')), ('post', wagtail.core.blocks.StructBlock([('post_id', wagtail.core.blocks.IntegerBlock())]))], blank=True, null=True),
        ),
    ]
