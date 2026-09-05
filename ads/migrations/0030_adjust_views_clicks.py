# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations

def adjust_views_clicks(apps, schema_editor):
    cursor = schema_editor.connection.cursor()

    # Update LineItems in bulk
    cursor.execute("""
        UPDATE ads_lineitem
        SET 
          views = CASE 
            WHEN views - COALESCE((SELECT COUNT(*) FROM ads_log WHERE ads_log.line_item_id = ads_lineitem.id), 0) < 0 THEN 0
            ELSE views - COALESCE((SELECT COUNT(*) FROM ads_log WHERE ads_log.line_item_id = ads_lineitem.id), 0)
          END,
          clicks = CASE 
            WHEN clicks - COALESCE((SELECT COUNT(*) FROM ads_log WHERE ads_log.line_item_id = ads_lineitem.id AND ads_log.clicked), 0) < 0 THEN 0
            ELSE clicks - COALESCE((SELECT COUNT(*) FROM ads_log WHERE ads_log.line_item_id = ads_lineitem.id AND ads_log.clicked), 0)
          END
    """)

    # Update Creatives in bulk
    cursor.execute("""
        UPDATE ads_creative
        SET 
          views = CASE 
            WHEN views - COALESCE((SELECT COUNT(*) FROM ads_log WHERE ads_log.creative_id = ads_creative.id), 0) < 0 THEN 0
            ELSE views - COALESCE((SELECT COUNT(*) FROM ads_log WHERE ads_log.creative_id = ads_creative.id), 0)
          END,
          clicks = CASE 
            WHEN clicks - COALESCE((SELECT COUNT(*) FROM ads_log WHERE ads_log.creative_id = ads_creative.id AND ads_log.clicked), 0) < 0 THEN 0
            ELSE clicks - COALESCE((SELECT COUNT(*) FROM ads_log WHERE ads_log.creative_id = ads_creative.id AND ads_log.clicked), 0)
          END
    """)

def reverse_adjust(apps, schema_editor):
    cursor = schema_editor.connection.cursor()

    # Restore LineItems in bulk
    cursor.execute("""
        UPDATE ads_lineitem
        SET 
          views = views + COALESCE((SELECT COUNT(*) FROM ads_log WHERE ads_log.line_item_id = ads_lineitem.id), 0),
          clicks = clicks + COALESCE((SELECT COUNT(*) FROM ads_log WHERE ads_log.line_item_id = ads_lineitem.id AND ads_log.clicked), 0)
    """)

    # Restore Creatives in bulk
    cursor.execute("""
        UPDATE ads_creative
        SET 
          views = views + COALESCE((SELECT COUNT(*) FROM ads_log WHERE ads_log.creative_id = ads_creative.id), 0),
          clicks = clicks + COALESCE((SELECT COUNT(*) FROM ads_log WHERE ads_log.creative_id = ads_creative.id AND ads_log.clicked), 0)
    """)

class Migration(migrations.Migration):
    dependencies = [
        ('ads', '0029_auto_20230120_2018'),
    ]
    operations = [
        migrations.RunPython(adjust_views_clicks, reverse_adjust),
    ]
