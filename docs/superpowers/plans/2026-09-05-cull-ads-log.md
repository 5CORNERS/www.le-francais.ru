# Ads Log Culling Feature Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a command to cull/delete old log entries, aggregate their views/clicks counts into their related Creative and LineItem models, and display the combined live and historical stats in Django Admin without double-counting.

**Architecture:**
* **Data Migration:** Adjust current views/clicks values on existing LineItem and Creative models by subtracting the active logs count, making them purely archive/culled counts.
* **Stop Real-Time field updates:** Remove direct database modifications of `views` and `clicks` fields on models during real-time requests. Active views/clicks will only be tracked via persistent `Log` entries.
* **Log Culling Command:** Create a Django management command to atomically aggregate old log views and clicks, increment those values into their respective models, and delete those logs from the database.
* **Admin Customization:** Modify Django admin for LineItem and Creative to calculate and display the combined live and archived views and clicks in real-time.

**Tech Stack:** Django 1.11, Python 3.7, SQLite/PostgreSQL, Powershell.

**Spec:** Bounded design approved in chat on 2026-09-05.

## Global Constraints
* **Python Environment Path:** `C:\Users\anton\miniconda3\envs\le-francais\python.exe`
* **Django Version:** `>= 1.11.29, < 2.0.0`
* **Shell:** PowerShell syntax exclusively
* **Pathing:** Backslashes (`\`) for file paths
* **Formatting:** CRLF line endings for all generated files

---

### Task 1: Decouple Live Events from Model Fields

**Files:**
* Modify: `ads\templatetags\ads.py`
* Modify: `ads\views.py`
* Modify: `ads\tests.py`

**Interfaces:**
* Consumes: Model definitions of `Log`, `Creative`, `LineItem`.
* Produces: Modified live views and template tags that do NOT directly increment `views`/`clicks` columns on model instances in real-time.

* [ ] **Step 1: Write the failing tests**
  Add test cases to `ads\tests.py` that check that rendering an ad or recording a click does NOT change `line_item.views`, `line_item.clicks`, `creative.views`, or `creative.clicks` directly.

  ```python
  from django.test import TestCase, RequestFactory
  from django.contrib.auth import get_user_model
  from django.utils import timezone
  from django.contrib.sessions.middleware import SessionMiddleware
  from ads.models import LineItem, Creative, Log
  from ads.views import AdCounterRedirectView, get_creative_dict

  User = get_user_model()

  class LiveIncrementDecoupleTestCase(TestCase):
      def setUp(self):
          self.user = User.objects.create_user(username='testuser', email='test@test.com', password='password')
          self.line_item = LineItem.objects.create(name='Test Line Item', priority=10)
          self.creative = Creative.objects.create(
              name='Test Creative',
              line_item=self.line_item,
              image_click_through_url='https://example.com'
          )
          self.factory = RequestFactory()

      def test_live_view_does_not_increment_fields(self):
          # Initial views count
          initial_li_views = self.line_item.views
          initial_cr_views = self.creative.views

          # Simulate AJAX creative request
          request = self.factory.get('/ads/get-html/', {'ad_unit_name': 'test_unit'})
          request.user = self.user
          # Setup sessions
          middleware = SessionMiddleware()
          middleware.process_request(request)
          request.session['geoip'] = {'country_code': 'FR', 'city': 'Paris', 'country_name': 'France'}
          request.session.save()

          # Call the view logic
          res = get_creative_dict(request)

          # Verify a Log was created
          self.assertEqual(Log.objects.filter(creative=self.creative).count(), 1)

          # Reload models
          self.line_item.refresh_from_db()
          self.creative.refresh_from_db()

          # Verify that model views fields DID NOT change
          self.assertEqual(self.line_item.views, initial_li_views)
          self.assertEqual(self.creative.views, initial_cr_views)
  ```

* [ ] **Step 2: Run the test to verify it fails**
  Run: `C:\Users\anton\miniconda3\envs\le-francais\python.exe manage.py test ads`
  Expected: FAIL (fields are incremented live).

* [ ] **Step 3: Modify `ads\templatetags\ads.py` to remove live view increment**
  Remove lines 176-178:
  ```python
  # In ads\templatetags\ads.py
  if not context['request'].user.is_staff:
      line_item.views = F('views') + 1
      line_item.save()
  ```

* [ ] **Step 4: Modify `ads\views.py` to remove live view & click increments**
  Remove client-side view increments (lines 325-328):
  ```python
  # In ads\views.py
  chosen_creative.views += 1
  chosen_creative.save(update_fields=['views'])
  chosen_creative.line_item.views += 1
  chosen_creative.line_item.save(update_fields=['views'])
  ```
  Remove client-side click increments (lines 44-48):
  ```python
  # In ads\views.py
  creative.clicks = F('clicks') + 1
  creative.save(update_fields=['clicks'])

  line_item.clicks = F('clicks') + 1
  line_item.save(update_fields=['clicks'])
  ```

* [ ] **Step 5: Run the tests to verify they pass**
  Run: `C:\Users\anton\miniconda3\envs\le-francais\python.exe manage.py test ads`
  Expected: PASS.

* [ ] **Step 6: Commit changes**
  Run:
  ```powershell
  git add ads\templatetags\ads.py ads\views.py ads\tests.py
  git commit -m "feat(ads): decouple live view and click increments from model columns"
  ```

---

### Task 2: Create Data Migration to Adjust Existing Totals

**Files:**
* Create: `ads\migrations\0030_adjust_views_clicks.py`

**Interfaces:**
* Consumes: Model definitions of `Log`, `Creative`, `LineItem`.
* Produces: Safe migration script that subtracts existing active log counts from total counts.

* [ ] **Step 1: Create the migration file**
  Create `ads\migrations\0030_adjust_views_clicks.py` with the following content:

  ```python
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
  ```

* [ ] **Step 2: Run the migrations**
  Run: `C:\Users\anton\miniconda3\envs\le-francais\python.exe manage.py migrate ads`
  Expected: Success.

* [ ] **Step 3: Commit migration**
  Run:
  ```powershell
  git add ads\migrations\0030_adjust_views_clicks.py
  git commit -m "migration(ads): convert current views/clicks totals to historical archived values"
  ```

---

### Task 3: Implement Log Culling Command

**Files:**
* Create: `ads\management\commands\cull_logs.py`
* Modify: `ads\tests.py`

**Interfaces:**
* Consumes: Positional argument `days` (int).
* Produces: A Django command that purges logs older than N days and aggregates their counts back to model fields atomically.

* [ ] **Step 1: Write the failing tests**
  Add tests verifying that `python manage.py cull_logs <days>` purges appropriate logs and updates `views` and `clicks` on `LineItem`/`Creative` correctly.

  ```python
  from datetime import timedelta
  from django.utils import timezone
  from django.core.management import call_command
  from ads.models import LineItem, Creative, Log

  class CullLogsCommandTestCase(TestCase):
      def setUp(self):
          self.line_item = LineItem.objects.create(name='Cull Test Line Item', priority=1, views=10, clicks=5)
          self.creative = Creative.objects.create(name='Cull Test Creative', line_item=self.line_item, views=8, clicks=4)
          
          # Create logs
          now = timezone.now()
          # Logs older than 10 days (should be culled)
          Log.objects.create(
              datetime=now - timedelta(days=15),
              line_item=self.line_item,
              creative=self.creative,
              ip='127.0.0.1',
              clicked=True
          )
          Log.objects.create(
              datetime=now - timedelta(days=12),
              line_item=self.line_item,
              creative=self.creative,
              ip='127.0.0.1',
              clicked=False
          )
          # Log newer than 10 days (should NOT be culled)
          Log.objects.create(
              datetime=now - timedelta(days=5),
              line_item=self.line_item,
              creative=self.creative,
              ip='127.0.0.1',
              clicked=False
          )

      def test_cull_logs_command(self):
          # Cull logs older than 10 days
          call_command('cull_logs', 10)

          # Reload models
          self.line_item.refresh_from_db()
          self.creative.refresh_from_db()

          # Expecting 2 culled logs: 2 views, 1 click added to model fields
          self.assertEqual(self.line_item.views, 12)  # 10 + 2
          self.assertEqual(self.line_item.clicks, 6)  # 5 + 1
          self.assertEqual(self.creative.views, 10)  # 8 + 2
          self.assertEqual(self.creative.clicks, 5)  # 4 + 1

          # Only 1 log should remain in the database
          self.assertEqual(Log.objects.count(), 1)
  ```

* [ ] **Step 2: Run the test to verify it fails**
  Run: `C:\Users\anton\miniconda3\envs\le-francais\python.exe manage.py test ads`
  Expected: FAIL (command `cull_logs` does not exist).

* [ ] **Step 3: Implement `ads\management\commands\cull_logs.py`**
  Write the management command. Ensure to handle `auto_now_add` in logs by mock/stubbing or setting `datetime` manually where necessary, and using transaction atomic lock:

  ```python
  from datetime import timedelta
  from django.core.management.base import BaseCommand
  from django.utils import timezone
  from django.db import transaction, models
  from django.db.models import Count, Sum, Case, When, IntegerField, F
  from ads.models import Log, Creative, LineItem

  class Command(BaseCommand):
      help = "Removes log entries older than N days and aggregates their counts into the corresponding models."

      def add_arguments(self, parser):
          parser.add_argument('days', type=int, help='Cull logs older than this number of days.')

      def handle(self, *args, **options):
          days = options['days']
          cutoff_datetime = timezone.now() - timedelta(days=days)
          old_logs = Log.objects.filter(datetime__lt=cutoff_datetime)

          total_to_cull = old_logs.count()
          if total_to_cull == 0:
              self.stdout.write(self.style.SUCCESS("No logs to cull."))
              return

          self.stdout.write(f"Found {total_to_cull} logs to cull.")

          # Aggregate stats for creatives
          creative_stats = old_logs.values('creative').annotate(
              views_count=Count('id'),
              clicks_count=Sum(
                  Case(
                      When(clicked=True, then=1),
                      default=0,
                      output_field=IntegerField()
                  )
              )
          )

          # Aggregate stats for line items
          line_item_stats = old_logs.values('line_item').annotate(
              views_count=Count('id'),
              clicks_count=Sum(
                  Case(
                      When(clicked=True, then=1),
                      default=0,
                      output_field=IntegerField()
                  )
              )
          )

          with transaction.atomic():
              # Update creatives
              for stat in creative_stats:
                  creative_id = stat['creative']
                  if creative_id is not None:
                      Creative.objects.filter(pk=creative_id).update(
                          views=F('views') + stat['views_count'],
                          clicks=F('clicks') + stat['clicks_count']
                      )

              # Update line items
              for stat in line_item_stats:
                  line_item_id = stat['line_item']
                  if line_item_id is not None:
                      LineItem.objects.filter(pk=line_item_id).update(
                          views=F('views') + stat['views_count'],
                          clicks=F('clicks') + stat['clicks_count']
                      )

              # Delete the logs
              deleted_count, _ = old_logs.delete()

          self.stdout.write(self.style.SUCCESS(f"Successfully culled {deleted_count} logs."))
  ```

* [ ] **Step 4: Run the test to verify it passes**
  Run: `C:\Users\anton\miniconda3\envs\le-francais\python.exe manage.py test ads`
  Expected: PASS.

* [ ] **Step 5: Commit command**
  Run:
  ```powershell
  git add ads\management\commands\cull_logs.py ads\tests.py
  git commit -m "feat(ads): implement cull_logs command with atomic count accumulation"
  ```

---

### Task 4: Custom Combined Fields in Django Admin

**Files:**
* Modify: `ads\admin.py`
* Modify: `ads\tests.py`

**Interfaces:**
* Consumes: Model values for `views`, `clicks`, and active `Log` counts.
* Produces: Dynamically computed values displayed as `Combined Views` and `Combined Clicks` in list views and detail pages.

* [ ] **Step 1: Write the failing tests**
  Add verification in `ads\tests.py` checking that the admin helpers calculate the exact sums correctly under both situations (with and without active logs).

  ```python
  from ads.admin import LineItemAdmin, CreativeAdmin
  from django.contrib.admin.sites import AdminSite

  class AdminCombinedFieldsTestCase(TestCase):
      def setUp(self):
          self.site = AdminSite()
          self.line_item = LineItem.objects.create(name='Admin Test Line Item', views=100, clicks=10)
          self.creative = Creative.objects.create(name='Admin Test Creative', line_item=self.line_item, views=50, clicks=5)
          
          # Create active logs
          Log.objects.create(line_item=self.line_item, creative=self.creative, ip='127.0.0.1', clicked=True)
          Log.objects.create(line_item=self.line_item, creative=self.creative, ip='127.0.0.1', clicked=False)

      def test_admin_combined_fields(self):
          li_admin = LineItemAdmin(LineItem, self.site)
          cr_admin = CreativeAdmin(Creative, self.site)

          # LineItem combined counts:
          # Stored: views=100, clicks=10
          # Active logs: 2 views, 1 click
          self.assertEqual(li_admin.combined_views(self.line_item), 102)
          self.assertEqual(li_admin.combined_clicks(self.line_item), 11)

          # Creative combined counts:
          # Stored: views=50, clicks=5
          # Active logs: 2 views, 1 click
          self.assertEqual(cr_admin.combined_views(self.creative), 52)
          self.assertEqual(cr_admin.combined_clicks(self.creative), 6)
  ```

* [ ] **Step 2: Run the test to verify it fails**
  Run: `C:\Users\anton\miniconda3\envs\le-francais\python.exe manage.py test ads`
  Expected: FAIL (combined methods are missing from admin classes).

* [ ] **Step 3: Update `ads\admin.py` to add combined fields and adjust displays**
  Modify `CreativeInline` (lines 12-16) to include `combined_views` and `combined_clicks` in `readonly_fields`:
  ```python
  class CreativeInline(admin.TabularInline):
      model = Creative
      fk_name = 'line_item'
      extra = 0
      readonly_fields = ['combined_views', 'combined_clicks', 'views', 'clicks']
  ```

  Modify `LineItemAdmin` to:
  * Register `combined_views` and `combined_clicks` under `readonly_fields` and `fields`.
  * Define `combined_views` and `combined_clicks` methods.
  ```python
  @admin.register(LineItem)
  class LineItemAdmin(admin.ModelAdmin):
      form = GeoAdder
      readonly_fields = ['combined_views', 'combined_clicks', 'views', 'clicks']
      inlines = [CreativeInline]
      fields = [
          'name', 'priority', 'placements', 'placements_inverted',
          'placements_and', 'placements_and_inverted',
          'ad_units',
          'do_not_show_to',
          'less_than_n_days_ago',
          'less_than_n_days_ago_value',
          'do_not_show_if_was_on_conjugations',
          'combined_views',
          'combined_clicks',
          'views',
          'clicks',
          'capping_day',
          'capping_week',
          'capping_month',
          'do_not_display_to_registered_users',
          'do_not_display_to_anonymous_users',
          'labels',
          'disable', 'utm_campaign', 'utm_medium',
          'do_not_display_to_donating_users',
          'do_not_display_to_donating_users_days_ago',
          'display_to_paying_users',
          'do_not_display_to_paying_users',
          'targeting_countries',
          'targeting_cities',
          'targeting_invert',
      ]

      def combined_views(self, obj):
          current_logs = Log.objects.filter(line_item=obj).count()
          return obj.views + current_logs
      combined_views.short_description = 'Combined Views'

      def combined_clicks(self, obj):
          current_clicks = Log.objects.filter(line_item=obj, clicked=True).count()
          return obj.clicks + current_clicks
      combined_clicks.short_description = 'Combined Clicks'
  ```

  Modify `CreativeAdmin` to show combined fields in list display and edit detail view:
  ```python
  @admin.register(Creative)
  class CreativeAdmin(admin.ModelAdmin):
      list_display = ['name', 'line_item', 'combined_views', 'combined_clicks', 'views', 'clicks']
      readonly_fields = ['combined_views', 'combined_clicks', 'views', 'clicks']
      fields = [
          'name', 'utm_campaign', 'utm_medium', 'utm_source',
          'image_click_through_url', 'image', 'image_url', 'html', 'iframe',
          'line_item', 'disable', 'combined_views', 'combined_clicks', 'views', 'clicks',
          'labels', 'fluid', 'priority'
      ]

      def combined_views(self, obj):
          current_logs = Log.objects.filter(creative=obj).count()
          return obj.views + current_logs
      combined_views.short_description = 'Combined Views'

      def combined_clicks(self, obj):
          current_clicks = Log.objects.filter(creative=obj, clicked=True).count()
          return obj.clicks + current_clicks
      combined_clicks.short_description = 'Combined Clicks'
  ```

* [ ] **Step 4: Run the tests to verify they pass**
  Run: `C:\Users\anton\miniconda3\envs\le-francais\python.exe manage.py test ads`
  Expected: PASS.

* [ ] **Step 5: Commit changes**
  Run:
  ```powershell
  git add ads\admin.py ads\tests.py
  git commit -m "feat(ads): add combined live/historical views and clicks in Django admin"
  ```

---

### Task 5: End-to-End Verification

**Files:**
* Modify: `ads\tests.py`

**Interfaces:**
* Consumes: Full codebase integrations.
* Produces: Verified feature readiness with 100% test passing stats.

* [ ] **Step 1: Write exhaustive tests inside `ads\tests.py`**
  Consolidate and write a comprehensive suite in `ads\tests.py` that fully verifies live request simulation, log creation, data culling, total increments, database atomicity, and correct reverse migrations (mock-tested if needed).

* [ ] **Step 2: Run the full test suite**
  Run: `C:\Users\anton\miniconda3\envs\le-francais\python.exe manage.py test ads`
  Expected: All tests pass perfectly.

* [ ] **Step 3: Run Django system check**
  Run: `C:\Users\anton\miniconda3\envs\le-francais\python.exe manage.py check`
  Expected: No system errors or issues related to modified files.

* [ ] **Step 4: Commit and finalize**
  Run:
  ```powershell
  git add ads\tests.py
  git commit -m "test(ads): complete integration and end-to-end verification for log culling feature"
  ```
