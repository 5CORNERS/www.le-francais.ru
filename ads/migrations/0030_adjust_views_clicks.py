# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations

def adjust_views_clicks(apps, schema_editor):
    LineItem = apps.get_model('ads', 'LineItem')
    Creative = apps.get_model('ads', 'Creative')
    Log = apps.get_model('ads', 'Log')

    # For LineItems
    for item in LineItem.objects.all():
        active_views = Log.objects.filter(line_item=item).count()
        active_clicks = Log.objects.filter(line_item=item, clicked=True).count()
        item.views = max(0, item.views - active_views)
        item.clicks = max(0, item.clicks - active_clicks)
        item.save()

    # For Creatives
    for creative in Creative.objects.all():
        active_views = Log.objects.filter(creative=creative).count()
        active_clicks = Log.objects.filter(creative=creative, clicked=True).count()
        creative.views = max(0, creative.views - active_views)
        creative.clicks = max(0, creative.clicks - active_clicks)
        creative.save()

def reverse_adjust(apps, schema_editor):
    LineItem = apps.get_model('ads', 'LineItem')
    Creative = apps.get_model('ads', 'Creative')
    Log = apps.get_model('ads', 'Log')

    for item in LineItem.objects.all():
        active_views = Log.objects.filter(line_item=item).count()
        active_clicks = Log.objects.filter(line_item=item, clicked=True).count()
        item.views = item.views + active_views
        item.clicks = item.clicks + active_clicks
        item.save()

    for creative in Creative.objects.all():
        active_views = Log.objects.filter(creative=creative).count()
        active_clicks = Log.objects.filter(creative=creative, clicked=True).count()
        creative.views = creative.views + active_views
        creative.clicks = creative.clicks + active_clicks
        creative.save()

class Migration(migrations.Migration):
    dependencies = [
        ('ads', '0029_auto_20230120_2018'),
    ]
    operations = [
        migrations.RunPython(adjust_views_clicks, reverse_adjust),
    ]
