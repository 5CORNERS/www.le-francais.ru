/**
 * Forum Modern WYSIWYG & Markdown Editor
 * Supports bidirectional switching, image upload (Drag&Drop, Clipboard paste),
 * and custom pymdownx formatting (^^underline^^, ~~strike~~, ==mark==, ++keys++, ^sup^, ~sub~, ???- spoilers).
 */
(function(window, document, $) {
    'use strict';

    // Popular emojis list for picker with shortcodes
    var EMOJIS = [
        { char: '😀', code: ':grinning:' },
        { char: '😃', code: ':smiley:' },
        { char: '😄', code: ':smile:' },
        { char: '😁', code: ':grin:' },
        { char: '😆', code: ':laughing:' },
        { char: '😅', code: ':sweat_smile:' },
        { char: '😂', code: ':joy:' },
        { char: '🤣', code: ':rofl:' },
        { char: '😊', code: ':blush:' },
        { char: '😇', code: ':innocent:' },
        { char: '🙂', code: ':slight_smile:' },
        { char: '🙃', code: ':upside_down:' },
        { char: '😉', code: ':wink:' },
        { char: '😌', code: ':relieved:' },
        { char: '😍', code: ':heart_eyes:' },
        { char: '🥰', code: ':smiling_face_with_3_hearts:' },
        { char: '😘', code: ':kissing_heart:' },
        { char: '😋', code: ':yum:' },
        { char: '😛', code: ':stuck_out_tongue:' },
        { char: '😜', code: ':stuck_out_tongue_winking_eye:' },
        { char: '🤪', code: ':zany_face:' },
        { char: '😝', code: ':stuck_out_tongue_closed_eyes:' },
        { char: '🤗', code: ':hugs:' },
        { char: '🤭', code: ':hand_over_mouth:' },
        { char: '🤫', code: ':shushing_face:' },
        { char: '🤔', code: ':thinking:' },
        { char: '🤐', code: ':zipper_mouth:' },
        { char: '🤨', code: ':raised_eyebrow:' },
        { char: '😐', code: ':neutral_face:' },
        { char: '😑', code: ':expressionless:' },
        { char: '😶', code: ':no_mouth:' },
        { char: '😏', code: ':smirk:' },
        { char: '😒', code: ':unamused:' },
        { char: '🙄', code: ':roll_eyes:' },
        { char: '😬', code: ':grimacing:' },
        { char: '🤥', code: ':lying_face:' },
        { char: '😔', code: ':pensive:' },
        { char: '😪', code: ':sleepy:' },
        { char: '🤤', code: ':drooling_face:' },
        { char: '😴', code: ':sleeping:' },
        { char: '😷', code: ':mask:' },
        { char: '🤒', code: ':thermometer_face:' },
        { char: '🤕', code: ':head_bandage:' },
        { char: '🤢', code: ':nauseated_face:' },
        { char: '🤮', code: ':vomiting_face:' },
        { char: '🤧', code: ':sneezing_face:' },
        { char: '🥵', code: ':hot_face:' },
        { char: '🥶', code: ':cold_face:' },
        { char: '🥴', code: ':woozy_face:' },
        { char: '😵', code: ':dizzy_face:' },
        { char: '🤯', code: ':exploding_head:' },
        { char: '🤠', code: ':cowboy:' },
        { char: '🥳', code: ':partying_face:' },
        { char: '😎', code: ':sunglasses:' },
        { char: '🤓', code: ':nerd:' },
        { char: '🧐', code: ':monocle:' },
        { char: '😕', code: ':confused:' },
        { char: '😟', code: ':worried:' },
        { char: '🙁', code: ':slightly_frowning_face:' },
        { char: '😮', code: ':open_mouth:' },
        { char: '😯', code: ':hushed:' },
        { char: '😲', code: ':astonished:' },
        { char: '😳', code: ':flushed:' },
        { char: '🥺', code: ':pleading_face:' },
        { char: '😦', code: ':frowning:' },
        { char: '😧', code: ':anguished:' },
        { char: '😨', code: ':fearful:' },
        { char: '😰', code: ':cold_sweat:' },
        { char: '😥', code: ':disappointed_relieved:' },
        { char: '😢', code: ':cry:' },
        { char: '😭', code: ':sob:' },
        { char: '😱', code: ':scream:' },
        { char: '😖', code: ':confounded:' },
        { char: '😣', code: ':persevere:' },
        { char: '😞', code: ':disappointed:' },
        { char: '😓', code: ':sweat:' },
        { char: '😩', code: ':weary:' },
        { char: '😫', code: ':tired_face:' },
        { char: '🥱', code: ':yawning_face:' },
        { char: '😤', code: ':triumph:' },
        { char: '😡', code: ':rage:' },
        { char: '😠', code: ':angry:' },
        { char: '🤬', code: ':cursing_face:' },
        { char: '😈', code: ':smiling_imp:' },
        { char: '👿', code: ':imp:' },
        { char: '💀', code: ':skull:' },
        { char: '💩', code: ':poop:' },
        { char: '🤡', code: ':clown:' },
        { char: '👻', code: ':ghost:' },
        { char: '👏', code: ':clap:' },
        { char: '👍', code: ':+1:' },
        { char: '👎', code: ':-1:' },
        { char: '👊', code: ':punch:' },
        { char: '✊', code: ':fist:' },
        { char: '🤛', code: ':left_facing_fist:' },
        { char: '🤜', code: ':right_facing_fist:' },
        { char: '🤞', code: ':crossed_fingers:' },
        { char: '✌️', code: ':v:' },
        { char: '🤟', code: ':love_you_gesture:' },
        { char: '👌', code: ':ok_hand:' },
        { char: '👈', code: ':point_left:' },
        { char: '👉', code: ':point_right:' },
        { char: '👆', code: ':point_up_2:' },
        { char: '👇', code: ':point_down:' },
        { char: '☝️', code: ':point_up:' },
        { char: '✋', code: ':hand:' },
        { char: '👋', code: ':wave:' },
        { char: '💪', code: ':muscle:' },
        { char: '🙏', code: ':pray:' },
        { char: '❤️', code: ':heart:' },
        { char: '🧡', code: ':orange_heart:' },
        { char: '💛', code: ':yellow_heart:' },
        { char: '💚', code: ':green_heart:' },
        { char: '💙', code: ':blue_heart:' },
        { char: '💜', code: ':purple_heart:' },
        { char: '🖤', code: ':black_heart:' },
        { char: '🤍', code: ':white_heart:' },
        { char: '💔', code: ':broken_heart:' },
        { char: '❣️', code: ':heavy_heart_exclamation:' },
        { char: '💕', code: ':two_hearts:' },
        { char: '💞', code: ':revolving_hearts:' },
        { char: '💓', code: ':heartbeat:' },
        { char: '💗', code: ':heartpulse:' },
        { char: '💖', code: ':sparkling_heart:' },
        { char: '💘', code: ':cupid:' },
        { char: '💝', code: ':gift_heart:' },
        { char: '☕', code: ':coffee:' },
        { char: '🥖', code: ':baguette_bread:' },
        { char: '🥐', code: ':croissant:' },
        { char: '🍷', code: ':wine_glass:' },
        { char: '🧀', code: ':cheese:' },
        { char: '🇫🇷', code: ':flag_fr:' },
        { char: '🇷🇺', code: ':flag_ru:' },
        { char: '🇬🇧', code: ':flag_gb:' },
        { char: '🎉', code: ':tada:' },
        { char: '💡', code: ':bulb:' },
        { char: '✍️', code: ':writing_hand:' },
        { char: '📚', code: ':books:' },
        { char: '❓', code: ':question:' },
        { char: '❗', code: ':exclamation:' }
    ];

    var SHORTCODE_TO_CHAR = {
        ':thumbsup:': '👍',
        ':thumbsdown:': '👎',
        ':fire:': '🔥',
        ':star:': '⭐',
        ':100:': '💯',
        ':check:': '✔️',
        ':x:': '❌',
        ':beer:': '🍺',
        ':cake:': '🎂',
        ':book:': '📖'
    };
    for (var i = 0; i < EMOJIS.length; i++) {
        SHORTCODE_TO_CHAR[EMOJIS[i].code] = EMOJIS[i].char;
    }

    function escapeHtml(str) {
        return (str || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function sanitizeUrl(url) {
        if (!url) return '#';
        url = url.trim();
        if (/^(https?:|\/|mailto:)/i.test(url)) {
            return escapeHtml(url);
        }
        return '#';
    }

    /**
     * Converts Markdown string to Visual HTML for contenteditable
     */
    function markdownToHtml(md) {
        if (!md) return '';
        var text = md.replace(/\r\n/g, '\n').replace(/\r/g, '\n');

        // Protect code blocks
        var codeBlocks = [];
        text = text.replace(/```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g, function(match, lang, code) {
            var id = '___CODEBLOCK_' + codeBlocks.length + '___';
            codeBlocks.push({ lang: lang || '', code: code });
            return id;
        });

        // Protect inline code
        var inlineCodes = [];
        text = text.replace(/`([^`\n]+)`/g, function(match, code) {
            var id = '___INLINECODE_' + inlineCodes.length + '___';
            inlineCodes.push(code);
            return id;
        });

        // Spoilers: ???- "Title"\n(    body)*
        text = text.replace(/\?\?\?[-+]?\s*"([^"\n]+)"\n((?:(?:    |\t).*\n?)+)/g, function(match, title, body) {
            var cleanBody = body.replace(/^(?:    |\t)/gm, '');
            return '\n<details class="forum-spoiler"><summary>' + escapeHtml(title) + '</summary><div class="spoiler-body">' + markdownToHtml(cleanBody) + '</div></details>\n';
        });

        // Blockquotes
        var lines = text.split('\n');
        var inQuote = false;
        var quoteLines = [];
        var processedLines = [];
        for (var i = 0; i < lines.length; i++) {
            var line = lines[i];
            if (line.match(/^>\s?(.*)$/)) {
                inQuote = true;
                quoteLines.push(line.replace(/^>\s?/, ''));
            } else {
                if (inQuote) {
                    processedLines.push('<blockquote>' + markdownToHtml(quoteLines.join('\n')) + '</blockquote>');
                    inQuote = false;
                    quoteLines = [];
                }
                processedLines.push(line);
            }
        }
        if (inQuote) {
            processedLines.push('<blockquote>' + markdownToHtml(quoteLines.join('\n')) + '</blockquote>');
        }
        text = processedLines.join('\n');

        // Headings
        text = text.replace(/^### (.*$)/gim, '<h3>$1</h3>');
        text = text.replace(/^## (.*$)/gim, '<h2>$1</h2>');
        text = text.replace(/^# (.*$)/gim, '<h1>$1</h1>');

        // Horizontal rules
        text = text.replace(/^---$/gim, '<hr>');

        // Images: ![alt](url)
        text = text.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, function(match, alt, url) {
            return '<img src="' + sanitizeUrl(url) + '" alt="' + escapeHtml(alt) + '" class="forum-embedded-img">';
        });

        // Links: [text](url)
        text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, function(match, label, url) {
            return '<a href="' + sanitizeUrl(url) + '" target="_blank" rel="noopener">' + label + '</a>';
        });

        // Emojis: :heart: -> ❤️
        text = text.replace(/:([a-zA-Z0-9_+-]+):/g, function(match) {
            return SHORTCODE_TO_CHAR[match] || match;
        });

        // Custom formatting
        // Keystrokes: ++ctrl+c++, ++asdf++, ++"hello world"++
        text = text.replace(/\+\+(?:(?:"([^"]+)")|(.+?))\+\+/g, function(match, quoted, unquoted) {
            return '<kbd class="editor-key">' + escapeHtml(quoted || unquoted) + '</kbd>';
        });

        // Highlight: ==text==
        text = text.replace(/==(.+?)==/g, '<mark class="editor-mark">$1</mark>');

        // Underline: ^^text^^
        text = text.replace(/\^\^(.+?)\^\^/g, '<u class="editor-underline">$1</u>');

        // Strikethrough: ~~text~~
        text = text.replace(/~~(.+?)~~/g, '<del class="editor-del">$1</del>');

        // Superscript: ^text^
        text = text.replace(/\^([^\s^]+)\^/g, '<sup>$1</sup>');

        // Subscript: ~text~
        text = text.replace(/~([^\s~]+)~/g, '<sub>$1</sub>');

        // Ordered lists
        text = text.replace(/^\d+\.\s+(.*)$/gim, '<oli>$1</oli>');
        text = text.replace(/((?:<oli>.*<\/oli>\s*)+)/g, function(match) {
            return '<ol>' + match.replace(/<\/?oli>/g, function(m) { return m === '<oli>' ? '<li>' : '</li>'; }) + '</ol>';
        });

        // Unordered lists
        text = text.replace(/^[-*]\s+(.*)$/gim, '<li>$1</li>');
        text = text.replace(/((?:<li>.*<\/li>\s*)+)/g, '<ul>$1</ul>');

        // Bold italic: ***text***
        text = text.replace(/\*\*\*([^*]+)\*\*\*/g, '<strong><em>$1</em></strong>');

        // Bold: **text**
        text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

        // Italic: *text* (emulate negative lookbehind with capture group for cross-browser support)
        text = text.replace(/(^|[^*])\*([^\s*][^*\n]*?[^\s*]|\S)\*(?!\*)/g, '$1<em>$2</em>');

        // Restore inline codes
        for (var j = 0; j < inlineCodes.length; j++) {
            text = text.replace('___INLINECODE_' + j + '___', '<code>' + escapeHtml(inlineCodes[j]) + '</code>');
        }

        // Restore code blocks
        for (var k = 0; k < codeBlocks.length; k++) {
            var cb = codeBlocks[k];
            text = text.replace('___CODEBLOCK_' + k + '___', '<pre class="editor-code-block"' + (cb.lang ? ' data-lang="' + escapeHtml(cb.lang) + '"' : '') + '><code>' + escapeHtml(cb.code) + '</code></pre>');
        }

        // Paragraphs & newlines
        var blocks = text.split(/\n{2,}/);
        var res = blocks.map(function(b) {
            b = b.trim();
            if (!b) return '';
            if (b.startsWith('<blockquote') || b.startsWith('<details') || b.startsWith('<h1') || b.startsWith('<h2') || b.startsWith('<h3') || b.startsWith('<ul') || b.startsWith('<ol') || b.startsWith('<pre') || b.startsWith('<hr')) {
                return b;
            }
            return '<p>' + b.replace(/\n/g, '<br>') + '</p>';
        });

        return res.filter(Boolean).join('');
    }

    /**
     * Converts DOM tree from contenteditable back to Markdown
     */
    function htmlToMarkdown(domRoot) {
        function walk(node) {
            if (!node) return '';
            if (node.nodeType === 3) return node.nodeValue;
            if (node.nodeType !== 1) return '';

            var tag = node.tagName.toLowerCase();

            // Skip uploading placeholder
            if (node.classList && node.classList.contains('forum-img-uploading-placeholder')) {
                return '';
            }

            var childrenText = '';
            for (var i = 0; i < node.childNodes.length; i++) {
                childrenText += walk(node.childNodes[i]);
            }

            switch (tag) {
                case 'strong':
                case 'b':
                    return childrenText.trim() ? '**' + childrenText.trim() + '**' : '';
                case 'em':
                case 'i':
                    return childrenText.trim() ? '*' + childrenText.trim() + '*' : '';
                case 'u':
                case 'ins':
                    return childrenText.trim() ? '^^' + childrenText.trim() + '^^' : '';
                case 'del':
                case 's':
                case 'strike':
                    return childrenText.trim() ? '~~' + childrenText.trim() + '~~' : '';
                case 'mark':
                    return childrenText.trim() ? '==' + childrenText.trim() + '==' : '';
                case 'sup':
                    return childrenText.trim() ? '^' + childrenText.trim() + '^' : '';
                case 'sub':
                    return childrenText.trim() ? '~' + childrenText.trim() + '~' : '';
                case 'kbd':
                    if (node.parentNode && node.parentNode.classList && node.parentNode.classList.contains('keys')) {
                        return childrenText.trim();
                    }
                    return childrenText.trim() ? '++' + childrenText.trim() + '++' : '';
                case 'span':
                    if (node.classList && node.classList.contains('keys')) {
                        return childrenText.trim() ? '++' + childrenText.trim() + '++' : '';
                    }
                    return childrenText;
                case 'code':
                    if (node.parentNode && node.parentNode.tagName.toLowerCase() === 'pre') {
                        return node.textContent;
                    }
                    return '`' + node.textContent + '`';
                case 'pre':
                    var lang = node.dataset.lang || '';
                    var codeNode = node.querySelector('code') || node;
                    return '\n```' + lang + '\n' + codeNode.textContent.replace(/^\n+|\n+$/g, '') + '\n```\n\n';
                case 'h1':
                    return '# ' + childrenText.trim() + '\n\n';
                case 'h2':
                    return '## ' + childrenText.trim() + '\n\n';
                case 'h3':
                    return '### ' + childrenText.trim() + '\n\n';
                case 'a':
                    return '[' + childrenText.trim() + '](' + (node.getAttribute('href') || '') + ')';
                case 'img':
                    var src = node.getAttribute('src') || '';
                    var alt = node.getAttribute('alt') || '';
                    return '![' + alt + '](' + src + ')';
                case 'br':
                    return '\n';
                case 'hr':
                    return '\n---\n\n';
                case 'blockquote':
                    var lines = childrenText.trim().split('\n');
                    return lines.map(function(l) { return '> ' + l; }).join('\n') + '\n\n';
                case 'details':
                    var summaryNode = node.querySelector('summary');
                    var summary = summaryNode ? summaryNode.textContent.trim() : 'Спойлер';
                    var bodyNode = node.querySelector('.spoiler-body') || node;
                    var bodyMd = '';
                    for (var j = 0; j < bodyNode.childNodes.length; j++) {
                        var child = bodyNode.childNodes[j];
                        if (child.tagName && child.tagName.toLowerCase() === 'summary') continue;
                        bodyMd += walk(child);
                    }
                    var bodyLines = bodyMd.trim().split('\n').map(function(l) { return '    ' + l; }).join('\n');
                    return '???- "' + summary + '"\n' + bodyLines + '\n\n';
                case 'ul':
                    var uRes = '';
                    for (var u = 0; u < node.children.length; u++) {
                        if (node.children[u].tagName.toLowerCase() === 'li') {
                            uRes += '- ' + walk(node.children[u]).trim() + '\n';
                        }
                    }
                    return uRes + '\n';
                case 'ol':
                    var oRes = '';
                    for (var o = 0; o < node.children.length; o++) {
                        if (node.children[o].tagName.toLowerCase() === 'li') {
                            oRes += (o + 1) + '. ' + walk(node.children[o]).trim() + '\n';
                        }
                    }
                    return oRes + '\n';
                case 'li':
                    return childrenText;
                case 'p':
                    return childrenText.trim() + '\n\n';
                case 'div':
                    return childrenText + '\n';
                default:
                    return childrenText;
            }
        }

        return walk(domRoot).trim();
    }

    /**
     * Gets CSRF token from cookie or hidden form input
     */
    function getCsrfToken() {
        var $csrf = $('input[name="csrfmiddlewaretoken"]');
        if ($csrf.length) return $csrf.val();
        var match = document.cookie.match(/csrftoken=([^;]+)/);
        return match ? match[1] : '';
    }

    /**
     * Helper to wrap selected text in contenteditable with an inline tag
     */
    function wrapSelectionWithTag(tagName, className) {
        var sel = window.getSelection();
        if (!sel || !sel.rangeCount) return;
        var range = sel.getRangeAt(0);

        var selectedText = range.toString();
        var el = document.createElement(tagName);
        if (className) el.className = className;

        if (selectedText) {
            el.textContent = selectedText;
            range.deleteContents();
            range.insertNode(el);
        } else {
            el.innerHTML = '&#8203;'; // Zero-width space so cursor can stay inside
            range.insertNode(el);
            range.selectNodeContents(el);
        }

        // Collapse to end of element
        var newRange = document.createRange();
        newRange.setStartAfter(el);
        newRange.collapse(true);
        sel.removeAllRanges();
        sel.addRange(newRange);
    }

    /**
     * Helper to wrap textarea selection with markdown prefixes/suffixes
     */
    function wrapTextareaSelection($textarea, prefix, suffix, placeholder) {
        var el = $textarea[0];
        var start = el.selectionStart;
        var end = el.selectionEnd;
        var val = el.value;
        var selected = val.substring(start, end) || placeholder || '';
        var replacement = prefix + selected + suffix;

        el.value = val.substring(0, start) + replacement + val.substring(end);
        el.focus();
        el.setSelectionRange(start + prefix.length, start + prefix.length + selected.length);
        $textarea.trigger('input');
    }

    /**
     * Main Editor Class
     */
    function ForumEditor(options) {
        this.options = $.extend({
            textareaSelector: '#id_body',
            uploadUrl: '/forum/upload-image/',
            initialMode: localStorage.getItem('forum_editor_mode') || 'visual'
        }, options);

        this.$textarea = $(this.options.textareaSelector);
        if (!this.$textarea.length) return;

        this.currentMode = this.options.initialMode; // 'visual' or 'markdown'
        this.savedRange = null;
        this.init();
    }

    ForumEditor.prototype.saveSelection = function() {
        if (this.currentMode === 'visual') {
            var sel = window.getSelection();
            if (sel && sel.rangeCount > 0) {
                var range = sel.getRangeAt(0);
                if (this.$visualEditor && this.$visualEditor.length && this.$visualEditor[0].contains(range.commonAncestorContainer)) {
                    this.savedRange = range.cloneRange();
                }
            }
        }
    };

    ForumEditor.prototype.restoreSelection = function() {
        if (this.currentMode === 'visual' && this.savedRange) {
            var sel = window.getSelection();
            if (sel) {
                sel.removeAllRanges();
                sel.addRange(this.savedRange);
            }
        }
    };


    ForumEditor.prototype.init = function() {
        var self = this;

        // Prevent legacy markItUp from initializing
        this.$textarea.addClass('no-markitup forum-markdown-textarea');

        // Prevent HTML5 constraint validation on hidden textarea from blocking form submit
        this.$textarea.removeAttr('required');
        this.$textarea.closest('form').attr('novalidate', 'novalidate');

        // Build Editor UI Wrapper
        this.buildUI();

        // Populate initial content
        var initialMarkdown = this.$textarea.val() || '';
        if (this.currentMode === 'visual') {
            this.$visualEditor.html(markdownToHtml(initialMarkdown));
            this.$visualEditor.show();
            this.$textarea.hide();
        } else {
            this.$visualEditor.hide();
            this.$textarea.show();
        }
        this.updateModeButtons();

        // Bind events
        this.bindEvents();

        // Bind upload handlers (Drag&Drop, Paste, Button)
        this.bindUploadHandlers();

        // Bind resizer
        this.initResizer();

        // Expose public instance
        window.forumEditor = this;
    };

    ForumEditor.prototype.buildUI = function() {
        var emojiItemsHtml = EMOJIS.map(function(item) {
            return '<span class="forum-emoji-item" data-emoji="' + item.char + '" data-code="' + item.code + '" title="' + item.code + '">' + item.char + '</span>';
        }).join('');

        var toolbarHtml = [
            '<div class="forum-editor-wrapper">',
                '<div class="forum-editor-toolbar">',
                    // Left Mode Switcher Block
                    '<div class="forum-editor-mode-block">',
                        '<div class="forum-mode-switch" title="Переключить режим: Визуальный / Markdown">',
                            '<span class="forum-mode-switch-btn visual active" data-mode="visual" title="Визуальный редактор (WYSIWYG)"><i class="fa fa-eye"></i></span>',
                            '<label class="forum-toggle-track" title="Переключить режим">',
                                '<input type="checkbox" class="forum-mode-checkbox" aria-label="Переключить Markdown / Визуальный">',
                                '<span class="forum-toggle-thumb"></span>',
                            '</label>',
                            '<span class="forum-mode-switch-btn markdown" data-mode="markdown" title="Исходный Markdown"><i class="fa fa-code"></i></span>',
                        '</div>',
                    '</div>',
                    '<div class="forum-toolbar-divider"></div>',
                    // Formatting & Insert Tools Block
                    '<div class="forum-editor-tools-block">',
                        // Formatting
                        '<div class="btn-group btn-group-sm" role="group">',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="bold" title="Жирный (**текст**)"><i class="fa fa-bold"></i></button>',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="italic" title="Курсив (*текст*)"><i class="fa fa-italic"></i></button>',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="underline" title="Подчеркнутый (^^текст^^)"><i class="fa fa-underline"></i></button>',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="strikethrough" title="Зачеркнутый (~~текст~~)"><i class="fa fa-strikethrough"></i></button>',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="mark" title="Выделение маркером (==текст==)"><i class="fa fa-pencil" style="background:#fff3cd;padding:1px 3px;border-radius:2px;"></i></button>',
                        '</div>',
                        // Script / Keys
                        '<div class="btn-group btn-group-sm" role="group">',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="superscript" title="Верхний индекс (^текст^)"><i class="fa fa-superscript"></i></button>',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="subscript" title="Нижний индекс (~текст~)"><i class="fa fa-subscript"></i></button>',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="kbd" title="Клавиша (++клавиша++)"><i class="fa fa-keyboard-o"></i></button>',
                        '</div>',
                        // Structure
                        '<div class="btn-group btn-group-sm" role="group">',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="h2" title="Подзаголовок (## Заголовок)"><strong>H2</strong></button>',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="h3" title="Подзаголовок (### Заголовок)"><strong>H3</strong></button>',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="quote" title="Цитата (> текст)"><i class="fa fa-quote-left"></i></button>',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="ul" title="Список (- пункт)"><i class="fa fa-list-ul"></i></button>',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="ol" title="Нумерованный список (1. пункт)"><i class="fa fa-list-ol"></i></button>',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="spoiler" title="Спойлер (???- Заголовок)"><i class="fa fa-caret-square-o-down"></i></button>',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="code" title="Код (`код`)"><i class="fa fa-code"></i></button>',
                        '</div>',
                        // Insert
                        '<div class="btn-group btn-group-sm" role="group">',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="link" title="Вставить ссылку"><i class="fa fa-link"></i></button>',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="image" title="Вставить или загрузить изображение"><i class="fa fa-picture-o"></i></button>',
                            '<div class="btn-group btn-group-sm forum-emoji-group position-relative" role="group">',
                                '<button type="button" class="btn btn-light forum-editor-btn forum-emoji-btn" title="Вставить эмодзи"><i class="fa fa-smile-o"></i></button>',
                                '<div class="forum-emoji-dropdown d-none">',
                                    '<div class="forum-emoji-header">',
                                        '<span class="small font-weight-bold text-muted">Эмодзи</span>',
                                        '<button type="button" class="btn btn-sm btn-link text-muted p-0 forum-emoji-close" style="font-size:16px;line-height:1;text-decoration:none;">&times;</button>',
                                    '</div>',
                                    '<div class="forum-emoji-grid">' + emojiItemsHtml + '</div>',
                                '</div>',
                            '</div>',
                        '</div>',
                    '</div>',
                '</div>',
                // Hidden file input
                '<input type="file" class="forum-image-file-input d-none" accept="image/jpeg,image/png,image/gif,image/webp">',
                // Editor body container
                '<div class="forum-editor-container position-relative">',
                    '<div class="forum-visual-editor" contenteditable="true" spellcheck="true" placeholder="Напишите ответ или перетащите изображение сюда..."></div>',
                    // Drop overlay
                    '<div class="forum-drop-overlay d-none">',
                        '<div class="forum-drop-message">',
                            '<i class="fa fa-cloud-upload fa-3x mb-2 text-primary"></i>',
                            '<div><strong>Отпустите изображение для загрузки</strong></div>',
                            '<small class="text-muted">Файл будет оптимизирован и добавлен в сообщение</small>',
                        '</div>',
                    '</div>',
                    // Upload progress banner
                    '<div class="forum-upload-progress d-none alert alert-info py-2 px-3 mb-0">',
                        '<i class="fa fa-spinner fa-spin mr-2"></i>',
                        '<span class="upload-progress-text">Загрузка и оптимизация изображения...</span>',
                    '</div>',
                '</div>',
                // Footer
                '<div class="forum-editor-footer d-flex justify-content-between align-items-center">',
                    '<small class="text-muted"><i class="fa fa-info-circle mr-1"></i>Поддерживаются: Drag & Drop и Ctrl+V для картинок, <code>^^подчеркивание^^</code>, <code>==маркер==</code>, <code>~~зачеркивание~~</code>, <code>++клавиши++</code>, спойлеры.</small>',
                    '<div class="d-flex align-items-center flex-shrink-0 ml-2">',
                        '<small class="text-muted font-italic forum-char-counter mr-2"></small>',
                        '<div class="forum-editor-resizer" title="Изменить высоту поля ввода">',
                            '<svg viewBox="0 0 10 10" width="10" height="10">',
                                '<path d="M9 1L1 9M9 5L5 9M9 9L9 9" stroke="#adb5bd" stroke-width="1.5" stroke-linecap="round"/>',
                            '</svg>',
                        '</div>',
                    '</div>',
                '</div>',
            '</div>'
        ].join('');

        this.$wrapper = $(toolbarHtml);
        this.$textarea.before(this.$wrapper);

        // Move textarea inside container
        this.$container = this.$wrapper.find('.forum-editor-container');
        this.$visualEditor = this.$wrapper.find('.forum-visual-editor');
        this.$dropOverlay = this.$wrapper.find('.forum-drop-overlay');
        this.$uploadProgress = this.$wrapper.find('.forum-upload-progress');
        this.$fileInput = this.$wrapper.find('.forum-image-file-input');
        this.$charCounter = this.$wrapper.find('.forum-char-counter');

        this.$container.append(this.$textarea);
    };

    ForumEditor.prototype.updateModeButtons = function() {
        var isVisual = this.currentMode === 'visual';
        this.$wrapper.find('.forum-mode-checkbox').prop('checked', !isVisual);
        this.$wrapper.find('.forum-mode-switch-btn.visual').toggleClass('active', isVisual);
        this.$wrapper.find('.forum-mode-switch-btn.markdown').toggleClass('active', !isVisual);
    };

    ForumEditor.prototype.setMode = function(newMode) {
        if (newMode === this.currentMode) return;

        if (newMode === 'markdown') {
            // Keep resized height in sync
            var visualH = this.$visualEditor.outerHeight();
            if (visualH && visualH > 0) {
                this.$textarea.css({'height': visualH + 'px', 'max-height': 'none'});
            }
            // Convert Visual HTML -> Markdown
            var md = htmlToMarkdown(this.$visualEditor[0]);
            this.$textarea.val(md);
            this.$visualEditor.hide();
            this.$textarea.show().focus();
            this.currentMode = 'markdown';
        } else {
            // Keep resized height in sync
            var textH = this.$textarea.outerHeight();
            if (textH && textH > 0) {
                this.$visualEditor.css({'height': textH + 'px', 'max-height': 'none'});
            }
            // Convert Markdown -> Visual HTML
            var html = markdownToHtml(this.$textarea.val());
            this.$visualEditor.html(html);
            this.$textarea.hide();
            this.$visualEditor.show().focus();
            this.currentMode = 'visual';
        }

        localStorage.setItem('forum_editor_mode', this.currentMode);
        this.updateModeButtons();
        this.updateCharCounter();
    };

    ForumEditor.prototype.syncMarkdownFromVisual = function() {
        if (this.currentMode === 'visual') {
            var md = htmlToMarkdown(this.$visualEditor[0]);
            this.$textarea.val(md);
        }
    };

    ForumEditor.prototype.syncVisualFromMarkdown = function() {
        var md = this.$textarea.val() || '';
        var html = markdownToHtml(md);
        this.$visualEditor.html(html);
        this.updateCharCounter();
    };

    ForumEditor.prototype.insertMarkdown = function(md) {
        if (this.currentMode === 'visual') {
            this.syncMarkdownFromVisual();
            var cur = this.$textarea.val();
            if (cur && !cur.endsWith('\n')) cur += '\n\n';
            this.$textarea.val(cur + md);
            this.syncVisualFromMarkdown();
        } else {
            var curVal = this.$textarea.val();
            if (curVal && !curVal.endsWith('\n')) curVal += '\n\n';
            this.$textarea.val(curVal + md);
            this.updateCharCounter();
        }
    };

    ForumEditor.prototype.updateCharCounter = function() {
        var len = (this.currentMode === 'visual' ? htmlToMarkdown(this.$visualEditor[0]) : this.$textarea.val()).length;
        this.$charCounter.text(len > 0 ? len + ' симв.' : '');
    };

    ForumEditor.prototype.bindEvents = function() {
        var self = this;

        // Prevent toolbar buttons and emoji items from stealing focus from visual editor
        this.$wrapper.on('mousedown', '.forum-editor-btn, .forum-emoji-item, .forum-emoji-close', function(e) {
            e.preventDefault();
        });

        // Save selection on cursor movement / click in visual editor
        this.$visualEditor.on('mouseup keyup focus blur', function() {
            self.saveSelection();
        });

        // Mode switch checkbox change
        this.$wrapper.on('change', '.forum-mode-checkbox', function() {
            var mode = this.checked ? 'markdown' : 'visual';
            self.setMode(mode);
        });

        // Mode switch icon buttons click
        this.$wrapper.on('click', '.forum-mode-switch-btn', function(e) {
            e.preventDefault();
            e.stopPropagation();
            var mode = $(this).data('mode');
            self.setMode(mode);
        });

        // Toolbar formatting buttons
        this.$wrapper.on('click', '.forum-editor-btn[data-cmd]', function(e) {
            e.preventDefault();
            var cmd = $(this).data('cmd');
            self.executeCommand(cmd);
        });

        // Emoji popup toggle
        this.$wrapper.on('click', '.forum-emoji-btn', function(e) {
            e.preventDefault();
            e.stopPropagation();
            var $dropdown = self.$wrapper.find('.forum-emoji-dropdown');
            $dropdown.toggleClass('d-none');
        });

        // Emoji popup close button
        this.$wrapper.on('click', '.forum-emoji-close', function(e) {
            e.preventDefault();
            e.stopPropagation();
            self.$wrapper.find('.forum-emoji-dropdown').addClass('d-none');
        });

        // Close emoji popup on click outside
        $(document).on('click.forumEmoji', function(e) {
            if (!$(e.target).closest('.forum-emoji-group').length) {
                self.$wrapper.find('.forum-emoji-dropdown').addClass('d-none');
            }
        });

        // Emoji buttons
        this.$wrapper.on('click', '.forum-emoji-item', function(e) {
            e.preventDefault();
            e.stopPropagation();
            var emoji = $(this).data('emoji');
            var code = $(this).data('code') || emoji;
            self.insertEmoji(emoji, code);
            self.$wrapper.find('.forum-emoji-dropdown').addClass('d-none');
        });

        // Live continuous sync on input / changes in visual editor
        this.$visualEditor.on('input keyup paste change', function() {
            self.syncMarkdownFromVisual();
            self.updateCharCounter();
        });
        this.$textarea.on('input keyup paste change', function() {
            self.updateCharCounter();
        });

        // Sync before submit button click and form submit
        var $form = this.$textarea.closest('form');
        $form.on('click', 'button[type="submit"], input[type="submit"]', function() {
            self.syncMarkdownFromVisual();
        });
        $form.on('submit', function(e) {
            self.syncMarkdownFromVisual();
            var val = $.trim(self.$textarea.val());
            if (!val) {
                e.preventDefault();
                e.stopPropagation();
                alert('Пожалуйста, введите текст сообщения.');
                if (self.currentMode === 'visual') {
                    self.$visualEditor.focus();
                } else {
                    self.$textarea.focus();
                }
                return false;
            }
        });
    };

    ForumEditor.prototype.executeCommand = function(cmd) {
        if (this.currentMode === 'visual') {
            this.executeVisualCommand(cmd);
            this.syncMarkdownFromVisual();
        } else {
            this.executeMarkdownCommand(cmd);
        }
        this.updateCharCounter();
    };

    ForumEditor.prototype.executeVisualCommand = function(cmd) {
        this.$visualEditor.focus();
        if (this.savedRange) {
            this.restoreSelection();
        }
        switch (cmd) {
            case 'bold':
                document.execCommand('bold', false, null);
                break;
            case 'italic':
                document.execCommand('italic', false, null);
                break;
            case 'underline':
                wrapSelectionWithTag('u', 'editor-underline');
                break;
            case 'strikethrough':
                wrapSelectionWithTag('del', 'editor-del');
                break;
            case 'mark':
                wrapSelectionWithTag('mark', 'editor-mark');
                break;
            case 'superscript':
                document.execCommand('superscript', false, null);
                break;
            case 'subscript':
                document.execCommand('subscript', false, null);
                break;
            case 'kbd':
                wrapSelectionWithTag('kbd', 'editor-key');
                break;
            case 'h2':
                document.execCommand('formatBlock', false, '<h2>');
                break;
            case 'h3':
                document.execCommand('formatBlock', false, '<h3>');
                break;
            case 'quote':
                document.execCommand('formatBlock', false, '<blockquote>');
                break;
            case 'ul':
                document.execCommand('insertUnorderedList', false, null);
                break;
            case 'ol':
                document.execCommand('insertOrderedList', false, null);
                break;
            case 'spoiler':
                var title = prompt('Введите заголовок спойлера:', 'Спойлер');
                if (title !== null) {
                    var spoilerHtml = '<details class="forum-spoiler"><summary>' + escapeHtml(title || 'Спойлер') + '</summary><div class="spoiler-body"><p>Текст спойлера</p></div></details><p><br></p>';
                    document.execCommand('insertHTML', false, spoilerHtml);
                }
                break;
            case 'code':
                wrapSelectionWithTag('code');
                break;
            case 'link':
                var url = prompt('Введите URL ссылки:', 'https://');
                if (url) {
                    var sel = window.getSelection();
                    var selectedText = sel ? sel.toString() : '';
                    if (!selectedText) {
                        var text = prompt('Введите текст ссылки:', url);
                        document.execCommand('insertHTML', false, '<a href="' + escapeHtml(url) + '" target="_blank" rel="noopener">' + escapeHtml(text || url) + '</a>');
                    } else {
                        document.execCommand('createLink', false, url);
                    }
                }
                break;
            case 'image':
                this.$fileInput.click();
                break;
        }
        this.saveSelection();
    };


    ForumEditor.prototype.executeMarkdownCommand = function(cmd) {
        switch (cmd) {
            case 'bold':
                wrapTextareaSelection(this.$textarea, '**', '**', 'жирный текст');
                break;
            case 'italic':
                wrapTextareaSelection(this.$textarea, '*', '*', 'курсив');
                break;
            case 'underline':
                wrapTextareaSelection(this.$textarea, '^^', '^^', 'подчеркнутый текст');
                break;
            case 'strikethrough':
                wrapTextareaSelection(this.$textarea, '~~', '~~', 'зачеркнутый текст');
                break;
            case 'mark':
                wrapTextareaSelection(this.$textarea, '==', '==', 'выделенный текст');
                break;
            case 'superscript':
                wrapTextareaSelection(this.$textarea, '^', '^', '2');
                break;
            case 'subscript':
                wrapTextareaSelection(this.$textarea, '~', '~', '2');
                break;
            case 'kbd':
                wrapTextareaSelection(this.$textarea, '++', '++', 'Ctrl+C');
                break;
            case 'h2':
                wrapTextareaSelection(this.$textarea, '## ', '\n', 'Заголовок');
                break;
            case 'h3':
                wrapTextareaSelection(this.$textarea, '### ', '\n', 'Подзаголовок');
                break;
            case 'quote':
                wrapTextareaSelection(this.$textarea, '> ', '\n', 'Текст цитаты');
                break;
            case 'ul':
                wrapTextareaSelection(this.$textarea, '- ', '\n', 'Элемент списка');
                break;
            case 'ol':
                wrapTextareaSelection(this.$textarea, '1. ', '\n', 'Первый пункт');
                break;
            case 'spoiler':
                var title = prompt('Введите заголовок спойлера:', 'Спойлер');
                if (title !== null) {
                    wrapTextareaSelection(this.$textarea, '???- "' + (title || 'Спойлер') + '"\n    ', '\n\n', 'Текст спойлера');
                }
                break;
            case 'code':
                wrapTextareaSelection(this.$textarea, '`', '`', 'код');
                break;
            case 'link':
                var linkUrl = prompt('Введите URL ссылки:', 'https://');
                if (linkUrl) {
                    wrapTextareaSelection(this.$textarea, '[', '](' + linkUrl + ')', 'текст ссылки');
                }
                break;
            case 'image':
                this.$fileInput.click();
                break;
        }
    };

    ForumEditor.prototype.insertEmoji = function(emoji, code) {
        if (this.currentMode === 'visual') {
            this.$visualEditor.focus();
            if (this.savedRange) {
                this.restoreSelection();
            }
            var inserted = false;
            try {
                inserted = document.execCommand('insertText', false, emoji);
            } catch (err) {}

            if (!inserted) {
                var sel = window.getSelection();
                if (sel && sel.rangeCount > 0) {
                    var range = sel.getRangeAt(0);
                    range.deleteContents();
                    var textNode = document.createTextNode(emoji);
                    range.insertNode(textNode);
                    range.setStartAfter(textNode);
                    range.collapse(true);
                    sel.removeAllRanges();
                    sel.addRange(range);
                } else {
                    this.$visualEditor.append(document.createTextNode(emoji));
                }
            }
            this.saveSelection();
            this.syncMarkdownFromVisual();
        } else {
            wrapTextareaSelection(this.$textarea, '', code || emoji, '');
        }
        this.updateCharCounter();
    };


    ForumEditor.prototype.bindUploadHandlers = function() {
        var self = this;

        // Button file input change
        this.$fileInput.on('change', function() {
            var files = this.files;
            if (files && files.length) {
                for (var i = 0; i < files.length; i++) {
                    self.uploadFile(files[i]);
                }
                this.value = '';
            }
        });

        // Drag & Drop
        var $wrapper = this.$wrapper;
        var dragCounter = 0;

        $wrapper.on('dragenter', function(e) {
            e.preventDefault();
            e.stopPropagation();
            dragCounter++;
            if (e.originalEvent.dataTransfer && e.originalEvent.dataTransfer.types) {
                self.$dropOverlay.removeClass('d-none');
            }
        });

        $wrapper.on('dragover', function(e) {
            e.preventDefault();
            e.stopPropagation();
        });

        $wrapper.on('dragleave', function(e) {
            e.preventDefault();
            e.stopPropagation();
            dragCounter--;
            if (dragCounter <= 0) {
                dragCounter = 0;
                self.$dropOverlay.addClass('d-none');
            }
        });

        $wrapper.on('drop', function(e) {
            e.preventDefault();
            e.stopPropagation();
            dragCounter = 0;
            self.$dropOverlay.addClass('d-none');

            var files = e.originalEvent.dataTransfer ? e.originalEvent.dataTransfer.files : null;
            if (files && files.length) {
                for (var i = 0; i < files.length; i++) {
                    var file = files[i];
                    if (file.type.indexOf('image/') === 0) {
                        self.uploadFile(file);
                    }
                }
            }
        });

        // Clipboard Paste
        var pasteHandler = function(e) {
            var items = (e.originalEvent || e).clipboardData ? (e.originalEvent || e).clipboardData.items : null;
            if (!items) return;

            for (var i = 0; i < items.length; i++) {
                if (items[i].type.indexOf('image') !== -1) {
                    e.preventDefault();
                    var blob = items[i].getAsFile();
                    if (blob) {
                        self.uploadFile(blob);
                    }
                }
            }
        };

        this.$visualEditor.on('paste', pasteHandler);
        this.$textarea.on('paste', pasteHandler);
    };

    ForumEditor.prototype.uploadFile = function(file) {
        var self = this;
        var uploadId = 'upload_' + Math.random().toString(36).substr(2, 9);
        var filename = file.name || 'image.jpg';

        // Check raw size before upload (10 MB limit)
        if (file.size > 10 * 1024 * 1024) {
            alert('Файл «' + filename + '» превышает 10 МБ. Пожалуйста, сожмите изображение или используйте сторонний сервис.');
            return;
        }

        // Insert placeholder
        self.$uploadProgress.removeClass('d-none');
        var placeholderMd = '![Загрузка ' + filename + '...]()';

        if (self.currentMode === 'visual') {
            self.$visualEditor.focus();
            var placeholderHtml = '<div class="forum-img-uploading-placeholder" id="' + uploadId + '"><i class="fa fa-spinner fa-spin mr-2"></i> Загрузка ' + escapeHtml(filename) + '...</div><p><br></p>';
            document.execCommand('insertHTML', false, placeholderHtml);
        } else {
            wrapTextareaSelection(self.$textarea, '\n', placeholderMd + '\n', '');
        }

        var formData = new FormData();
        formData.append('file', file);
        formData.append('csrfmiddlewaretoken', getCsrfToken());

        $.ajax({
            url: self.options.uploadUrl,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                'X-CSRFToken': getCsrfToken()
            },
            success: function(response) {
                self.$uploadProgress.addClass('d-none');
                if (response.success && response.url) {
                    var imgUrl = response.url;
                    var altText = response.filename || filename;

                    if (self.currentMode === 'visual') {
                        var $ph = $('#' + uploadId);
                        var imgHtml = '<p><img src="' + escapeHtml(imgUrl) + '" alt="' + escapeHtml(altText) + '" class="forum-embedded-img"></p><p><br></p>';
                        if ($ph.length) {
                            $ph.replaceWith(imgHtml);
                        } else {
                            document.execCommand('insertHTML', false, imgHtml);
                        }
                        self.syncMarkdownFromVisual();
                    } else {
                        var currentVal = self.$textarea.val();
                        var finalMd = '![' + altText + '](' + imgUrl + ')';
                        if (currentVal.indexOf(placeholderMd) !== -1) {
                            self.$textarea.val(currentVal.replace(placeholderMd, finalMd));
                        } else {
                            self.insertMarkdown(finalMd);
                        }
                    }
                    self.updateCharCounter();
                } else {
                    self.handleUploadError(uploadId, placeholderMd, response.error || 'Ошибка при загрузке изображения.');
                }
            },
            error: function(xhr) {
                self.$uploadProgress.addClass('d-none');
                var err = 'Ошибка при загрузке изображения.';
                try {
                    var json = JSON.parse(xhr.responseText);
                    if (json && json.error) err = json.error;
                } catch(e) {}
                self.handleUploadError(uploadId, placeholderMd, err);
            }
        });
    };

    ForumEditor.prototype.handleUploadError = function(uploadId, placeholderMd, errorMessage) {
        if (this.currentMode === 'visual') {
            $('#' + uploadId).remove();
            this.syncMarkdownFromVisual();
        } else {
            var currentVal = this.$textarea.val();
            this.$textarea.val(currentVal.replace(placeholderMd, ''));
        }
        alert(errorMessage);
        this.updateCharCounter();
    };

    ForumEditor.prototype.initResizer = function() {
        var self = this;
        var $resizer = this.$wrapper.find('.forum-editor-resizer');
        if (!$resizer.length) return;

        var $doc = $(document);
        var $body = $('body');

        function startResize(startY) {
            var startHeight = self.currentMode === 'markdown' ? self.$textarea.outerHeight() : self.$visualEditor.outerHeight();
            $body.css('user-select', 'none');
            $doc.css('cursor', 'se-resize');

            function onMove(clientY) {
                var delta = clientY - startY;
                var newHeight = Math.max(140, startHeight + delta);
                self.$visualEditor.css({'height': newHeight + 'px', 'max-height': 'none'});
                self.$textarea.css({'height': newHeight + 'px', 'max-height': 'none'});
            }

            function onMouseMove(e) {
                onMove(e.clientY);
            }

            function onTouchMove(e) {
                if (e.originalEvent && e.originalEvent.touches && e.originalEvent.touches.length) {
                    onMove(e.originalEvent.touches[0].clientY);
                }
            }

            function onEnd() {
                $doc.off('mousemove', onMouseMove)
                    .off('mouseup', onEnd)
                    .off('touchmove', onTouchMove)
                    .off('touchend', onEnd)
                    .css('cursor', '');
                $body.css('user-select', '');
            }

            $doc.on('mousemove', onMouseMove)
                .on('mouseup', onEnd)
                .on('touchmove', onTouchMove)
                .on('touchend', onEnd);
        }

        $resizer.on('mousedown', function(e) {
            e.preventDefault();
            startResize(e.clientY);
        }).on('touchstart', function(e) {
            if (e.originalEvent && e.originalEvent.touches && e.originalEvent.touches.length) {
                startResize(e.originalEvent.touches[0].clientY);
            }
        });
    };

    // Auto-initialize when DOM is ready
    $(function() {
        if ($('#id_body').length) {
            new ForumEditor({
                textareaSelector: '#id_body',
                uploadUrl: '/forum/upload-image/'
            });
        }
    });

})(window, document, jQuery);
