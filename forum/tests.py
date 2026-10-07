# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from io import BytesIO
from PIL import Image

from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model

from forum.models import ForumAttachment, PostReply, ForumUserPreference, PostReaction
from forum.attachment_utils import process_uploaded_image, link_attachments_to_post
from forum.markup_engines import CustomMarkdownParser
from forum.reactions import (
    get_reaction, get_all_reactions, render_reaction_icon_html,
    prefetch_posts_reactions, get_post_reactions_summary, DEFAULT_REACTION
)
from forum.utils import (
    extract_quoted_and_mentioned_names,
    get_quoted_and_mentioned_users
)
from home.forms import AorPostForm, AORProfileForm
from notifications.models import Notification, clean_post
from pybb import util as pybb_util
from pybb.models import Forum, Category, Topic, Post, Profile


User = get_user_model()


class ForumAttachmentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testforumuser@example.com', username='testforumuser', password='password123')
        pybb_util.get_pybb_profile(self.user)
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

    def test_keystroke_variations(self):
        # 1. Unquoted key name
        html_unquoted = self.parser.format('++asdf++')
        self.assertIn('<kbd', html_unquoted)
        self.assertIn('asdf</kbd>', html_unquoted)

        # 2. Cyrillic unquoted key name
        html_cyrillic = self.parser.format('++пробел++')
        self.assertIn('<kbd', html_cyrillic)
        self.assertIn('пробел</kbd>', html_cyrillic)

        # 3. Cyrillic key with space
        html_cyrillic_space = self.parser.format('++тестовая клавиша++')
        self.assertIn('<kbd', html_cyrillic_space)
        self.assertIn('тестовая клавиша</kbd>', html_cyrillic_space)

        # 4. Multi-key shortcut
        html_shortcut = self.parser.format('++ctrl+c++')
        self.assertIn('<kbd', html_shortcut)
        self.assertIn('Ctrl', html_shortcut)
        self.assertIn('C', html_shortcut)

        # 5. Quoted key name
        html_quoted = self.parser.format('++"Enter / Return"++')
        self.assertIn('<kbd', html_quoted)
        self.assertIn('Enter / Return</kbd>', html_quoted)

    def test_spoiler_formatting(self):
        md = '???- "Мой секрет"\n    Скрытый текст'
        html = self.parser.format(md)
        self.assertIn('<details', html)
        self.assertIn('<summary>Мой секрет</summary>', html)
        self.assertIn('Скрытый текст', html)

    def test_emoji_formatting(self):
        html = self.parser.format(':heart:')
        self.assertTrue('<img' in html or '❤️' in html or 'emojione' in html)

    def test_quote_formatting(self):
        # Quote with username
        quote_with_user = self.parser.quote('Привет мир!', username='Иван')
        self.assertIn('> **Иван**:\n> Привет мир!\n\n', quote_with_user)

        # Quote without username
        quote_no_user = self.parser.quote('Текст цитаты')
        self.assertIn('> Текст цитаты\n\n', quote_no_user)

        # Multiline quote
        multiline = self.parser.quote('Строка 1\nСтрока 2', username='Анна')
        self.assertIn('> **Анна**:\n> Строка 1\n> Строка 2\n\n', multiline)


class AorPostFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='author@example.com', username='author', password='password123')
        pybb_util.get_pybb_profile(self.user)
        self.category = Category.objects.create(name='Test Category')
        self.forum = Forum.objects.create(category=self.category, name='Test Forum')
        self.topic = Topic.objects.create(forum=self.forum, name='Test Topic', user=self.user)
        self.post = Post.objects.create(topic=self.topic, user=self.user, body='Original topic starter post')

    def test_form_initialization_widget_and_attributes(self):
        form = AorPostForm(user=self.user, topic=self.topic)
        self.assertFalse(form.use_required_attribute)
        self.assertEqual(form.fields['body'].widget.__class__.__name__, 'Textarea')
        self.assertIn('forum-markdown-textarea', form.fields['body'].widget.attrs['class'])
        self.assertNotIn('required', form.fields['body'].widget.attrs)
        self.assertNotIn('markitup', str(form.media))

    def test_form_reply_to_post_initial(self):
        form = AorPostForm(user=self.user, topic=self.topic, initial={'reply_to_post': self.post.pk})
        self.assertEqual(form.fields['reply_to_post'].initial, self.post.pk)

    def test_form_save_creates_post_reply(self):
        form = AorPostForm(user=self.user, topic=self.topic, data={
            'body': 'Ответ на исходное сообщение',
            'reply_to_post': self.post.pk,
        })
        self.assertTrue(form.is_valid())
        new_post, _ = form.save(commit=True)
        self.assertTrue(PostReply.objects.filter(post=new_post, reply_to=self.post).exists())

    def test_form_save_links_forum_attachments(self):
        im = Image.new('RGB', (400, 300), color=(100, 150, 200))
        bio = BytesIO()
        im.save(bio, format='JPEG')
        bio.seek(0)
        upload = SimpleUploadedFile('image_for_post.jpg', bio.read(), content_type='image/jpeg')
        attachment = process_uploaded_image(upload, self.user)
        self.assertIsNone(attachment.post)

        form = AorPostForm(user=self.user, topic=self.topic, data={
            'body': 'Текст с картинкой: ![{}]({})'.format(attachment.filename, attachment.file.url),
        })
        self.assertTrue(form.is_valid())
        new_post, _ = form.save(commit=True)

        attachment.refresh_from_db()
        self.assertEqual(attachment.post, new_post)


class AorProfileFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='prefuser@example.com', username='prefuser', password='password123')
        self.profile = pybb_util.get_pybb_profile(self.user)

    def test_profile_form_initial_and_save_preferences(self):
        # Initial preference setting
        pref = ForumUserPreference.objects.create(user=self.user, email_on_reply=False)
        form = AORProfileForm(instance=self.profile)
        self.assertFalse(form.fields['email_on_reply'].initial)

        # Update preference to True via form save
        form2 = AORProfileForm(instance=self.profile, data={
            'email_on_reply': True,
            'autosubscribe': True,
            'receive_emails': True,
            'show_signatures': True,
            'time_zone': 3.0,
            'language': 'ru',
        })
        self.assertTrue(form2.is_valid())
        form2.save(commit=True)

        pref.refresh_from_db()
        self.assertTrue(pref.email_on_reply)


class PostReactionTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='author1@example.com', username='author1', password='password123')
        pybb_util.get_pybb_profile(self.user1)
        self.user2 = User.objects.create_user(email='author2@example.com', username='author2', password='password123')
        pybb_util.get_pybb_profile(self.user2)

        self.category = Category.objects.create(name='Test Category')
        self.forum = Forum.objects.create(category=self.category, name='Test Forum')
        self.topic = Topic.objects.create(forum=self.forum, name='Test Topic', user=self.user1)
        self.post = Post.objects.create(topic=self.topic, user=self.user1, body='Check out this post')
        self.client = Client()

    def test_reaction_registry_and_rendering(self):
        self.assertIsNotNone(get_reaction('heart'))
        self.assertIsNotNone(get_reaction('beret'))
        self.assertIsNone(get_reaction('nonexistent_reaction'))
        self.assertEqual(DEFAULT_REACTION, 'heart')

        all_rx = get_all_reactions()
        self.assertGreaterEqual(len(all_rx), 7)

        # SVG render for custom 'beret'
        beret_html = render_reaction_icon_html('beret')
        self.assertIn('<svg', beret_html)
        self.assertIn('reaction-beret-icon', beret_html)

        # Emoji render for standard emoji reaction
        heart_html = render_reaction_icon_html('heart')
        self.assertIn('<span class="reaction-emoji', heart_html)
        self.assertIn('❤️', heart_html)

    def test_post_react_ajax_unauthenticated(self):
        react_url = reverse('forum:react_post', args=[self.post.pk])
        resp = self.client.post(react_url, {'reaction': 'heart'})
        self.assertEqual(resp.status_code, 401)

    def test_post_react_ajax_invalid_post(self):
        self.client.force_login(self.user2)
        react_url = reverse('forum:react_post', args=[999999])
        resp = self.client.post(react_url, {'reaction': 'heart'})
        self.assertEqual(resp.status_code, 404)

    def test_post_react_ajax_invalid_reaction(self):
        self.client.force_login(self.user2)
        react_url = reverse('forum:react_post', args=[self.post.pk])
        resp = self.client.post(react_url, {'reaction': 'unknown_reaction_code'})
        self.assertEqual(resp.status_code, 400)

    def test_post_react_ajax_add_and_toggle(self):
        self.client.force_login(self.user2)
        react_url = reverse('forum:react_post', args=[self.post.pk])

        # 1. Add 'heart' reaction
        resp1 = self.client.post(react_url, {'reaction': 'heart'})
        self.assertEqual(resp1.status_code, 200)
        data1 = resp1.json()
        self.assertEqual(data1['status'], 'ok')
        self.assertEqual(data1['user_reaction'], 'heart')
        self.assertEqual(data1['total_count'], 1)
        self.assertTrue(PostReaction.objects.filter(post=self.post, user=self.user2, active=True).exists())

        # 2. Toggle 'heart' reaction off
        resp2 = self.client.post(react_url, {'reaction': 'heart'})
        self.assertEqual(resp2.status_code, 200)
        data2 = resp2.json()
        self.assertEqual(data2['status'], 'ok')
        self.assertIsNone(data2['user_reaction'])
        self.assertEqual(data2['total_count'], 0)
        self.assertFalse(PostReaction.objects.filter(post=self.post, user=self.user2, active=True).exists())

    def test_post_react_ajax_switch_reaction(self):
        self.client.force_login(self.user2)
        react_url = reverse('forum:react_post', args=[self.post.pk])

        # Add 'heart'
        self.client.post(react_url, {'reaction': 'heart'})

        # Switch to 'like'
        resp = self.client.post(react_url, {'reaction': 'like'})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['user_reaction'], 'like')
        self.assertEqual(data['total_count'], 1)

        rx = PostReaction.objects.get(post=self.post, user=self.user2)
        self.assertEqual(rx.reaction_type, 'like')
        self.assertTrue(rx.active)

    def test_post_reaction_users_ajax(self):
        PostReaction.objects.create(post=self.post, user=self.user1, reaction_type='heart', active=True)
        PostReaction.objects.create(post=self.post, user=self.user2, reaction_type='beret', active=True)

        users_url = reverse('forum:post_reactions', args=[self.post.pk])
        resp = self.client.get(users_url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['total_count'], 2)

        codes = [item['code'] for item in data['summary']]
        self.assertIn('heart', codes)
        self.assertIn('beret', codes)

    def test_prefetch_posts_reactions(self):
        PostReaction.objects.create(post=self.post, user=self.user2, reaction_type='fire', active=True)
        prefetch_posts_reactions([self.post])

        self.assertTrue(hasattr(self.post, '_prefetched_reactions'))
        self.assertEqual(len(self.post._prefetched_reactions), 1)

        summary = get_post_reactions_summary(self.post, current_user=self.user2)
        self.assertEqual(summary['total_count'], 1)
        self.assertEqual(summary['user_reaction'], 'fire')


class ForumNotificationTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1@example.com', username='user1', password='password123')
        pybb_util.get_pybb_profile(self.user1)
        self.user2 = User.objects.create_user(email='user2@example.com', username='user2', password='password123')
        pybb_util.get_pybb_profile(self.user2)
        self.user3 = User.objects.create_user(email='user3@example.com', username='user3', password='password123')
        pybb_util.get_pybb_profile(self.user3)

        self.category = Category.objects.create(name='Test Category')
        self.forum = Forum.objects.create(category=self.category, name='Test Forum')
        self.topic = Topic.objects.create(forum=self.forum, name='Notification Topic', user=self.user1)
        self.post1 = Post.objects.create(topic=self.topic, user=self.user1, body='First root post in thread')

    def test_clean_post_normal(self):
        post_text = '> Quote line 1\n> Quote line 2\nActual answer body to the author'
        cleaned = clean_post(post_text)
        self.assertIn('Actual answer body', cleaned)
        self.assertNotIn('Quote line 1', cleaned)

    def test_clean_post_quote_only(self):
        # Quote-only post must not produce an empty string
        post_text = '> Quoted text only without other text'
        cleaned = clean_post(post_text)
        self.assertTrue(len(cleaned) > 0)
        self.assertIn('Quoted text only without other text', cleaned)

    def test_clean_post_truncation(self):
        long_text = 'A' * 100
        cleaned = clean_post(long_text)
        self.assertTrue(cleaned.endswith('...'))
        self.assertLessEqual(len(cleaned), 55)

    def test_extract_quoted_and_mentioned_names(self):
        text = '> **user1**:\n> Quoted greeting\n\n**user2**, check this out! And @user3 please review.'
        quoted, mentioned = extract_quoted_and_mentioned_names(text)
        self.assertEqual(quoted, {'user1'})
        self.assertEqual(mentioned, {'user2', 'user3'})

    def test_extract_cyrillic_quoted_and_mentioned_names(self):
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

    def test_extract_quoted_and_mentioned_deduplication(self):
        # If user is quoted, they should not get a duplicate mention notification
        text = '> **user1**:\n> Quoted greeting\n\n**user1**, follow up comment!'
        quoted, mentioned = extract_quoted_and_mentioned_names(text)
        self.assertEqual(quoted, {'user1'})
        self.assertEqual(mentioned, set())

    def test_get_quoted_and_mentioned_users(self):
        text = '> **user1**:\n> Quote\n\n**user2**, note this'
        q_users, m_users = get_quoted_and_mentioned_users(text, exclude_user_ids=[self.user1.id])
        self.assertEqual(len(q_users), 0)  # Excluded user1
        self.assertEqual(len(m_users), 1)
        self.assertEqual(m_users[0].username, 'user2')

    def test_direct_reply_and_quote_notifications(self):
        # Direct reply to post1
        reply_post = Post(
            topic=self.topic,
            user=self.user2,
            body='> **user3**:\n> Some quote from user3\n\nDirect reply to user1'
        )
        reply_post._reply_to_id = self.post1.id
        reply_post.save()

        # Check in-app bell notification for user1 (direct reply recipient)
        notif_reply = Notification.objects.filter(
            notificationuser__user=self.user1,
            category=Notification.REPLYES
        ).last()
        self.assertIsNotNone(notif_reply)
        self.assertTrue(notif_reply.data.get('is_reply_to_you'))

        # Check in-app bell notification for user3 (quoted author)
        notif_quote = Notification.objects.filter(
            notificationuser__user=self.user3,
            category=Notification.REPLYES
        ).last()
        self.assertIsNotNone(notif_quote)
        self.assertTrue(notif_quote.data.get('is_quote'))

    def test_post_reaction_notification_creation(self):
        # Reaction on post1 by user2
        rx = PostReaction.objects.create(
            post=self.post1,
            user=self.user2,
            reaction_type='heart',
            active=True
        )

        notif = Notification.objects.filter(
            notificationuser__user=self.user1,
            category=Notification.LIKES
        ).last()
        self.assertIsNotNone(notif)
        self.assertEqual(notif.data.get('reaction_type'), 'heart')
        self.assertEqual(notif.data.get('reaction_label'), 'Сердечко')
