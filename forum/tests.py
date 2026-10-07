# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from io import BytesIO
from PIL import Image

from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

from forum.models import ForumAttachment
from forum.attachment_utils import process_uploaded_image, link_attachments_to_post
from forum.markup_engines import CustomMarkdownParser
from pybb.models import Forum, Category, Topic, Post


User = get_user_model()


class ForumAttachmentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testforumuser@example.com', username='testforumuser', password='password123')
        self.client = Client()


    def create_test_image(self, width=800, height=600, fmt='JPEG'):
        im = Image.new('RGB', (width, height), color=(120, 160, 200))
        bio = BytesIO()
        im.save(bio, format=fmt)
        bio.seek(0)
        return bio.read()

    def test_process_uploaded_image_resizing_and_compression(self):
        # 2000x1500 image should be resized down to max 1400px
        raw_data = self.create_test_image(width=2000, height=1500)
        upload = SimpleUploadedFile('sample_large.jpg', raw_data, content_type='image/jpeg')

        attachment = process_uploaded_image(upload, self.user)
        self.assertEqual(attachment.user, self.user)
        self.assertEqual(attachment.filename, 'sample_large.jpg')
        self.assertLessEqual(attachment.width, 1400)
        self.assertLessEqual(attachment.height, 1400)
        self.assertLessEqual(attachment.file_size, 1024 * 1024)
        self.assertTrue(attachment.file.url.startswith('http') or attachment.file.url.startswith('/'))

    def test_process_uploaded_image_invalid_format(self):
        fake_upload = SimpleUploadedFile('bad.txt', b'Hello not an image', content_type='text/plain')
        with self.assertRaises(ValueError):
            process_uploaded_image(fake_upload, self.user)

    def test_upload_image_ajax_view(self):
        upload_url = reverse('forum:upload_image')

        # 1. Anonymous request
        raw_data = self.create_test_image(width=400, height=300)
        upload = SimpleUploadedFile('photo.jpg', raw_data, content_type='image/jpeg')
        resp = self.client.post(upload_url, {'file': upload})
        self.assertEqual(resp.status_code, 401)

        # 2. Authenticated request
        self.client.force_login(self.user)
        upload2 = SimpleUploadedFile('photo.jpg', raw_data, content_type='image/jpeg')
        resp2 = self.client.post(upload_url, {'file': upload2})
        self.assertEqual(resp2.status_code, 200)
        data = resp2.json()
        self.assertTrue(data['success'])
        self.assertIn('url', data)
        self.assertEqual(data['filename'], 'photo.jpg')
        self.assertGreater(data['size'], 0)

        # 3. Oversized file (> 10MB)
        huge_data = b'0' * (11 * 1024 * 1024)
        huge_upload = SimpleUploadedFile('huge.jpg', huge_data, content_type='image/jpeg')
        resp3 = self.client.post(upload_url, {'file': huge_upload})
        self.assertEqual(resp3.status_code, 400)
        self.assertFalse(resp3.json()['success'])

    def test_link_attachments_to_post(self):
        category = Category.objects.create(name='Test Category')
        forum = Forum.objects.create(category=category, name='Test Forum')
        topic = Topic.objects.create(forum=forum, name='Test Topic', user=self.user)

        raw_data = self.create_test_image(width=300, height=200)
        upload = SimpleUploadedFile('linked_photo.jpg', raw_data, content_type='image/jpeg')
        attachment = process_uploaded_image(upload, self.user)
        self.assertIsNone(attachment.post)

        post = Post.objects.create(
            topic=topic,
            user=self.user,
            body='See attachment: ![{}]({})'.format(attachment.filename, attachment.file.url)
        )
        link_attachments_to_post(post, post.body)
        attachment.refresh_from_db()
        self.assertEqual(attachment.post, post)


class CustomMarkdownParserTests(TestCase):
    def setUp(self):
        self.parser = CustomMarkdownParser()

    def test_formatting_features(self):
        md = '^^подчеркивание^^ ~~зачеркивание~~ ==маркер== 3^ème^ C~2~H~5~OH ++ctrl+c++'
        html = self.parser.format(md)
        self.assertIn('<ins>подчеркивание</ins>', html)
        self.assertIn('<del>зачеркивание</del>', html)
        self.assertIn('<mark>маркер</mark>', html)
        self.assertIn('<sup>ème</sup>', html)
        self.assertIn('<sub>2</sub>', html)
        self.assertIn('<kbd', html)

    def test_spoiler_formatting(self):
        md = '???- "Мой секрет"\n    Скрытый текст'
        html = self.parser.format(md)
        self.assertIn('<details', html)
        self.assertIn('<summary>Мой секрет</summary>', html)
        self.assertIn('Скрытый текст', html)
