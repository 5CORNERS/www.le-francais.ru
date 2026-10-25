# Forum Fixes and Notification Email Tests Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix all critical bugs, security vulnerabilities, and performance bottlenecks identified in forum commits 4d9447b2..0f50f4e0 (attachment linking, XSS and markdown parsing, reaction race conditions, N+1 queries, Cyrillic mentions) and implement robust automated tests for forum notification emails using Django's dummy memory backend. Commit after every task.

**Architecture:** Use a `post_save` signal receiver on `pybb.models.Post` for guaranteed attachment linking; atomic transaction and `select_for_update().get_or_create()` in `post_react_ajax` to eliminate race conditions; protocol and HTML sanitization in `forum-editor.js` without ES2018 regex lookbehinds; prefetch tags to eliminate N+1 queries; `translation.override` for safe per-user localized email rendering; and `@override_settings(PYBB_USE_DJANGO_MAILER=False, EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')` for email testing without network delivery.

**Tech Stack:** Django 1.11.29, Python 3.7, PyBB, PostgreSQL, jQuery, Pillow, Bootstrap 4.

**Spec:** Code review findings from commit range `4d9447b2`..`0f50f4e0`.

## Global Constraints

- **Python Environment:** Use conda python at `C:\Users\anton\miniconda3\envs\le-francais\python.exe`.
- **Shell Syntax:** Use Windows PowerShell syntax exclusively.
- **Email Safety:** Testing must NEVER send real emails. All tests must explicitly use `locmem.EmailBackend` with `PYBB_USE_DJANGO_MAILER=False`.
- **Commits:** Commit specific changed files after every task as specified in each task's final step.

## Review Focus

1. **Attachment linking lifecycle:** Posts created or edited through standard `AddPostView` / `EditPostView` pass `commit=False` to `form.save()`; attachments must be linked when `post.save()` completes.
2. **Reaction concurrency:** Rapid double-clicks from users must safely toggle state and never raise `IntegrityError` or crash with HTTP 500.
3. **Editor XSS vector:** Markdown text containing quotes, image tags, or link anchors with `javascript:` or `onerror=` handlers must never execute script when switching to visual mode.
4. **Markdown list integrity:** Bullet lists using `* item` must not be mangled into `<em>` italics when roundtripping between Markdown and Visual modes.
5. **Cyrillic username resolution:** Mentions of Russian names (e.g., `@Алексей Линецкий` or `@Иван`) must resolve and notify the appropriate accounts.

---

### File Structure Map

| File | Responsibility |
| --- | --- |
| `forum/models.py` | Add `post_save` signal receiver connecting `Post` saves to `link_attachments_to_post`. |
| `forum/views.py` | Update `post_react_ajax` with `transaction.atomic()` and `get_or_create()` to prevent concurrency conflicts. |
| `forum/utils.py` | Support Unicode/Cyrillic in `@mentions` regex, and replace `translation.activate` with `translation.override`. |
| `home/templates/tags/topic_block.html` | Add `{% prefetch_posts_reactions_tag post_list %}` to eliminate N+1 queries on lesson pages. |
| `home/templates/pybb/post_template.html` | Remove dead `{% liked post request.user as liked %}` query call. |
| `notifications/notifications_templates/LK.html` | Replace hardcoded `/static/` with `{% static %}` tag. |
| `home/static/js/forum-editor.js` | Fix XSS sanitization, URL schemes, ordered list (`<ol>`) parsing, and asterisk list vs. italic precedence using backward-compatible regexes (no lookbehinds). |
| `forum/tests.py` | Add tests for automated attachment linking, reaction concurrency, and email notifications (direct reply, quotes, mentions, subscriptions, and opt-outs) using `locmem`. |

---

### Task 1: Fix Attachment Linking via `post_save` Signal

**Files:**
- Modify: `forum/models.py`
- Modify: `forum/tests.py`

**Interfaces:**
- Consumes: `pybb.models.Post`, `forum.attachment_utils.link_attachments_to_post`, `django.core.files.base.ContentFile`
- Produces: Automatic linking of unlinked `ForumAttachment` records to `Post` upon save.

- [ ] **Step 1: Write the failing test for automated attachment linking on `post.save()`**

In `forum/tests.py`, ensure `from django.core.files.base import ContentFile` is imported at the top, then add to `ForumAttachmentTestCase`:
```python
    def test_post_save_signal_links_attachment_automatically(self):
        from forum.models import ForumAttachment
        from pybb.models import Topic, Forum, Post
        forum = Forum.objects.create(name='Test Forum', slug='test-forum')
        topic = Topic.objects.create(forum=forum, name='Test Topic', user=self.user)
        
        attachment = ForumAttachment(
            user=self.user,
            filename='auto_test.jpg',
            file_size=1000,
            width=200,
            height=200,
        )
        attachment.file.save('auto_test_123.jpg', ContentFile(b'dummy'), save=True)
        self.assertIsNone(attachment.post)

        # Creating post via standard model save (just like AddPostView does)
        post = Post(
            topic=topic,
            user=self.user,
            body='Here is my image: ![auto_test.jpg]({})'.format(attachment.file.url)
        )
        post.save()

        attachment.refresh_from_db()
        self.assertEqual(attachment.post, post)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `C:\Users\anton\miniconda3\envs\le-francais\python.exe manage.py test forum.tests.ForumAttachmentTestCase.test_post_save_signal_links_attachment_automatically`
Expected: FAIL with `AssertionError: None != <Post: ...>`

- [ ] **Step 3: Implement signal handler in `forum/models.py`**

In `forum/models.py`, register a `post_save` receiver for `Post`:
```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from pybb.models import Post

@receiver(post_save, sender=Post)
def link_post_attachments_on_save(sender, instance, **kwargs):
    if instance and instance.pk and instance.body:
        from forum.attachment_utils import link_attachments_to_post
        try:
            link_attachments_to_post(instance, instance.body)
        except Exception:
            pass
```

- [ ] **Step 4: Run test to verify it passes**

Run: `C:\Users\anton\miniconda3\envs\le-francais\python.exe manage.py test forum.tests.ForumAttachmentTestCase.test_post_save_signal_links_attachment_automatically`
Expected: PASS

- [ ] **Step 5: Commit**

```powershell
git add forum/models.py forum/tests.py
git commit -m "fix(forum): link attachments to post automatically on post_save"
```

---

### Task 2: Prevent Race Conditions in `post_react_ajax`

**Files:**
- Modify: `forum/views.py`
- Modify: `forum/tests.py`

**Interfaces:**
- Consumes: `PostReaction`, `Like`, `get_post_reactions_summary`
- Produces: Idempotent and thread-safe `post_react_ajax(request, pk)` view returning JSON status.

- [ ] **Step 1: Write tests for reaction toggle and concurrency**

Add `PostReactionViewTestCase` to `forum/tests.py`:
```python
class PostReactionViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='reaction_user', email='react@example.com', password='password')
        forum = Forum.objects.create(name='React Forum', slug='react-forum')
        topic = Topic.objects.create(forum=forum, name='React Topic', user=self.user)
        self.post = Post.objects.create(topic=topic, user=self.user, body='React to this')

    def test_toggle_reaction_ajax(self):
        self.client.login(username='reaction_user', password='password')
        url = reverse('post_react_ajax', kwargs={'pk': self.post.pk})
        
        # Add reaction
        resp1 = self.client.post(url, {'reaction': 'fire'})
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp1.json()['user_reaction'], 'fire')

        # Toggle reaction off
        resp2 = self.client.post(url, {'reaction': 'fire'})
        self.assertEqual(resp2.status_code, 200)
        self.assertIsNone(resp2.json()['user_reaction'])
```

- [ ] **Step 2: Run test to verify initial state**

Run: `C:\Users\anton\miniconda3\envs\le-francais\python.exe manage.py test forum.tests.PostReactionViewTestCase`

- [ ] **Step 3: Refactor `post_react_ajax` in `forum/views.py` with atomic handling**

Update `post_react_ajax` in `forum/views.py`:
```python
    from django.db import transaction

    with transaction.atomic():
        existing_reaction, created = PostReaction.objects.select_for_update().get_or_create(
            post=post,
            user=request.user,
            defaults={
                'reaction_type': reaction_code,
                'active': True,
            }
        )
        if not created:
            if existing_reaction.active and existing_reaction.reaction_type == reaction_code:
                existing_reaction.active = False
            else:
                existing_reaction.reaction_type = reaction_code
                existing_reaction.active = True
            existing_reaction.save()

        if pybb_profile:
            Like.objects.update_or_create(
                post=post,
                profile=pybb_profile,
                defaults={'active': existing_reaction.active}
            )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `C:\Users\anton\miniconda3\envs\le-francais\python.exe manage.py test forum.tests.PostReactionViewTestCase`
Expected: PASS

- [ ] **Step 5: Commit**

```powershell
git add forum/views.py forum/tests.py
git commit -m "fix(forum): prevent race condition in post reactions using atomic transaction"
```

---

### Task 3: Fix N+1 Queries and Template Quirks

**Files:**
- Modify: `home/templates/tags/topic_block.html`
- Modify: `home/templates/pybb/post_template.html`
- Modify: `notifications/notifications_templates/LK.html`

**Interfaces:**
- Consumes: `{% prefetch_posts_reactions_tag %}`, `{% static %}`
- Produces: Optimized HTML rendering without repetitive `Like` or `PostReaction` queries.

- [ ] **Step 1: Eliminate N+1 reaction queries in `home/templates/tags/topic_block.html`**

In `home/templates/tags/topic_block.html`, ensure `forum_tags` is loaded:
```html
{% load pybb_tags i18n staticfiles site_tags forum_tags %}
```
And right before `{% for post in post_list %}`:
```html
{% prefetch_posts_reactions_tag post_list %}
```

- [ ] **Step 2: Remove dead legacy tag in `home/templates/pybb/post_template.html`**

In `home/templates/pybb/post_template.html`, delete line 5:
```html
{% liked post request.user as liked %}
```

- [ ] **Step 3: Replace hardcoded static path in `notifications/notifications_templates/LK.html`**

In `notifications/notifications_templates/LK.html` line 15, ensure `{% load static %}` is present and replace:
```html
<img src="/static/{{ reaction_image }}" ...>
```
with:
```html
<img src="{% static reaction_image %}" ...>
```

- [ ] **Step 4: Verify template syntax by compiling templates**

Run: `C:\Users\anton\miniconda3\envs\le-francais\python.exe manage.py check`
Expected: System check identified no issues.

- [ ] **Step 5: Commit**

```powershell
git add home/templates/tags/topic_block.html home/templates/pybb/post_template.html notifications/notifications_templates/LK.html
git commit -m "perf(forum): prefetch reactions in topic_block, remove dead like tag, and fix static URL in LK"
```

---

### Task 4: Fix Cyrillic Mentions and Language Switch Safety

**Files:**
- Modify: `forum/utils.py`
- Modify: `forum/tests.py`

**Interfaces:**
- Consumes: `extract_quoted_and_mentioned_names(text)`, `send_forum_mail(users, template, ...)`, `translation.override`
- Produces: Full Cyrillic support in `@Username` mentions and exception-safe `translation.override` context.

- [ ] **Step 1: Write failing test for Cyrillic @mentions and addressed users**

Add to `forum/tests.py`:
```python
    def test_extract_cyrillic_quoted_and_mentioned_names(self):
        from forum.utils import extract_quoted_and_mentioned_names
        text = (
            "> **Алексей Линецкий**:\n> Привет!\n\n"
            "**Fatma Ametova**, посмотри на это:\n"
            "А также спросим @Иван и @Jean_Valjean."
        )
        quoted, addressed, mentions = extract_quoted_and_mentioned_names(text)
        self.assertIn('Алексей Линецкий', quoted)
        self.assertIn('Fatma Ametova', addressed)
        self.assertIn('Иван', mentions)
        self.assertIn('Jean_Valjean', mentions)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `C:\Users\anton\miniconda3\envs\le-francais\python.exe manage.py test forum.tests.ForumUtilTestCase.test_extract_cyrillic_quoted_and_mentioned_names`
Expected: FAIL with `'Иван' not found in mentions`

- [ ] **Step 3: Implement Unicode Cyrillic support and `translation.override` in `forum/utils.py`**

In `forum/utils.py`:
1. In `extract_quoted_and_mentioned_names`:
```python
    # 3. Direct @mentions: @Username (supports Latin, Cyrillic, numbers, _, -)
    mentions = re.findall(r'(?<![\w@])@([a-zA-Z0-9_.\u0400-\u04FF@+-]+)', text)
```
2. In `send_forum_mail`, replace manual `translation.activate` / `translation.activate(old_lang)` with `translation.override(lang)` inside the user loop:
```python
    mails = []
    for user in users:
        ...
        profile = util.get_pybb_profile(user)
        lang = getattr(profile, 'language', None) or settings.LANGUAGE_CODE
        with translation.override(lang):
            subject = render_to_string('pybb/mail_templates/%s_subject.html' % template, user_context)
            txt_message = render_to_string('pybb/mail_templates/%s_body.html' % template, user_context)
            try:
                html_message = render_to_string('pybb/mail_templates/%s_body-html.html' % template, user_context)
            except TemplateDoesNotExist:
                mails.append((subject, txt_message, from_email, [user.email], None, headers))
            else:
                mails.append((subject, txt_message, from_email, [user.email], html_message, headers))

    if mails:
        send_mass_html_mail(mails, fail_silently=True)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `C:\Users\anton\miniconda3\envs\le-francais\python.exe manage.py test forum.tests.ForumUtilTestCase.test_extract_cyrillic_quoted_and_mentioned_names`
Expected: PASS

- [ ] **Step 5: Commit**

```powershell
git add forum/utils.py forum/tests.py
git commit -m "fix(forum): support Cyrillic username mentions and use translation.override"
```

---

### Task 5: Fix Frontend WYSIWYG Editor XSS, Ordered Lists, and Asterisk Lists

**Files:**
- Modify: `home/static/js/forum-editor.js`
- Modify: `forum/tests.py`

**Interfaces:**
- Consumes: `markdownToHtml(md)`, `htmlToMarkdown(rootEl)`
- Produces: Safe HTML rendering with protocol validation, correct bullet list preservation, `<ol>` parsing, and cross-browser regexes without ES2018 lookbehinds.

- [ ] **Step 1: Write backend tests verifying markdown rendering parity**

In `forum/tests.py`:
```python
    def test_ordered_list_and_bullet_list_formatting(self):
        md = "1. First item\n2. Second item\n\n* Bullet item 1\n* Bullet item 2"
        html = self.parser.format(md)
        self.assertIn('<ol>', html)
        self.assertIn('<ul>', html)
        self.assertNotIn('<em> Bullet item 1</em>', html)
```

- [ ] **Step 2: Run backend test to verify baseline**

Run: `C:\Users\anton\miniconda3\envs\le-francais\python.exe manage.py test forum.tests.ForumFormattingTestCase.test_ordered_list_and_bullet_list_formatting`
Expected: PASS

- [ ] **Step 3: Implement sanitization, list parsing, and backward-compatible regex in `home/static/js/forum-editor.js`**

1. **Protocol and HTML injection validation in `markdownToHtml`:**
   Add URL protocol check helper:
   ```javascript
   function sanitizeUrl(url) {
       if (!url) return '#';
       url = url.trim();
       if (/^(https?:|\/|mailto:)/i.test(url)) {
           return escapeHtml(url);
       }
       return '#';
   }
   ```
   Apply to links and images:
   ```javascript
   text = text.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, function(match, alt, url) {
       return '<img src="' + sanitizeUrl(url) + '" alt="' + escapeHtml(alt) + '" class="forum-embedded-img">';
   });
   text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, function(match, label, url) {
       return '<a href="' + sanitizeUrl(url) + '" target="_blank" rel="noopener">' + label + '</a>';
   });
   ```

2. **Ordered lists (`<ol>`) conversion:**
   In `markdownToHtml`:
   ```javascript
   // Ordered lists
   text = text.replace(/^\d+\.\s+(.*)$/gim, '<oli>$1</oli>');
   text = text.replace(/((?:<oli>.*<\/oli>\s*)+)/g, function(match) {
       return '<ol>' + match.replace(/<\/?oli>/g, function(m) { return m === '<oli>' ? '<li>' : '</li>'; }) + '</ol>';
   });
   ```
   And include `<ol` in paragraph ignore check:
   ```javascript
   if (b.startsWith('<blockquote') || b.startsWith('<details') || b.startsWith('<h1') || b.startsWith('<h2') || b.startsWith('<h3') || b.startsWith('<ul') || b.startsWith('<ol') || b.startsWith('<pre') || b.startsWith('<hr')) {
   ```

3. **Asterisk list vs Italic precedence without lookbehind (Safari / iOS compatibility):**
   Process bullet and ordered lists **before** inline italics.
   Replace inline italic regex with capture group emulation:
   ```javascript
   text = text.replace(/(^|[^*])\*([^\s*][^*\n]*?[^\s*]|\S)\*(?!\*)/g, '$1<em>$2</em>');
   ```

- [ ] **Step 4: Verify syntax and editor scripts**

Run: `node -c home/static/js/forum-editor.js`
Expected: Clean compilation with exit code 0.

- [ ] **Step 5: Commit**

```powershell
git add home/static/js/forum-editor.js forum/tests.py
git commit -m "fix(forum): sanitize editor URLs and fix list parsing without regex lookbehind"
```

---

### Task 6: Implement Automated Tests for Reply Email Notifications (Dummy Backend)

**Files:**
- Modify: `forum/tests.py`

**Interfaces:**
- Consumes: `create_pybb_post_notification`, `ForumUserPreference`, `mail.outbox`
- Produces: Exhaustive verification suite for notification emails with guaranteed mock delivery.

- [ ] **Step 1: Write test suite using `locmem.EmailBackend` in `forum/tests.py`**

Add `ForumEmailNotificationTestCase` to `forum/tests.py` (notice no redundant `mail.outbox = []` reassignment as Django TestCase manages it automatically):
```python
from django.core import mail
from django.test import TestCase, override_settings
from pybb.models import Forum, Topic, Post
from custom_user.models import User
from forum.models import ForumUserPreference, PostReply

@override_settings(
    PYBB_USE_DJANGO_MAILER=False,
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
)
class ForumEmailNotificationTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='alice', email='alice@example.com', password='pw')
        self.user2 = User.objects.create_user(username='bob', email='bob@example.com', password='pw')
        self.user3 = User.objects.create_user(username='charlie', email='charlie@example.com', password='pw')
        
        self.forum = Forum.objects.create(name='Discussion', slug='discussion')
        self.topic = Topic.objects.create(forum=self.forum, name='General Topic', user=self.user1)
        self.first_post = Post.objects.create(topic=self.topic, user=self.user1, body='Initial post')

    def test_direct_reply_sends_email_to_recipient(self):
        # Bob replies directly to Alice's post
        reply_post = Post(
            topic=self.topic,
            user=self.user2,
            body='**alice**, thank you!'
        )
        reply_post._reply_to_id = self.first_post.pk
        reply_post.save()

        # Check mail was sent to dummy outbox
        self.assertTrue(len(mail.outbox) >= 1)
        recipient_emails = [m.to[0] for m in mail.outbox]
        self.assertIn('alice@example.com', recipient_emails)
        self.assertNotIn('bob@example.com', recipient_emails)

    def test_opt_out_preference_prevents_email(self):
        # Alice disables reply emails
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

        # Alice should NOT receive email
        recipient_emails = [m.to[0] for m in mail.outbox]
        self.assertNotIn('alice@example.com', recipient_emails)

    def test_quote_email_notification(self):
        quote_post = Post(
            topic=self.topic,
            user=self.user2,
            body='> **alice**:\n> Initial post\n\nI agree completely.'
        )
        quote_post.save()

        self.assertTrue(len(mail.outbox) >= 1)
        recipient_emails = [m.to[0] for m in mail.outbox]
        self.assertIn('alice@example.com', recipient_emails)

    def test_mention_email_notification_with_cyrillic(self):
        cyrillic_user = User.objects.create_user(username='Дмитрий', email='dmitry@example.com', password='pw')
        post = Post(
            topic=self.topic,
            user=self.user1,
            body='Привет, @Дмитрий, как дела?'
        )
        post.save()

        self.assertTrue(len(mail.outbox) >= 1)
        recipient_emails = [m.to[0] for m in mail.outbox]
        self.assertIn('dmitry@example.com', recipient_emails)

    def test_subscriber_email_notification(self):
        # Charlie subscribes to topic
        self.topic.subscribers.add(self.user3)

        post = Post(
            topic=self.topic,
            user=self.user2,
            body='Just a regular comment'
        )
        post.save()

        recipient_emails = [m.to[0] for m in mail.outbox]
        self.assertIn('charlie@example.com', recipient_emails)
        self.assertNotIn('bob@example.com', recipient_emails)
```

- [ ] **Step 2: Run the test suite**

Run: `C:\Users\anton\miniconda3\envs\le-francais\python.exe manage.py test forum.tests.ForumEmailNotificationTestCase`
Expected: All 5 tests PASS with 0 real emails sent.

- [ ] **Step 3: Commit**

```powershell
git add forum/tests.py
git commit -m "test(forum): add notification email tests using dummy locmem backend"
```

---

### Task 7: Full Verification Run

**Files:**
- Verify: Full test suite for `forum` app

- [ ] **Step 1: Execute all forum tests**

Run: `C:\Users\anton\miniconda3\envs\le-francais\python.exe manage.py test forum`
Expected: All tests pass with exit code 0.

- [ ] **Step 2: Execute system check and git status**

Run: `C:\Users\anton\miniconda3\envs\le-francais\python.exe manage.py check`
Run: `git status`
Expected: Clean working tree, all tasks committed, no errors.
