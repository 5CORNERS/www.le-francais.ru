/**
 * Forum Modern WYSIWYG & Markdown Editor
 * Supports bidirectional switching, image upload (Drag&Drop, Clipboard paste),
 * and custom pymdownx formatting (^^underline^^, ~~strike~~, ==mark==, ++keys++, ^sup^, ~sub~, ???- spoilers).
 */
(function(window, document, $) {
    'use strict';

    // Popular emojis list for picker
    var EMOJIS = [
        '😀', '😃', '😄', '😁', '😆', '😅', '😂', '🤣', '😊', '😇',
        '🙂', '🙃', '😉', '😌', '😍', '🥰', '😘', '😋', '😛', '😜',
        '🤪', '😝', '🤗', '🤭', '🤫', '🤔', '🤐', '🤨', '😐', '😑',
        '😶', '😏', '😒', '🙄', '😬', '🤥', '😌', '😔', '😪', '🤤',
        '😴', '😷', '🤒', '🤕', '🤢', '🤮', '🤧', '🥵', '🥶', '🥴',
        '😵', '🤯', '🤠', '🥳', '😎', '🤓', '🧐', '😕', '😟', '🙁',
        '😮', '😯', '😲', '😳', '🥺', '😦', '😧', '😨', '😰', '😥',
        '😢', '😭', '😱', '😖', '😣', '😞', '😓', '😩', '😫', '🥱',
        '😤', '😡', '😠', '🤬', '😈', '👿', '💀', '💩', '🤡', '👻',
        '👏', '👍', '👎', '👊', '✊', '🤛', '🤜', '🤞', '✌️', '🤟',
        '👌', '👈', '👉', '👆', '👇', '☝️', '✋', '👋', '💪', '🙏',
        '❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '💔', '❣️',
        '💕', '💞', '💓', '💗', '💖', '💘', '💝', '☕', '🥖', '🥐',
        '🍷', '🧀', '🇫🇷', '🇷🇺', '🇬🇧', '🎉', '💡', '✍️', '📚', '❓', '❗'
    ];

    function escapeHtml(str) {
        return (str || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
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
        text = text.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" class="forum-embedded-img">');

        // Links: [text](url)
        text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');

        // Custom formatting
        // Keystrokes: ++ctrl+c++
        text = text.replace(/\+\+([^+]+)\+\+/g, '<kbd class="editor-key">$1</kbd>');

        // Highlight: ==text==
        text = text.replace(/==([^=]+)==/g, '<mark class="editor-mark">$1</mark>');

        // Underline: ^^text^^
        text = text.replace(/\^\^([^^]+)\^\^/g, '<u class="editor-underline">$1</u>');

        // Strikethrough: ~~text~~
        text = text.replace(/~~([^~]+)~~/g, '<del class="editor-del">$1</del>');

        // Superscript: ^text^
        text = text.replace(/\^([^\s^]+)\^/g, '<sup>$1</sup>');

        // Subscript: ~text~
        text = text.replace(/~([^\s~]+)~/g, '<sub>$1</sub>');

        // Bold italic: ***text***
        text = text.replace(/\*\*\*([^*]+)\*\*\*/g, '<strong><em>$1</em></strong>');

        // Bold: **text**
        text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

        // Italic: *text*
        text = text.replace(/\*([^*]+)\*/g, '<em>$1</em>');

        // Lists
        text = text.replace(/^[-*]\s+(.*)$/gim, '<li>$1</li>');
        text = text.replace(/((?:<li>.*<\/li>\s*)+)/g, '<ul>$1</ul>');

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
            if (b.startsWith('<blockquote') || b.startsWith('<details') || b.startsWith('<h1') || b.startsWith('<h2') || b.startsWith('<h3') || b.startsWith('<ul') || b.startsWith('<pre') || b.startsWith('<hr')) {
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
                    return childrenText.trim() ? '++' + childrenText.trim() + '++' : '';
                case 'span':
                    if (node.classList && node.classList.contains('keys')) {
                        return '++' + node.textContent.trim() + '++';
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
        this.init();
    }

    ForumEditor.prototype.init = function() {
        var self = this;

        // Prevent legacy markItUp from initializing
        this.$textarea.addClass('no-markitup forum-markdown-textarea');

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

        // Expose public instance
        window.forumEditor = this;
    };

    ForumEditor.prototype.buildUI = function() {
        var emojiItemsHtml = EMOJIS.map(function(emoji) {
            return '<span class="forum-emoji-item" data-emoji="' + emoji + '" title="' + emoji + '">' + emoji + '</span>';
        }).join('');

        var toolbarHtml = [
            '<div class="forum-editor-wrapper">',
                '<div class="forum-editor-toolbar">',
                    // Formatting
                    '<div class="btn-group btn-group-sm mr-1 mb-1" role="group">',
                        '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="bold" title="Жирный (**текст**)"><i class="fa fa-bold"></i></button>',
                        '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="italic" title="Курсив (*текст*)"><i class="fa fa-italic"></i></button>',
                        '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="underline" title="Подчеркнутый (^^текст^^)"><i class="fa fa-underline"></i></button>',
                        '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="strikethrough" title="Зачеркнутый (~~текст~~)"><i class="fa fa-strikethrough"></i></button>',
                        '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="mark" title="Выделение маркером (==текст==)"><i class="fa fa-pencil" style="background:#fff3cd;padding:1px 3px;border-radius:2px;"></i></button>',
                    '</div>',
                    // Script / Keys
                    '<div class="btn-group btn-group-sm mr-1 mb-1" role="group">',
                        '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="superscript" title="Верхний индекс (^текст^)"><i class="fa fa-superscript"></i></button>',
                        '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="subscript" title="Нижний индекс (~текст~)"><i class="fa fa-subscript"></i></button>',
                        '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="kbd" title="Клавиша (++клавиша++)"><i class="fa fa-keyboard-o"></i></button>',
                    '</div>',
                    // Structure
                    '<div class="btn-group btn-group-sm mr-1 mb-1" role="group">',
                        '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="h2" title="Подзаголовок (## Заголовок)"><strong>H2</strong></button>',
                        '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="h3" title="Подзаголовок (### Заголовок)"><strong>H3</strong></button>',
                        '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="quote" title="Цитата (> текст)"><i class="fa fa-quote-left"></i></button>',
                        '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="ul" title="Список (- пункт)"><i class="fa fa-list-ul"></i></button>',
                        '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="ol" title="Нумерованный список (1. пункт)"><i class="fa fa-list-ol"></i></button>',
                        '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="spoiler" title="Спойлер (???- Заголовок)"><i class="fa fa-caret-square-o-down"></i> Спойлер</button>',
                        '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="code" title="Код (`код`)"><i class="fa fa-code"></i></button>',
                    '</div>',
                    // Insert
                    '<div class="btn-group btn-group-sm mr-1 mb-1" role="group">',
                        '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="link" title="Вставить ссылку"><i class="fa fa-link"></i></button>',
                        '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="image" title="Вставить или загрузить изображение"><i class="fa fa-picture-o"></i> Картинка</button>',
                        '<div class="btn-group btn-group-sm" role="group">',
                            '<button type="button" class="btn btn-light forum-editor-btn dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" title="Вставить эмодзи"><i class="fa fa-smile-o"></i></button>',
                            '<div class="dropdown-menu forum-emoji-dropdown">' + emojiItemsHtml + '</div>',
                        '</div>',
                    '</div>',
                    // Mode Switcher
                    '<div class="btn-group btn-group-sm mb-1 forum-mode-switcher" role="group">',
                        '<button type="button" class="btn btn-primary active forum-mode-btn" data-mode="visual" title="Визуальный WYSIWYG редактор"><i class="fa fa-eye mr-1"></i>Визуальный</button>',
                        '<button type="button" class="btn btn-light forum-mode-btn" data-mode="markdown" title="Исходный Markdown код"><i class="fa fa-code mr-1"></i>Markdown</button>',
                    '</div>',
                '</div>',
                // Hidden file input
                '<input type="file" class="forum-image-file-input d-none" accept="image/jpeg,image/png,image/gif,image/webp">',
                // Editor body container
                '<div class="forum-editor-container position-relative">',
                    '<div class="forum-visual-editor form-control" contenteditable="true" spellcheck="true" placeholder="Напишите ответ или перетащите изображение сюда..."></div>',
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
                    '<small class="text-muted font-italic forum-char-counter"></small>',
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
        this.$wrapper.find('.forum-mode-btn[data-mode="visual"]')
            .toggleClass('btn-primary active', isVisual)
            .toggleClass('btn-light', !isVisual);
        this.$wrapper.find('.forum-mode-btn[data-mode="markdown"]')
            .toggleClass('btn-primary active', !isVisual)
            .toggleClass('btn-light', isVisual);
    };

    ForumEditor.prototype.setMode = function(newMode) {
        if (newMode === this.currentMode) return;

        if (newMode === 'markdown') {
            // Convert Visual HTML -> Markdown
            var md = htmlToMarkdown(this.$visualEditor[0]);
            this.$textarea.val(md);
            this.$visualEditor.hide();
            this.$textarea.show().focus();
            this.currentMode = 'markdown';
        } else {
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

        // Mode switch buttons
        this.$wrapper.on('click', '.forum-mode-btn', function(e) {
            e.preventDefault();
            var mode = $(this).data('mode');
            self.setMode(mode);
        });

        // Toolbar formatting buttons
        this.$wrapper.on('click', '.forum-editor-btn[data-cmd]', function(e) {
            e.preventDefault();
            var cmd = $(this).data('cmd');
            self.executeCommand(cmd);
        });

        // Emoji buttons
        this.$wrapper.on('click', '.forum-emoji-item', function(e) {
            e.preventDefault();
            var emoji = $(this).data('emoji');
            self.insertEmoji(emoji);
        });

        // Live sync on input
        this.$visualEditor.on('input', function() {
            self.updateCharCounter();
        });
        this.$textarea.on('input', function() {
            self.updateCharCounter();
        });

        // Sync before form submit
        this.$textarea.closest('form').on('submit', function() {
            self.syncMarkdownFromVisual();
        });
    };

    ForumEditor.prototype.executeCommand = function(cmd) {
        if (this.currentMode === 'visual') {
            this.executeVisualCommand(cmd);
        } else {
            this.executeMarkdownCommand(cmd);
        }
        this.updateCharCounter();
    };

    ForumEditor.prototype.executeVisualCommand = function(cmd) {
        this.$visualEditor.focus();
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

    ForumEditor.prototype.insertEmoji = function(emoji) {
        if (this.currentMode === 'visual') {
            this.$visualEditor.focus();
            document.execCommand('insertText', false, emoji);
        } else {
            wrapTextareaSelection(this.$textarea, '', emoji, '');
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
        } else {
            var currentVal = this.$textarea.val();
            this.$textarea.val(currentVal.replace(placeholderMd, ''));
        }
        alert(errorMessage);
        this.updateCharCounter();
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
