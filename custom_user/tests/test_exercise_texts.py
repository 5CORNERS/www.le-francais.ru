# -*- coding: UTF-8 -*-
import json
import os
import shutil
import tempfile
from unittest.mock import patch

from django.test import TestCase, Client, override_settings
from django.urls import reverse

from custom_user.models import User
from custom_user.exercise_texts import (
    get_all_lessons_summary,
    get_lesson_exercises_data,
    save_exercise_text,
    save_exercise_texts_batch,
)


class ExerciseTextsUnitTests(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_all_lessons_summary(self):
        summary = get_all_lessons_summary()
        self.assertIsInstance(summary, list)
        if summary:
            first = summary[0]
            self.assertIn('lesson', first)
            self.assertIn('count', first)

    def test_get_lesson_exercises_data(self):
        summary = get_all_lessons_summary()
        if summary:
            first_lesson = summary[0]['lesson']
            exercises = get_lesson_exercises_data(first_lesson)
            self.assertIsInstance(exercises, list)
            if exercises:
                ex = exercises[0]
                self.assertIn('id', ex)
                self.assertIn('num_display', ex)
                self.assertIn('tasktext', ex)
                self.assertIn('helptext', ex)
                self.assertIn('feedback', ex)
                self.assertIn('titel', ex)
                self.assertIn('untertitel', ex)

    def test_save_exercise_text_logic(self):
        # Create a dummy app directory and index.html
        dummy_app_id = 'testapp123'
        dummy_app_dir = os.path.join(self.temp_dir, dummy_app_id)
        os.makedirs(dummy_app_dir, exist_ok=True)
        dummy_index = os.path.join(dummy_app_dir, 'index.html')

        initial_app_data = {
            'tasktext': 'Original Task',
            'helptext': 'Original Help',
            'feedback': 'Original Feedback',
            'initparameters': 'param1=val1&feedback=Original%20Feedback&param2=val2'
        }
        initial_html = (
            '<!DOCTYPE html><html><head>'
            '<script>var AppClientAppData = ' + json.dumps(initial_app_data) + ';</script>'
            '</head><body>Content</body></html>'
        )
        with open(dummy_index, 'w', encoding='utf-8') as f:
            f.write(initial_html)

        with patch('custom_user.exercise_texts.CACHE_APPS_DIR', self.temp_dir):
            with patch.dict(os.environ, {
                'SFTP_FILES_LE_FRANCAIS_HOSTNAME': '',
                'SFTP_FILES_LE_FRANCAIS_USERNAME': '',
                'SFTP_FILES_LE_FRANCAIS_PASSWORD': ''
            }):
                # Test updating tasktext
                res = save_exercise_text(dummy_app_id, 'tasktext', '<b>Updated Task</b>')
                self.assertEqual(res['status'], 'ok')

                with open(dummy_index, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.assertIn('<b>Updated Task</b>', content)

                # Test updating feedback (should update both top-level and initparameters)
                res = save_exercise_text(dummy_app_id, 'feedback', 'Super & Bien!')
                self.assertEqual(res['status'], 'ok')

                with open(dummy_index, 'r', encoding='utf-8') as f:
                    updated_content = f.read()
                self.assertIn('Super & Bien!', updated_content)
                self.assertIn('feedback=Super%20%26%20Bien%21', updated_content)

                # Test updating titel
                res = save_exercise_text(dummy_app_id, 'titel', '<b>Mots:</b> un, deux')
                self.assertEqual(res['status'], 'ok')
                with open(dummy_index, 'r', encoding='utf-8') as f:
                    updated_content2 = f.read()
                self.assertIn('titel=text|%3Cb%3EMots%3A%3C/b%3E%20un%2C%20deux|', updated_content2)

                # Test updating untertitel
                res = save_exercise_text(dummy_app_id, 'untertitel', 'Exemple: Je parle.')
                self.assertEqual(res['status'], 'ok')
                with open(dummy_index, 'r', encoding='utf-8') as f:
                    updated_content3 = f.read()
                self.assertIn('untertitel=text|Exemple%3A%20Je%20parle.|', updated_content3)

    def test_save_exercise_texts_batch_logic(self):
        # Create two dummy apps with index.html
        app1_id = 'testbatch1'
        app2_id = 'testbatch2'

        for app_id, task in [(app1_id, 'Task 1'), (app2_id, 'Task 2')]:
            app_dir = os.path.join(self.temp_dir, app_id)
            os.makedirs(app_dir, exist_ok=True)
            index_path = os.path.join(app_dir, 'index.html')
            app_data = {
                'tasktext': task,
                'feedback': 'Feedback',
                'initparameters': 'feedback=Feedback'
            }
            html = f'<!DOCTYPE html><html><head><script>var AppClientAppData = {json.dumps(app_data)};</script></head><body></body></html>'
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(html)

        with patch('custom_user.exercise_texts.CACHE_APPS_DIR', self.temp_dir):
            with patch.dict(os.environ, {
                'SFTP_FILES_LE_FRANCAIS_HOSTNAME': '',
                'SFTP_FILES_LE_FRANCAIS_USERNAME': '',
                'SFTP_FILES_LE_FRANCAIS_PASSWORD': ''
            }):
                batch_items = [
                    {'app_id': app1_id, 'field': 'tasktext', 'value': 'Updated Task 1'},
                    {'app_id': app1_id, 'field': 'feedback', 'value': 'Bravo 1!'},
                    {'app_id': app2_id, 'field': 'tasktext', 'value': 'Updated Task 2'},
                ]
                res = save_exercise_texts_batch(batch_items)
                self.assertEqual(res['status'], 'ok')
                self.assertEqual(res['saved_count'], 2)
                self.assertIn(app1_id, res['saved_app_ids'])
                self.assertIn(app2_id, res['saved_app_ids'])

                # Verify file contents
                with open(os.path.join(self.temp_dir, app1_id, 'index.html'), 'r', encoding='utf-8') as f:
                    c1 = f.read()
                self.assertIn('Updated Task 1', c1)
                self.assertIn('Bravo 1!', c1)

                with open(os.path.join(self.temp_dir, app2_id, 'index.html'), 'r', encoding='utf-8') as f:
                    c2 = f.read()
                self.assertIn('Updated Task 2', c2)


@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class ExerciseTextsViewTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='admin_staff',
            email='staff@example.com',
            password='password123',
            is_staff=True
        )
        self.normal_user = User.objects.create_user(
            username='normal_user',
            email='user@example.com',
            password='password123',
            is_staff=False
        )
        self.client = Client()

    def test_anonymous_access_redirects(self):
        url = reverse('custom_user:exercise_texts_editor')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)

    def test_normal_user_access_denied_or_redirects(self):
        self.client.force_login(self.normal_user)
        url = reverse('custom_user:exercise_texts_editor')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)

    def test_staff_user_access_editor(self):
        self.client.force_login(self.staff_user)
        url = reverse('custom_user:exercise_texts_editor')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Редактор текстов упражнений')

    def test_staff_user_json_format(self):
        self.client.force_login(self.staff_user)
        url = reverse('custom_user:exercise_texts_editor') + '?lesson=1&format=json'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content.decode('utf-8'))
        self.assertIn('lesson', data)
        self.assertIn('exercises', data)

    def test_save_endpoint_validation(self):
        self.client.force_login(self.staff_user)
        url = reverse('custom_user:exercise_texts_save')
        # Missing payload fields
        resp = self.client.post(url, json.dumps({}), content_type='application/json')
        self.assertEqual(resp.status_code, 400)

    def test_batch_save_endpoint(self):
        self.client.force_login(self.staff_user)
        url = reverse('custom_user:exercise_texts_save')
        with patch('custom_user.exercise_texts.save_exercise_texts_batch') as mock_batch:
            mock_batch.return_value = {'status': 'ok', 'saved_count': 1, 'sftp_synced': False}
            payload = {
                'items': [
                    {'app_id': 'app1', 'field': 'tasktext', 'value': 'New task'}
                ]
            }
            resp = self.client.post(url, json.dumps(payload), content_type='application/json')
            self.assertEqual(resp.status_code, 200)
            data = json.loads(resp.content.decode('utf-8'))
            self.assertEqual(data['status'], 'ok')
            self.assertEqual(data['saved_count'], 1)
            mock_batch.assert_called_once()
