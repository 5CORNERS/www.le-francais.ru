# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-06 14:08
from __future__ import unicode_literals

from django.db import migrations
import wagtail.wagtailcore.blocks
import wagtail.wagtailcore.fields
import wagtail.wagtailimages.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_lessonpage_dictionary'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessonpage',
            name='comments_for_lesson',
            field=wagtail.wagtailcore.fields.StreamField((('paragraph', wagtail.wagtailcore.blocks.RichTextBlock()), ('image', wagtail.wagtailimages.blocks.ImageChooserBlock()), ('html', wagtail.wagtailcore.blocks.RawHTMLBlock()), ('audio', wagtail.wagtailcore.blocks.StructBlock((('url', wagtail.wagtailcore.blocks.URLBlock()),)))), blank=True, null=True),
        ),
    ]
