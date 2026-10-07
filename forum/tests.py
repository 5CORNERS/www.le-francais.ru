# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from io import BytesIO
from PIL import Image

from django.core import mail
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model

from forum.models import ForumAttachment, ForumUserPreference
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

    def test_post_save_signal_links_attachment_automatically(self):
        category = Category.objects.create(name='Signal Test Category')
        forum = Forum.objects.create(category=category, name='Signal Test Forum')
        topic = Topic.objects.create(forum=forum, name='Signal Test Topic', user=self.user)

        raw_data = self.create_test_image(width=300, height=200)
        attachment = ForumAttachment(
            user=self.user,
            filename='auto_linked.jpg',
            file_size=len(raw_data),
        )
        attachment.file.save('auto_linked.jpg', ContentFile(raw_data), save=True)
        self.assertIsNone(attachment.post)

        post = Post.objects.create(
            topic=topic,
            user=self.user,
            body='Look at this: ![{}]({})'.format(attachment.filename, attachment.file.url)
        )
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


class PostReactionViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='reaction_user', email='react@example.com', password='password')
        category = Category.objects.create(name='Test Category')
        forum = Forum.objects.create(name='React Forum', category=category)
        topic = Topic.objects.create(forum=forum, name='React Topic', user=self.user)
        self.post = Post.objects.create(topic=topic, user=self.user, body='React to this')

    def test_toggle_reaction_ajax(self):
        self.client.login(username='reaction_user', password='password')
        url = reverse('forum:react_post', kwargs={'pk': self.post.pk})
        
        # Add reaction
        resp1 = self.client.post(url, {'reaction': 'fire'})
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp1.json()['user_reaction'], 'fire')

        # Toggle reaction off
        resp2 = self.client.post(url, {'reaction': 'fire'})
        self.assertEqual(resp2.status_code, 200)
        self.assertIsNone(resp2.json()['user_reaction'])


class ForumUtilTestCase(TestCase):
    def test_extract_cyrillic_quoted_and_mentioned_names(self):
        from forum.utils import extract_quoted_and_mentioned_names
        text = (
            "> **Алексей Линецкий**:\n> Привет!\n\n"
            "**Fatma Ametova**, посмотри на это:\n"
            "А также спросим @Иван и @Jean_Valjean."
        )
        quoted, mentioned = extract_quoted_and_mentioned_names(text)
        self.assertIn('Алексей Линецкий', quoted)
        self.assertIn('Fatma Ametova', mentioned)
        self.assertIn('Иван', mentioned)
        self.assertIn('Jean_Valjean', mentioned)


class ForumFormattingTestCase(TestCase):
    def setUp(self):
        self.parser = CustomMarkdownParser()

    def test_ordered_list_and_bullet_list_formatting(self):
        html1 = self.parser.format("1. First item\n2. Second item")
        html2 = self.parser.format("* Bullet item 1\n* Bullet item 2")
        self.assertIn('<ol>', html1)
        self.assertIn('<ul>', html2)
        self.assertNotIn('<em> Bullet item 1</em>', html2)


@override_settings(
    MAILER_EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    MAILER_EMAIL_THROTTLE=0,
    PYBB_USE_DJANGO_MAILER=True
)
class ForumEmailNotificationTestCase(TestCase):
    def setUp(self):
        from mailer.models import Message
        Message.objects.all().delete()
        self.user1 = User.objects.create_user(username='alice', email='alice@test.com', password='pw')
        self.user2 = User.objects.create_user(username='bob', email='bob@test.com', password='pw')
        self.user3 = User.objects.create_user(username='charlie', email='charlie@test.com', password='pw')

        self.category = Category.objects.create(name='Discussion Cat')
        self.forum = Forum.objects.create(category=self.category, name='Discussion', slug='discussion')
        self.topic = Topic.objects.create(forum=self.forum, name='General Topic', user=self.user1)
        self.first_post = Post.objects.create(topic=self.topic, user=self.user1, body='Initial post')

    def test_direct_reply_sends_email_to_recipient(self):
        from mailer.engine import send_all
        reply_post = Post(
            topic=self.topic,
            user=self.user2,
            body='**alice**, thank you!'
        )
        reply_post._reply_to_id = self.first_post.pk
        reply_post.save()
        send_all()

        # Check mail was sent to dummy outbox
        self.assertTrue(len(mail.outbox) >= 1)
        recipient_emails = [m.to[0] for m in mail.outbox]
        self.assertIn('alice@test.com', recipient_emails)
        self.assertNotIn('bob@test.com', recipient_emails)

    def test_opt_out_preference_prevents_email(self):
        from mailer.engine import send_all
        pref, _ = ForumUserPreference.objects.get_or_create(user=self.user1)
        pref.email_on_reply = False
        pref.save()

        reply_post = Post(
            topic=self.topic,
            user=self.user2,
            body='**alice**, ping!'
        )
        reply_post._reply_to_id = self.first_post.pk
        reply_post.save()
        send_all()

        # Alice should NOT receive email
        recipient_emails = [m.to[0] for m in mail.outbox]
        self.assertNotIn('alice@test.com', recipient_emails)

    def test_quote_email_notification(self):
        from mailer.engine import send_all
        quote_post = Post(
            topic=self.topic,
            user=self.user2,
            body='> **alice**:\n> Initial post\n\nI agree completely.'
        )
        quote_post.save()
        send_all()

        self.assertTrue(len(mail.outbox) >= 1)
        recipient_emails = [m.to[0] for m in mail.outbox]
        self.assertIn('alice@test.com', recipient_emails)

    def test_mention_email_notification_with_cyrillic(self):
        from mailer.engine import send_all
        cyrillic_user = User.objects.create_user(username='Дмитрий', email='dmitry@test.com', password='pw')
        post = Post(
            topic=self.topic,
            user=self.user1,
            body='Привет, @Дмитрий, как дела?'
        )
        post.save()
        send_all()

        self.assertTrue(len(mail.outbox) >= 1)
        recipient_emails = [m.to[0] for m in mail.outbox]
        self.assertIn('dmitry@test.com', recipient_emails)

    def test_subscriber_email_notification(self):
        from mailer.engine import send_all
        self.topic.subscribers.add(self.user3)

        post = Post(
            topic=self.topic,
            user=self.user2,
            body='Just a regular comment'
        )
        post.save()
        send_all()

        recipient_emails = [m.to[0] for m in mail.outbox]
        self.assertIn('charlie@test.com', recipient_emails)
        self.assertNotIn('bob@test.com', recipient_emails)



