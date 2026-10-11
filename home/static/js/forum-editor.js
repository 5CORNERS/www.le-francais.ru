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

        // Spoilers: ???- "Title"\n(    body)*
        text = text.replace(/\?\?\?[-+]?\s*"([^"\n]+)"\n((?:(?:    |\t).*\n?)+)/g, function(match, title, body) {
            var cleanBody = body.replace(/^(?:    |\t)/gm, '');
            return '\n<details class="forum-spoiler" open><summary>' + escapeHtml(title) + '</summary><div class="spoiler-body">' + markdownToHtml(cleanBody) + '</div></details>\n';
        });

        // Indented code blocks (4 spaces or tab at start of lines, after spoilers are extracted)
        text = text.replace(/(^|\n\n)((?:(?:    |\t)[^\n]*(?:\n|$))+)/g, function(match, lead, block) {
            var code = block.replace(/^(?:    |\t)/gm, '').replace(/\n+$/, '');
            var id = '___CODEBLOCK_' + codeBlocks.length + '___';
            codeBlocks.push({ lang: '', code: code });
            return lead + id + '\n\n';
        });

        // Protect inline code
        var inlineCodes = [];
        text = text.replace(/`([^`\n]+)`/g, function(match, code) {
            var id = '___INLINECODE_' + inlineCodes.length + '___';
            inlineCodes.push(code);
            return id;
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

        // Images: ![alt](url "title") or ![alt](url)
        text = text.replace(/!\[([^\]]*)\]\(([^)\s]+)(?:\s+["']([^"']*)["'])?\)/g, function(match, alt, url, title) {
            var finalTitle = (title !== undefined) ? title : (alt || '');
            var titleAttr = ' title="' + escapeHtml(finalTitle) + '"';
            return '<img src="' + sanitizeUrl(url) + '" alt="' + escapeHtml(alt) + '"' + titleAttr + ' class="forum-embedded-img">';
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

        // Bold italic: ***text*** or ___text___
        text = text.replace(/\*\*\*([^*]+)\*\*\*/g, '<strong><em>$1</em></strong>');
        text = text.replace(/___([^_]+)___/g, '<strong><em>$1</em></strong>');

        // Bold: **text** or __text__
        text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        text = text.replace(/__([^_]+)__/g, '<strong>$1</strong>');

        // Italic: *text* (emulate negative lookbehind with capture group for cross-browser support)
        text = text.replace(/(^|[^*])\*([^\s*][^*\n]*?[^\s*]|\S)\*(?!\*)/g, '$1<em>$2</em>');

        // Italic: _text_ (support Latin, Cyrillic, French accents, punctuation around)
        var wordChars = 'a-zA-Z0-9\\u00C0-\\u024F\\u0400-\\u04FF';
        var reItalicUnder = new RegExp('(^|[^' + wordChars + '_])_([^\\s_][^_\\n]*?[^\\s_]|[^\\s_])_(?=[^' + wordChars + '_]|$)', 'g');
        text = text.replace(reItalicUnder, '$1<em>$2</em>');

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

        var html = res.filter(Boolean).join('');
        if (!html || html.endsWith('</blockquote>') || html.endsWith('</details>') || html.endsWith('</pre>')) {
            html += '<p><br></p>';
        }
        return html;
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
                    return childrenText.trim() ? '_' + childrenText.trim() + '_' : '';
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
                    var title = node.getAttribute('title');
                    if (title === null || title === undefined) {
                        title = alt;
                    }
                    return '![' + alt + '](' + src + ' "' + title + '")';
                case 'br':
                    return '\n';
                case 'hr':
                    return '\n---\n\n';
                case 'blockquote':
                    var lines = childrenText.trim().split('\n');
                    return lines.map(function(l) { return '> ' + l; }).join('\n') + '\n\n';
                case 'details':
                    var summaryNode = node.querySelector('summary');
                    var summary = summaryNode ? summaryNode.textContent.trim() : '';
                    if (!summary) summary = 'Спойлер';
                    var bodyNode = node.querySelector('.spoiler-body') || node;
                    var bodyMd = '';
                    for (var j = 0; j < bodyNode.childNodes.length; j++) {
                        var child = bodyNode.childNodes[j];
                        if (child.tagName && child.tagName.toLowerCase() === 'summary') continue;
                        bodyMd += walk(child);
                    }
                    var bodyTrimmed = bodyMd.trim();
                    if (!bodyTrimmed) bodyTrimmed = 'Текст спойлера';
                    var bodyLines = bodyTrimmed.split('\n').map(function(l) { return '    ' + l; }).join('\n');
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

        return walk(domRoot).replace(/\u00A0/g, ' ').trim();
    }

    /**
     * Ensures an unstyled spacer exists after an inline tag if it's at the end of its parent container.
     */
    function ensureTrailingSpacer(inlineNode) {
        if (!inlineNode || !inlineNode.parentNode) return;
        var topInline = inlineNode;
        while (topInline.parentNode && !/^(p|div|li|blockquote|summary|details|body)$/i.test(topInline.parentNode.tagName) && !(topInline.parentNode.classList && topInline.parentNode.classList.contains('forum-visual-editor'))) {
            topInline = topInline.parentNode;
        }
        var next = topInline.nextSibling;
        if (!next || next.nodeName.toLowerCase() === 'br' || (next.nodeType === 3 && next.nodeValue === '')) {
            var spacer = document.createTextNode('\u00A0');
            topInline.parentNode.insertBefore(spacer, next);
        }
    }

    /**
     * Checks if the collapsed range is at the end of the inline node.
     */
    function isAtEndOfInlineNode(range, node) {
        if (!range || !range.collapsed || !node) return false;
        var container = range.startContainer;
        var offset = range.startOffset;
        if (container.nodeType === 3) {
            if (offset < container.textContent.length) return false;
            var curr = container;
            while (curr && curr !== node) {
                var next = curr.nextSibling;
                while (next) {
                    if (next.textContent && next.textContent.length > 0) return false;
                    next = next.nextSibling;
                }
                curr = curr.parentNode;
            }
            return true;
        } else {
            return offset >= node.childNodes.length;
        }
    }

    /**
     * Moves cursor outside of the inline tag into a trailing spacer.
     */
    function exitInlineTag(inlineNode) {
        if (!inlineNode || !inlineNode.parentNode) return;
        var topInline = inlineNode;
        while (topInline.parentNode && !/^(p|div|li|blockquote|summary|details|body)$/i.test(topInline.parentNode.tagName) && !(topInline.parentNode.classList && topInline.parentNode.classList.contains('forum-visual-editor'))) {
            topInline = topInline.parentNode;
        }
        ensureTrailingSpacer(topInline);
        var sel = window.getSelection();
        if (!sel) return;
        var r = document.createRange();
        if (topInline.nextSibling && topInline.nextSibling.nodeType === 3) {
            var val = topInline.nextSibling.nodeValue || '';
            var targetOffset = (val.length > 0 && (/^\s/.test(val) || val.charCodeAt(0) === 160)) ? 1 : 0;
            r.setStart(topInline.nextSibling, targetOffset);
            r.collapse(true);
        } else {
            r.setStartAfter(topInline);
            r.collapse(true);
        }
        sel.removeAllRanges();
        sel.addRange(r);
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
     * Toggles custom inline formatting tag (mark, code, kbd) on selection.
     * If cursor/selection is inside the tag, it unwraps it (toggle off).
     * If text is selected, wraps it while keeping content selected (stackable).
     * If collapsed, inserts placeholder and selects it.
     */
    function toggleCustomInlineTag(tagName, className, placeholder) {
        var sel = window.getSelection();
        if (!sel || !sel.rangeCount) return;
        var range = sel.getRangeAt(0);
        var tagLower = tagName.toLowerCase();

        // 1. Check if inside tagName
        var container = range.commonAncestorContainer;
        var tagNode = (container.nodeType === 1 ? container : container.parentNode).closest(tagLower);

        if (tagNode && tagNode.closest('.forum-visual-editor')) {
            // If collapsed at the end of the tag: clicking button exits the tag!
            if (range.collapsed && isAtEndOfInlineNode(range, tagNode)) {
                exitInlineTag(tagNode);
                return;
            }

            // Unwrap tag
            var parent = tagNode.parentNode;
            var firstChild = tagNode.firstChild;
            var lastChild = tagNode.lastChild;
            while (tagNode.firstChild) {
                parent.insertBefore(tagNode.firstChild, tagNode);
            }
            parent.removeChild(tagNode);

            if (firstChild && lastChild) {
                var newRange = document.createRange();
                newRange.setStartBefore(firstChild);
                newRange.setEndAfter(lastChild);
                sel.removeAllRanges();
                sel.addRange(newRange);
            }
            return;
        }

        // If toggling sup or sub, unwrap opposite tag if currently inside it
        if (tagLower === 'sup' || tagLower === 'sub') {
            var oppTag = tagLower === 'sup' ? 'sub' : 'sup';
            var oppNode = (container.nodeType === 1 ? container : container.parentNode).closest(oppTag);
            if (oppNode && oppNode.closest('.forum-visual-editor')) {
                var oppParent = oppNode.parentNode;
                while (oppNode.firstChild) {
                    oppParent.insertBefore(oppNode.firstChild, oppNode);
                }
                oppParent.removeChild(oppNode);
            }
        }

        // 2. Check if selected content contains tagName elements
        if (!range.collapsed) {
            var clone = range.cloneContents();
            var existingTags = clone.querySelectorAll(tagLower);
            if (existingTags.length > 0) {
                var frag = range.extractContents();
                var matching = frag.querySelectorAll(tagLower);
                for (var m = 0; m < matching.length; m++) {
                    var el = matching[m];
                    var p = el.parentNode;
                    while (el.firstChild) {
                        p.insertBefore(el.firstChild, el);
                    }
                    p.removeChild(el);
                }
                var firstNode = frag.firstChild;
                var lastNode = frag.lastChild;
                range.insertNode(frag);
                if (firstNode && lastNode) {
                    var newRange = document.createRange();
                    newRange.setStartBefore(firstNode);
                    newRange.setEndAfter(lastNode);
                    sel.removeAllRanges();
                    sel.addRange(newRange);
                }
                return;
            }
        }

        // 3. Wrap selection or insert placeholder
        var newEl = document.createElement(tagName);
        if (className) newEl.className = className;

        if (!range.collapsed) {
            newEl.appendChild(range.extractContents());
            range.insertNode(newEl);

            ensureTrailingSpacer(newEl);

            var newRange = document.createRange();
            newRange.selectNodeContents(newEl);
            sel.removeAllRanges();
            sel.addRange(newRange);
        } else {
            var text = placeholder || 'текст';
            newEl.textContent = text;
            range.insertNode(newEl);

            ensureTrailingSpacer(newEl);

            var newRange = document.createRange();
            newRange.selectNodeContents(newEl);
            sel.removeAllRanges();
            sel.addRange(newRange);
        }
    }

    /**
     * Clears formatting in Visual Editor (native removeFormat + unwrap custom tags)
     */
    function clearFormattingVisual(editorEl) {
        document.execCommand('removeFormat', false, null);
        document.execCommand('unlink', false, null);

        var sel = window.getSelection();
        if (!sel || !sel.rangeCount) return;
        var range = sel.getRangeAt(0);

        var tagsToRemove = ['kbd', 'mark', 'code', 'u', 'del', 's', 'strike', 'sup', 'sub', 'strong', 'b', 'em', 'i'];
        var container = range.commonAncestorContainer;
        var root = container.nodeType === 1 ? container : container.parentNode;

        // Check if inside pre (code block)
        var pre = root.closest('pre');
        if (pre && editorEl.contains(pre)) {
            if (window.forumEditor && window.forumEditor.unwrapCodeBlock) {
                window.forumEditor.unwrapCodeBlock(pre);
                return;
            }
        }

        // Check ancestors within editor
        tagsToRemove.forEach(function(tag) {
            var el = root.closest(tag);
            if (el && editorEl.contains(el)) {
                var p = el.parentNode;
                while (el.firstChild) {
                    p.insertBefore(el.firstChild, el);
                }
                p.removeChild(el);
            }
        });

        // Check descendants in selection
        if (!range.collapsed) {
            var frag = range.extractContents();
            tagsToRemove.forEach(function(tag) {
                var matching = frag.querySelectorAll(tag);
                for (var m = 0; m < matching.length; m++) {
                    var el = matching[m];
                    var p = el.parentNode;
                    while (el.firstChild) {
                        p.insertBefore(el.firstChild, el);
                    }
                    p.removeChild(el);
                }
            });
            range.insertNode(frag);
        }
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
            this.updateSpoilerPlaceholders();
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
                        // Inline text formatting
                        '<div class="btn-group btn-group-sm" role="group">',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="bold" title="Жирный (**текст**, Ctrl+B)"><i class="fa fa-bold"></i></button>',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="italic" title="Курсив (_текст_, Ctrl+I)"><i class="fa fa-italic"></i></button>',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="underline" title="Подчеркнутый (^^текст^^, Ctrl+U)"><i class="fa fa-underline"></i></button>',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="strikethrough" title="Зачеркнутый (~~текст~~, Ctrl+Shift+X, Alt+Shift+5)"><i class="fa fa-strikethrough"></i></button>',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="mark" title="Выделение маркером (==текст==)"><i class="fa fa-pencil" style="background:#fff3cd;padding:1px 3px;border-radius:2px;"></i></button>',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="code" title="Код / блок кода (`код` в строке, ```блок``` для нескольких строк, Ctrl+Shift+M)"><i class="fa fa-code"></i></button>',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="kbd" title="Клавиша (++клавиша++)"><i class="fa fa-keyboard-o"></i></button>',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="superscript" title="Верхний индекс (^текст^)"><i class="fa fa-superscript"></i></button>',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="subscript" title="Нижний индекс (~текст~)"><i class="fa fa-subscript"></i></button>',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="removeFormat" title="Очистить форматирование (Ctrl+Shift+N, Ctrl+\\)"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px;"><path d="M5 6h14"></path><path d="M12 6v12"></path><line x1="4" y1="4" x2="20" y2="20" stroke="currentColor" stroke-width="2.2"></line></svg></button>',
                        '</div>',
                        // Structure / Block tools
                        '<div class="btn-group btn-group-sm" role="group">',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="h2" title="Подзаголовок (## Заголовок)"><strong>H2</strong></button>',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="h3" title="Подзаголовок (### Заголовок)"><strong>H3</strong></button>',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="quote" title="Цитата (> текст, Ctrl+Shift+.)"><i class="fa fa-quote-left"></i></button>',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="ul" title="Список (- пункт)"><i class="fa fa-list-ul"></i></button>',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="ol" title="Нумерованный список (1. пункт)"><i class="fa fa-list-ol"></i></button>',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="spoiler" title="Спойлер (???- Заголовок, Ctrl+Shift+P)"><i class="fa fa-caret-square-o-down"></i></button>',
                        '</div>',
                        // Insert
                        '<div class="btn-group btn-group-sm" role="group">',
                            '<button type="button" class="btn btn-light forum-editor-btn" data-cmd="link" title="Вставить ссылку (Ctrl+K)"><i class="fa fa-link"></i></button>',
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
                // Custom Modal Dialog Overlay for Link & Image Insertion
                '<div class="forum-editor-modal-overlay d-none">',
                    '<div class="forum-editor-modal" role="dialog" aria-modal="true">',
                        '<div class="forum-editor-modal-header">',
                            '<h5 class="forum-editor-modal-title">Вставить ссылку</h5>',
                            '<button type="button" class="forum-editor-modal-close" aria-label="Закрыть">&times;</button>',
                        '</div>',
                        '<div class="forum-editor-modal-body"></div>',
                        '<div class="forum-editor-modal-footer">',
                            '<button type="button" class="btn btn-sm btn-secondary forum-editor-modal-cancel">Отмена</button>',
                            '<button type="button" class="btn btn-sm btn-primary forum-editor-modal-submit">Вставить</button>',
                        '</div>',
                    '</div>',
                '</div>',
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
        this.$modalOverlay = this.$wrapper.find('.forum-editor-modal-overlay');
        this.$modalTitle = this.$wrapper.find('.forum-editor-modal-title');
        this.$modalBody = this.$wrapper.find('.forum-editor-modal-body');

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
            this.updateSpoilerPlaceholders();
            this.$textarea.hide();
            this.$visualEditor.show().focus();
            this.currentMode = 'visual';
        }

        localStorage.setItem('forum_editor_mode', this.currentMode);
        this.updateModeButtons();
        this.updateCharCounter();
    };

    ForumEditor.prototype.updateSpoilerPlaceholders = function() {
        if (!this.$visualEditor || !this.$visualEditor.length) return;
        this.$visualEditor.find('details.forum-spoiler').each(function() {
            var $summary = $(this).find('summary');
            var sText = $.trim($summary.text());
            $summary.attr('data-empty', sText ? 'false' : 'true');

            var $body = $(this).find('.spoiler-body');
            var bText = $.trim($body.text());
            var hasImg = $body.find('img').length > 0;
            $body.attr('data-empty', (bText || hasImg) ? 'false' : 'true');
        });
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
        this.updateSpoilerPlaceholders();
        this.updateCharCounter();
    };

    ForumEditor.prototype.insertQuote = function(quoteMd) {
        if (!quoteMd) return;

        if (this.currentMode === 'visual') {
            var targetRange = this.savedRange ? this.savedRange.cloneRange() : null;
            this.$visualEditor.focus();

            var quoteHtml = markdownToHtml(quoteMd).trim();
            var tempDiv = document.createElement('div');
            tempDiv.innerHTML = quoteHtml;

            var bqElement = tempDiv.querySelector('blockquote');
            if (!bqElement) {
                bqElement = document.createElement('blockquote');
                while (tempDiv.firstChild) {
                    bqElement.appendChild(tempDiv.firstChild);
                }
            }

            var trailingP = document.createElement('p');
            trailingP.innerHTML = '<br>';

            var sel = window.getSelection();
            var inserted = false;

            if (targetRange && this.$visualEditor[0].contains(targetRange.commonAncestorContainer)) {
                var container = targetRange.startContainer;
                var currentBlock = container.nodeType === 1 ? container : container.parentNode;
                while (currentBlock && currentBlock.parentNode && currentBlock.parentNode !== this.$visualEditor[0]) {
                    currentBlock = currentBlock.parentNode;
                }

                if (currentBlock && currentBlock.parentNode === this.$visualEditor[0]) {
                    var blockText = $.trim(currentBlock.textContent);
                    var hasImg = currentBlock.querySelector && currentBlock.querySelector('img');

                    if (!blockText && !hasImg) {
                        // Current paragraph is empty, replace it with blockquote and trailingP
                        this.$visualEditor[0].insertBefore(bqElement, currentBlock);
                        this.$visualEditor[0].insertBefore(trailingP, currentBlock);
                        currentBlock.parentNode.removeChild(currentBlock);
                        inserted = true;
                    } else {
                        // Current block has text: split at cursor!
                        var afterRange = document.createRange();
                        try {
                            afterRange.setStart(targetRange.endContainer, targetRange.endOffset);
                            afterRange.setEndAfter(currentBlock.lastChild || currentBlock);
                            var afterFrag = afterRange.extractContents();

                            // Insert blockquote after currentBlock
                            if (currentBlock.nextSibling) {
                                this.$visualEditor[0].insertBefore(bqElement, currentBlock.nextSibling);
                            } else {
                                this.$visualEditor[0].appendChild(bqElement);
                            }

                            // If there was text after cursor, put it in trailingP
                            var afterText = $.trim(afterFrag.textContent);
                            var afterHasImg = afterFrag.querySelector && afterFrag.querySelector('img');
                            if (afterText || afterHasImg) {
                                trailingP.innerHTML = '';
                                trailingP.appendChild(afterFrag);
                            }

                            if (bqElement.nextSibling) {
                                this.$visualEditor[0].insertBefore(trailingP, bqElement.nextSibling);
                            } else {
                                this.$visualEditor[0].appendChild(trailingP);
                            }
                            inserted = true;
                        } catch (e) {
                            inserted = false;
                        }
                    }
                }
            }

            if (!inserted) {
                this.$visualEditor.append(bqElement);
                this.$visualEditor.append(trailingP);
            }

            // Move cursor directly into trailingP outside the quote
            if (sel) {
                var r = document.createRange();
                r.setStart(trailingP, 0);
                r.collapse(true);
                sel.removeAllRanges();
                sel.addRange(r);
                this.savedRange = r.cloneRange();
            }

            this.syncMarkdownFromVisual();
            this.updateCharCounter();
        } else {
            var el = this.$textarea[0];
            var val = el.value;
            var start = (typeof this.savedMarkdownCursor === 'number') ? this.savedMarkdownCursor : el.selectionStart;
            if (typeof start !== 'number' || start < 0 || start > val.length) {
                start = val.length;
            }

            var before = val.substring(0, start);
            var after = val.substring(start);
            var prefix = '';
            if (before.length > 0 && !before.endsWith('\n')) {
                prefix = before.endsWith('\n\n') ? '' : (before.endsWith('\n') ? '\n' : '\n\n');
            }
            var suffix = '';
            if (after.length > 0 && !after.startsWith('\n')) {
                suffix = '\n\n';
            }
            var cleanMd = quoteMd.trim();
            var replacement = prefix + cleanMd + '\n\n' + suffix;
            el.value = before + replacement + after;
            var newPos = before.length + prefix.length + cleanMd.length + 2;
            el.focus();
            el.setSelectionRange(newPos, newPos);
            this.savedMarkdownCursor = newPos;

            this.$textarea.trigger('input');
            this.updateCharCounter();
        }
    };

    ForumEditor.prototype.insertMarkdown = function(md) {
        if (!md) return;
        if (md.trim().startsWith('>')) {
            this.insertQuote(md);
        } else {
            if (this.currentMode === 'visual') {
                this.$visualEditor.focus();
                if (this.savedRange) {
                    this.restoreSelection();
                }
                var html = markdownToHtml(md);
                document.execCommand('insertHTML', false, html);
                this.saveSelection();
                this.syncMarkdownFromVisual();
                this.updateCharCounter();
            } else {
                this.insertQuote(md);
            }
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

        // Save selection on cursor movement / click in visual editor (without blur/focus resetting it)
        this.$visualEditor.on('mouseup keyup touchend input', function() {
            self.saveSelection();
        });
        $(document).on('mouseup.forumEditor touchend.forumEditor selectionchange.forumEditor', function() {
            if (self.currentMode === 'visual') {
                self.saveSelection();
            }
        });

        // Track cursor position in markdown mode
        this.$textarea.on('mouseup keyup touchend input', function() {
            self.savedMarkdownCursor = this.selectionStart;
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

        // Modal overlay event handlers
        this.$modalOverlay.on('click', '.forum-editor-modal-close, .forum-editor-modal-cancel', function(e) {
            e.preventDefault();
            self.closeModal();
        });

        this.$modalOverlay.on('click', '.forum-editor-modal-submit', function(e) {
            e.preventDefault();
            if (self.activeModalSubmit) {
                self.activeModalSubmit();
            }
        });

        this.$modalOverlay.on('click', function(e) {
            if ($(e.target).hasClass('forum-editor-modal-overlay')) {
                self.closeModal();
            }
        });

        this.$modalOverlay.on('keydown', function(e) {
            if (e.key === 'Escape' || e.keyCode === 27) {
                e.preventDefault();
                self.closeModal();
            } else if (e.key === 'Enter' || e.keyCode === 13) {
                if ($(e.target).is('input')) {
                    e.preventDefault();
                    if (self.activeModalSubmit) {
                        self.activeModalSubmit();
                    }
                }
            }
        });

        // Keyboard shortcuts (Telegram-style shortcuts, Ctrl+K for link, protect dead keys)
        var handleKeydown = function(e) {
            // Free dead key: Never intercept Ctrl+Shift+6 (or Ctrl+6 / ^) for headings
            if (e.keyCode === 54 || e.key === '6' || e.key === '^') {
                return;
            }

            // Google Docs style Strikethrough: Alt+Shift+5
            if (e.altKey && e.shiftKey && (e.key === '5' || e.keyCode === 53 || e.code === 'Digit5')) {
                e.preventDefault();
                e.stopPropagation();
                self.executeCommand('strikethrough');
                return false;
            }

            var isCtrlOrCmd = e.ctrlKey || e.metaKey;
            if (!isCtrlOrCmd) return;

            var code = e.code || '';
            var key = (e.key || '').toLowerCase();
            var keyCode = e.keyCode;

            // Telegram: Ctrl+Shift+X -> Strikethrough
            if (e.shiftKey && (code === 'KeyX' || key === 'x' || key === 'ч' || keyCode === 88)) {
                e.preventDefault();
                e.stopPropagation();
                self.executeCommand('strikethrough');
                return false;
            }

            // Telegram: Ctrl+Shift+M -> Code / Monospace
            if (e.shiftKey && (code === 'KeyM' || key === 'm' || key === 'ь' || keyCode === 77)) {
                e.preventDefault();
                e.stopPropagation();
                self.executeCommand('code');
                return false;
            }

            // Telegram: Ctrl+Shift+P -> Spoiler
            if (e.shiftKey && (code === 'KeyP' || key === 'p' || key === 'з' || keyCode === 80)) {
                e.preventDefault();
                e.stopPropagation();
                self.executeCommand('spoiler');
                return false;
            }

            // Telegram: Ctrl+Shift+. (Period) -> Quote
            if (e.shiftKey && (code === 'Period' || key === '.' || key === '>' || key === 'ю' || keyCode === 190)) {
                e.preventDefault();
                e.stopPropagation();
                self.executeCommand('quote');
                return false;
            }

            // Clear formatting: Ctrl+Shift+N or Ctrl+\
            if ((e.shiftKey && (code === 'KeyN' || key === 'n' || key === 'т' || keyCode === 78)) ||
                (!e.shiftKey && (code === 'Backslash' || key === '\\' || keyCode === 220))) {
                e.preventDefault();
                e.stopPropagation();
                self.executeCommand('removeFormat');
                return false;
            }

            // Ctrl+K -> Link
            if (!e.shiftKey && !e.altKey && (code === 'KeyK' || key === 'k' || key === 'л' || keyCode === 75)) {
                e.preventDefault();
                e.stopPropagation();
                self.executeCommand('link');
                return false;
            }

            // Ctrl+B -> Bold
            if (!e.shiftKey && !e.altKey && (code === 'KeyB' || key === 'b' || key === 'и' || keyCode === 66)) {
                e.preventDefault();
                e.stopPropagation();
                self.executeCommand('bold');
                return false;
            }

            // Ctrl+I -> Italic
            if (!e.shiftKey && !e.altKey && (code === 'KeyI' || key === 'i' || key === 'ш' || keyCode === 73)) {
                e.preventDefault();
                e.stopPropagation();
                self.executeCommand('italic');
                return false;
            }

            // Ctrl+U -> Underline
            if (!e.shiftKey && !e.altKey && (code === 'KeyU' || key === 'u' || key === 'г' || keyCode === 85)) {
                e.preventDefault();
                e.stopPropagation();
                self.executeCommand('underline');
                return false;
            }

            // Ctrl+A / Cmd+A in visual editor: select ALL contents of the visual editor
            if (self.currentMode === 'visual' && !e.shiftKey && !e.altKey && (code === 'KeyA' || key === 'a' || key === 'ф' || keyCode === 65)) {
                e.preventDefault();
                e.stopPropagation();
                var r = document.createRange();
                r.selectNodeContents(self.$visualEditor[0]);
                var sel = window.getSelection();
                if (sel) {
                    sel.removeAllRanges();
                    sel.addRange(r);
                }
                self.saveSelection();
                return false;
            }
        };

        this.$visualEditor.on('keydown', handleKeydown);
        this.$textarea.on('keydown', handleKeydown);

        // Visual editor special key handling: inline formatting navigation & spoiler <summary> Enter
        this.$visualEditor.on('keydown', function(e) {
            var sel = window.getSelection();
            if (!sel || !sel.rangeCount) return;
            var range = sel.getRangeAt(0);
            var container = range.startContainer;
            var parentEl = container.nodeType === 1 ? container : container.parentNode;

            // 1. If inside <summary>: pressing Enter jumps to .spoiler-body without closing details
            if (e.key === 'Enter') {
                var summaryNode = parentEl.closest('summary');
                if (summaryNode && self.$visualEditor[0].contains(summaryNode)) {
                    e.preventDefault();
                    var detailsNode = summaryNode.closest('details');
                    if (detailsNode) {
                        var bodyNode = detailsNode.querySelector('.spoiler-body');
                        if (bodyNode) {
                            var targetP = bodyNode.querySelector('p') || bodyNode;
                            var r = document.createRange();
                            r.selectNodeContents(targetP);
                            r.collapse(true);
                            sel.removeAllRanges();
                            sel.addRange(r);
                        }
                    }
                    return;
                }
            }

            // 2. Inline formatting tags (em, strong, u, del, mark, code, kbd, sup, sub)
            var INLINE_SELECTOR = 'em, i, strong, b, u, ins, del, s, strike, mark, code, kbd, sup, sub';

            // ArrowRight: step out cleanly on ONE press (both when text is selected and when cursor is at end)
            if (e.key === 'ArrowRight') {
                if (!range.collapsed) {
                    var endContainer = range.endContainer;
                    var endEl = endContainer.nodeType === 1 ? endContainer : endContainer.parentNode;
                    var endInline = endEl ? endEl.closest(INLINE_SELECTOR) : null;
                    if (endInline && self.$visualEditor[0].contains(endInline)) {
                        e.preventDefault();
                        exitInlineTag(endInline);
                        return;
                    }
                } else {
                    var activeInline = parentEl.closest(INLINE_SELECTOR);
                    if (activeInline && self.$visualEditor[0].contains(activeInline)) {
                        if (isAtEndOfInlineNode(range, activeInline)) {
                            e.preventDefault();
                            exitInlineTag(activeInline);
                            return;
                        }
                    }
                }
            }

            var inlineNode = parentEl.closest(INLINE_SELECTOR);
            if (inlineNode && self.$visualEditor[0].contains(inlineNode)) {
                var isAtEnd = isAtEndOfInlineNode(range, inlineNode);

                // Prevent Enter inside/at end of inline tag from cloning formatting to the new line
                if (e.key === 'Enter' && !e.shiftKey) {
                    if (isAtEnd) {
                        e.preventDefault();
                        var parentBlock = inlineNode.closest('p, div, blockquote, li') || inlineNode.parentNode;
                        var newP = document.createElement('p');
                        newP.innerHTML = '<br>';
                        if (parentBlock && parentBlock.parentNode) {
                            parentBlock.parentNode.insertBefore(newP, parentBlock.nextSibling);
                        } else {
                            inlineNode.parentNode.insertBefore(newP, inlineNode.nextSibling);
                        }
                        var r = document.createRange();
                        r.setStart(newP, 0);
                        r.collapse(true);
                        sel.removeAllRanges();
                        sel.addRange(r);
                        return;
                    }
                }

                // For <kbd> and <code>: Space at end steps out
                var tagUpper = inlineNode.tagName.toUpperCase();
                if ((tagUpper === 'KBD' || tagUpper === 'CODE') && (e.key === ' ' || e.key === 'Spacebar') && range.collapsed && isAtEnd) {
                    e.preventDefault();
                    exitInlineTag(inlineNode);
                    return;
                }
            }

            // 3. Blockquote Enter & ArrowDown handling: breakout on empty line or move below
            var bqNode = parentEl.closest('blockquote');
            if (bqNode && self.$visualEditor[0].contains(bqNode)) {
                // Ensure a trailing paragraph exists after blockquote so user can click or ArrowDown into it
                if (!bqNode.nextSibling) {
                    var trailingPara = document.createElement('p');
                    trailingPara.innerHTML = '<br>';
                    bqNode.parentNode.appendChild(trailingPara);
                }

                if (e.key === 'Enter' && !e.shiftKey) {
                    var currentLine = parentEl.closest('p, div, li') || parentEl;
                    var textContent = $.trim(currentLine.textContent);
                    var hasImg = currentLine.querySelector && currentLine.querySelector('img');
                    // If current line inside blockquote is empty: break out of blockquote!
                    if (!textContent && !hasImg) {
                        e.preventDefault();
                        if (currentLine !== bqNode && currentLine.parentNode === bqNode) {
                            bqNode.removeChild(currentLine);
                        }
                        var newP = document.createElement('p');
                        newP.innerHTML = '<br>';
                        if (bqNode.nextSibling) {
                            bqNode.parentNode.insertBefore(newP, bqNode.nextSibling);
                        } else {
                            bqNode.parentNode.appendChild(newP);
                        }
                        var r = document.createRange();
                        r.setStart(newP, 0);
                        r.collapse(true);
                        sel.removeAllRanges();
                        sel.addRange(r);
                        self.saveSelection();
                        self.syncMarkdownFromVisual();
                        return;
                    }
                }

                if (e.key === 'ArrowDown') {
                    var lastChild = bqNode.lastElementChild || bqNode;
                    var isAtBottom = range.collapsed && (parentEl === lastChild || lastChild.contains(parentEl));
                    if (isAtBottom && bqNode.nextSibling && bqNode.nextSibling.tagName && bqNode.nextSibling.tagName.toLowerCase() === 'p') {
                        var nextP = bqNode.nextSibling;
                        var r = document.createRange();
                        r.setStart(nextP, 0);
                        r.collapse(true);
                        sel.removeAllRanges();
                        sel.addRange(r);
                        e.preventDefault();
                        return;
                    }
                }
            }

            // 4. Pre (code block) ArrowDown handling: move into paragraph below
            var preNode = parentEl.closest('pre');
            if (preNode && self.$visualEditor[0].contains(preNode)) {
                if (!preNode.nextSibling) {
                    var trailingPara = document.createElement('p');
                    trailingPara.innerHTML = '<br>';
                    preNode.parentNode.appendChild(trailingPara);
                }

                if (e.key === 'ArrowDown') {
                    var lastChild = preNode.lastElementChild || preNode;
                    var isAtBottom = range.collapsed && (parentEl === lastChild || lastChild.contains(parentEl));
                    if (isAtBottom && preNode.nextSibling && preNode.nextSibling.tagName && preNode.nextSibling.tagName.toLowerCase() === 'p') {
                        var nextP = preNode.nextSibling;
                        var r = document.createRange();
                        r.setStart(nextP, 0);
                        r.collapse(true);
                        sel.removeAllRanges();
                        sel.addRange(r);
                        e.preventDefault();
                        return;
                    }
                }
            }

            // 5. Backspace / Delete handling: allow clean deletion of entire editor or empty code blocks
            if (e.key === 'Backspace' || e.key === 'Delete' || e.keyCode === 8 || e.keyCode === 46) {
                // If entire editor is selected (e.g. after Ctrl+A): wipe cleanly to <p><br></p>
                if (!range.collapsed) {
                    var isAll = false;
                    if (range.commonAncestorContainer === self.$visualEditor[0]) {
                        if (range.startOffset === 0 && range.endOffset >= self.$visualEditor[0].childNodes.length) {
                            isAll = true;
                        }
                    }
                    if (!isAll) {
                        var selText = sel.toString();
                        var allText = self.$visualEditor.text();
                        if (selText.length > 0 && selText === allText) {
                            isAll = true;
                        }
                    }
                    if (isAll) {
                        e.preventDefault();
                        self.$visualEditor.html('<p><br></p>');
                        var r = document.createRange();
                        r.setStart(self.$visualEditor.find('p')[0], 0);
                        r.collapse(true);
                        sel.removeAllRanges();
                        sel.addRange(r);
                        self.saveSelection();
                        self.syncMarkdownFromVisual();
                        self.updateCharCounter();
                        return;
                    }
                }

                // If inside an empty code block: delete the code block
                var currentPre = parentEl ? parentEl.closest('pre') : null;
                if (currentPre && self.$visualEditor[0].contains(currentPre)) {
                    var preText = $.trim(currentPre.textContent);
                    if (!preText) {
                        e.preventDefault();
                        var nextP = currentPre.nextSibling && currentPre.nextSibling.tagName && currentPre.nextSibling.tagName.toLowerCase() === 'p'
                            ? currentPre.nextSibling
                            : null;
                        if (!nextP) {
                            nextP = document.createElement('p');
                            nextP.innerHTML = '<br>';
                            currentPre.parentNode.insertBefore(nextP, currentPre);
                        }
                        currentPre.parentNode.removeChild(currentPre);
                        var r = document.createRange();
                        r.setStart(nextP, 0);
                        r.collapse(true);
                        sel.removeAllRanges();
                        sel.addRange(r);
                        self.saveSelection();
                        self.syncMarkdownFromVisual();
                        self.updateCharCounter();
                        return;
                    }
                }
            }
        });

        // Live continuous sync on input / changes in visual editor
        this.$visualEditor.on('input keyup paste change', function() {
            // If the editor has only an empty pre left, clean it up to standard paragraph
            if (self.$visualEditor.children().length === 1 && self.$visualEditor.find('pre').length === 1 && !$.trim(self.$visualEditor.text())) {
                self.$visualEditor.html('<p><br></p>');
            }
            var sel = window.getSelection();
            if (sel && sel.rangeCount > 0) {
                var range = sel.getRangeAt(0);
                var container = range.endContainer;
                var el = container.nodeType === 1 ? container : container.parentNode;
                var inlineNode = el ? el.closest('em, i, strong, b, u, ins, del, s, strike, mark, code, kbd, sup, sub') : null;
                if (inlineNode && self.$visualEditor[0].contains(inlineNode)) {
                    ensureTrailingSpacer(inlineNode);
                }
            }
            self.updateSpoilerPlaceholders();
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

    ForumEditor.prototype.showModal = function() {
        this.$modalOverlay.removeClass('d-none');
    };

    ForumEditor.prototype.closeModal = function() {
        this.$modalOverlay.addClass('d-none');
        this.activeModalSubmit = null;
        if (this.currentMode === 'visual') {
            this.$visualEditor.focus();
            this.restoreSelection();
        } else {
            this.$textarea.focus();
        }
    };

    ForumEditor.prototype.openLinkModal = function() {
        var self = this;
        this.saveSelection();

        var currentText = '';
        if (this.currentMode === 'visual') {
            var sel = window.getSelection();
            if (sel && sel.rangeCount > 0) {
                currentText = sel.toString();
            }
        } else {
            var el = this.$textarea[0];
            currentText = el.value.substring(el.selectionStart, el.selectionEnd);
        }

        this.$modalTitle.text('Вставить ссылку');
        this.$modalBody.html([
            '<div class="form-group mb-2">',
                '<label for="forum-modal-link-url">URL ссылки</label>',
                '<input type="text" id="forum-modal-link-url" class="form-control form-control-sm" placeholder="https://" value="https://">',
            '</div>',
            '<div class="form-group mb-0">',
                '<label for="forum-modal-link-text">Текст ссылки</label>',
                '<input type="text" id="forum-modal-link-text" class="form-control form-control-sm" placeholder="Отображаемый текст">',
            '</div>'
        ].join(''));

        var $urlInput = this.$modalBody.find('#forum-modal-link-url');
        var $textInput = this.$modalBody.find('#forum-modal-link-text');

        if (currentText) {
            $textInput.val(currentText);
        }

        this.activeModalSubmit = function() {
            var url = $.trim($urlInput.val());
            var text = $.trim($textInput.val());
            if (!url || url === 'https://' || url === 'http://') {
                $urlInput.focus();
                return;
            }
            self.closeModal();

            if (self.currentMode === 'visual') {
                self.$visualEditor.focus();
                self.restoreSelection();
                var displayText = text || url;
                document.execCommand('insertHTML', false, '<a href="' + sanitizeUrl(url) + '" target="_blank" rel="noopener">' + escapeHtml(displayText) + '</a>');
                self.syncMarkdownFromVisual();
            } else {
                self.$textarea.focus();
                var displayText = text || url;
                wrapTextareaSelection(self.$textarea, '', '[' + displayText + '](' + url + ')', '');
            }
            self.updateCharCounter();
        };

        this.showModal();
        setTimeout(function() {
            $urlInput.focus();
            var len = $urlInput.val().length;
            if ($urlInput[0].setSelectionRange) {
                $urlInput[0].setSelectionRange(len, len);
            }
        }, 50);
    };

    ForumEditor.prototype.openImageModal = function() {
        var self = this;
        this.saveSelection();

        this.$modalTitle.text('Вставить изображение');
        this.$modalBody.html([
            '<div class="form-group mb-2">',
                '<label for="forum-modal-img-url">URL изображения</label>',
                '<input type="text" id="forum-modal-img-url" class="form-control form-control-sm" placeholder="https://example.com/image.jpg">',
            '</div>',
            '<div class="form-group mb-3">',
                '<label for="forum-modal-img-title">Подпись / заголовок (title & alt)</label>',
                '<input type="text" id="forum-modal-img-title" class="form-control form-control-sm" placeholder="Описание изображения (необязательно)">',
            '</div>',
            '<div class="text-center my-2">',
                '<span class="text-muted small">— или —</span>',
            '</div>',
            '<div class="text-center mt-2">',
                '<button type="button" class="btn btn-outline-primary btn-sm forum-modal-choose-file-btn">',
                    '<i class="fa fa-folder-open-o mr-1"></i> Выбрать файл на устройстве',
                '</button>',
            '</div>'
        ].join(''));

        var $urlInput = this.$modalBody.find('#forum-modal-img-url');
        var $titleInput = this.$modalBody.find('#forum-modal-img-title');
        var $chooseBtn = this.$modalBody.find('.forum-modal-choose-file-btn');

        $chooseBtn.on('click', function(e) {
            e.preventDefault();
            self.closeModal();
            self.$fileInput.click();
        });

        this.activeModalSubmit = function() {
            var url = $.trim($urlInput.val());
            var title = $.trim($titleInput.val());
            if (!url) {
                $urlInput.focus();
                return;
            }
            self.closeModal();

            var alt = title || '';
            var titleAttr = alt;

            if (self.currentMode === 'visual') {
                self.$visualEditor.focus();
                self.restoreSelection();
                var imgHtml = '<p><img src="' + sanitizeUrl(url) + '" alt="' + escapeHtml(alt) + '" title="' + escapeHtml(titleAttr) + '" class="forum-embedded-img"></p><p><br></p>';
                document.execCommand('insertHTML', false, imgHtml);
                self.syncMarkdownFromVisual();
            } else {
                self.$textarea.focus();
                var md = '![' + alt + '](' + url + ' "' + titleAttr + '")';
                wrapTextareaSelection(self.$textarea, '', md, '');
            }
            self.updateCharCounter();
        };

        this.showModal();
        setTimeout(function() {
            $urlInput.focus();
        }, 50);
    };

    ForumEditor.prototype.ensureActiveInlineSpacer = function() {
        var sel = window.getSelection();
        if (!sel || !sel.rangeCount) return;
        var range = sel.getRangeAt(0);
        var container = range.endContainer;
        var el = container.nodeType === 1 ? container : container.parentNode;
        var inlineNode = el ? el.closest('em, i, strong, b, u, ins, del, s, strike, mark, code, kbd, sup, sub') : null;
        if (inlineNode && this.$visualEditor[0].contains(inlineNode)) {
            ensureTrailingSpacer(inlineNode);
        }
    };

    ForumEditor.prototype.executeVisualCommand = function(cmd) {
        if (this.savedRange) {
            this.restoreSelection();
        } else {
            this.$visualEditor.focus();
        }
        switch (cmd) {
            case 'bold':
            case 'italic':
            case 'underline':
            case 'strikethrough': {
                var sel = window.getSelection();
                if (sel && sel.rangeCount > 0) {
                    var range = sel.getRangeAt(0);
                    if (range.collapsed) {
                        var container = range.commonAncestorContainer;
                        var parentEl = container.nodeType === 1 ? container : container.parentNode;
                        var tagSelector = {
                            'bold': 'strong, b',
                            'italic': 'em, i',
                            'underline': 'u, ins',
                            'strikethrough': 'del, s, strike'
                        }[cmd];
                        var activeTag = parentEl ? parentEl.closest(tagSelector) : null;
                        if (activeTag && this.$visualEditor[0].contains(activeTag)) {
                            exitInlineTag(activeTag);
                            this.saveSelection();
                            break;
                        }
                    }
                }
                var nativeCmd = {
                    'bold': 'bold',
                    'italic': 'italic',
                    'underline': 'underline',
                    'strikethrough': 'strikeThrough'
                }[cmd];
                document.execCommand(nativeCmd, false, null);
                this.ensureActiveInlineSpacer();
                break;
            }
            case 'mark':
                toggleCustomInlineTag('mark', 'editor-mark', 'текст');
                break;
            case 'code':
                this.toggleVisualCode();
                break;
            case 'kbd':
                toggleCustomInlineTag('kbd', 'editor-key', 'клавиша');
                break;
            case 'superscript':
                toggleCustomInlineTag('sup', '', '2');
                break;
            case 'subscript':
                toggleCustomInlineTag('sub', '', '2');
                break;
            case 'removeFormat':
                clearFormattingVisual(this.$visualEditor[0]);
                break;
            case 'h2':
                document.execCommand('formatBlock', false, '<h2>');
                break;
            case 'h3':
                document.execCommand('formatBlock', false, '<h3>');
                break;
            case 'quote': {
                var sel = window.getSelection();
                if (sel && sel.rangeCount > 0) {
                    var range = sel.getRangeAt(0);
                    var container = range.commonAncestorContainer;
                    var parentEl = container.nodeType === 1 ? container : container.parentNode;
                    var bqNode = parentEl ? parentEl.closest('blockquote') : null;
                    if (bqNode && this.$visualEditor[0].contains(bqNode)) {
                        // Unwrap blockquote
                        var p = bqNode.parentNode;
                        var firstChild = bqNode.firstChild;
                        var lastChild = bqNode.lastChild;
                        while (bqNode.firstChild) {
                            p.insertBefore(bqNode.firstChild, bqNode);
                        }
                        p.removeChild(bqNode);
                        if (firstChild && lastChild) {
                            var newRange = document.createRange();
                            newRange.setStartBefore(firstChild);
                            newRange.setEndAfter(lastChild);
                            sel.removeAllRanges();
                            sel.addRange(newRange);
                        }
                        this.saveSelection();
                        break;
                    }
                }
                document.execCommand('formatBlock', false, '<blockquote>');
                break;
            }
            case 'ul':
                document.execCommand('insertUnorderedList', false, null);
                break;
            case 'ol':
                document.execCommand('insertOrderedList', false, null);
                break;
            case 'spoiler':
                var spoilerHtml = '<details class="forum-spoiler" open>' +
                    '<summary data-placeholder="Введите заголовок спойлера" data-empty="true"><br></summary>' +
                    '<div class="spoiler-body" data-placeholder="Введите текст спойлера — можно также вставлять изображения" data-empty="true"><p><br></p></div>' +
                    '</details><p><br></p>';
                document.execCommand('insertHTML', false, spoilerHtml);
                var sel = window.getSelection();
                if (sel && sel.rangeCount > 0) {
                    var range = sel.getRangeAt(0);
                    var container = range.commonAncestorContainer;
                    var parentNode = container.nodeType === 1 ? container : container.parentNode;
                    var detailsNode = parentNode.closest ? parentNode.closest('details.forum-spoiler') : null;
                    if (!detailsNode) {
                        var spoilers = this.$visualEditor.find('details.forum-spoiler');
                        if (spoilers.length) detailsNode = spoilers.last()[0];
                    }
                    if (detailsNode) {
                        var summary = detailsNode.querySelector('summary');
                        if (summary) {
                            var newRange = document.createRange();
                            newRange.selectNodeContents(summary);
                            newRange.collapse(true);
                            sel.removeAllRanges();
                            sel.addRange(newRange);
                        }
                    }
                }
                this.updateSpoilerPlaceholders();
                break;
            case 'link':
                this.openLinkModal();
                break;
            case 'image':
                this.openImageModal();
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
                wrapTextareaSelection(this.$textarea, '_', '_', 'курсив');
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
            case 'code':
                this.toggleMarkdownCode();
                break;
            case 'kbd':
                wrapTextareaSelection(this.$textarea, '++', '++', 'Ctrl+C');
                break;
            case 'superscript':
                wrapTextareaSelection(this.$textarea, '^', '^', '2');
                break;
            case 'subscript':
                wrapTextareaSelection(this.$textarea, '~', '~', '2');
                break;
            case 'removeFormat':
                var el = this.$textarea[0];
                var start = el.selectionStart;
                var end = el.selectionEnd;
                var val = el.value;
                var selected = val.substring(start, end);
                if (selected) {
                    var cleaned = selected
                        .replace(/```[a-zA-Z0-9_-]*\n([\s\S]*?)\n```/g, '$1')
                        .replace(/\*\*([^*]+)\*\*/g, '$1')
                        .replace(/__([^_]+)__/g, '$1')
                        .replace(/\*([^*]+)\*/g, '$1')
                        .replace(/_([^_]+)_/g, '$1')
                        .replace(/\^\^([^~^]+)\^\^/g, '$1')
                        .replace(/~~([^~]+)~~/g, '$1')
                        .replace(/==([^=]+)==/g, '$1')
                        .replace(/\+\+([^+\n]+)\+\+/g, '$1')
                        .replace(/`([^`\n]+)`/g, '$1')
                        .replace(/\^([^\s^]+)\^/g, '$1')
                        .replace(/~([^\s~]+)~/g, '$1')
                        .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
                    el.value = val.substring(0, start) + cleaned + val.substring(end);
                    el.focus();
                    el.setSelectionRange(start, start + cleaned.length);
                    this.$textarea.trigger('input');
                }
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
                var el = this.$textarea[0];
                var start = el.selectionStart;
                var end = el.selectionEnd;
                var selected = el.value.substring(start, end) || 'Текст спойлера';
                var prefix = '???- "Заголовок спойлера"\n    ';
                var suffix = '\n\n';
                var replacement = prefix + selected + suffix;
                el.value = el.value.substring(0, start) + replacement + el.value.substring(end);
                el.focus();
                var titleStart = start + 6;
                var titleEnd = titleStart + 18;
                el.setSelectionRange(titleStart, titleEnd);
                this.$textarea.trigger('input');
                break;
            case 'link':
                this.openLinkModal();
                break;
            case 'image':
                this.openImageModal();
                break;
        }
    };

    ForumEditor.prototype.unwrapCodeBlock = function(preNode) {
        var codeNode = preNode.querySelector('code') || preNode;
        var text = (codeNode.textContent || '').replace(/\r\n/g, '\n').replace(/\r/g, '\n');
        var lines = text.split('\n');
        var unwrapHtml = lines.map(function(l) {
            return l.length > 0 ? '<p>' + escapeHtml(l) + '</p>' : '<p><br></p>';
        }).join('');
        if (!unwrapHtml) unwrapHtml = '<p><br></p>';

        var sel = window.getSelection();
        if (sel) {
            var r = document.createRange();
            r.selectNode(preNode);
            sel.removeAllRanges();
            sel.addRange(r);
            document.execCommand('insertHTML', false, unwrapHtml);
            this.saveSelection();
            this.syncMarkdownFromVisual();
            this.updateCharCounter();
        }
    };

    ForumEditor.prototype.toggleVisualCode = function() {
        var sel = window.getSelection();
        if (!sel || !sel.rangeCount) return;
        var range = sel.getRangeAt(0);
        var editorEl = this.$visualEditor[0];

        // 1. Inside existing <pre> (code block) -> unwrap to normal paragraphs
        var container = range.commonAncestorContainer;
        var preNode = (container.nodeType === 1 ? container : container.parentNode).closest('pre');
        if (preNode && editorEl.contains(preNode)) {
            this.unwrapCodeBlock(preNode);
            return;
        }

        // 2. Inside existing inline <code> -> unwrap or exit inline code
        var codeNode = (container.nodeType === 1 ? container : container.parentNode).closest('code');
        if (codeNode && editorEl.contains(codeNode) && (!codeNode.parentNode || codeNode.parentNode.tagName.toLowerCase() !== 'pre')) {
            toggleCustomInlineTag('code', '', 'код');
            return;
        }

        // 3. Selection analysis: multiple paragraphs vs single paragraph
        if (!range.collapsed) {
            function getTopBlock(node) {
                var curr = node.nodeType === 1 ? node : node.parentNode;
                while (curr && curr.parentNode && curr.parentNode !== editorEl) {
                    curr = curr.parentNode;
                }
                return (curr && curr.parentNode === editorEl) ? curr : null;
            }

            var startBlock = getTopBlock(range.startContainer);
            var endBlock = getTopBlock(range.endContainer);

            if (range.startContainer === editorEl) {
                startBlock = editorEl.childNodes[range.startOffset] || editorEl.firstChild;
            }
            if (range.endContainer === editorEl) {
                var idx = Math.max(0, range.endOffset - 1);
                endBlock = editorEl.childNodes[idx] || editorEl.lastChild;
            }

            var isMultiBlock = (startBlock && endBlock && startBlock !== endBlock);
            var cloneFrag = range.cloneContents();
            var hasMultipleLines = isMultiBlock || (cloneFrag.querySelectorAll && cloneFrag.querySelectorAll('p, div, br, li, pre, blockquote').length > 0);

            if (hasMultipleLines) {
                // Multi-paragraph or multi-line selection -> Block Code (pre.editor-code-block)
                var blocks = [];
                if (startBlock && endBlock) {
                    var curr = startBlock;
                    while (curr) {
                        blocks.push(curr);
                        if (curr === endBlock) break;
                        curr = curr.nextSibling;
                    }
                    if (blocks.indexOf(endBlock) === -1) {
                        blocks = [startBlock, endBlock];
                    }
                } else if (startBlock) {
                    blocks.push(startBlock);
                }

                // Extract text with preserved newlines
                var codeText = '';
                if (blocks.length > 1) {
                    var lines = [];
                    for (var b = 0; b < blocks.length; b++) {
                        var bClone = blocks[b].cloneNode(true);
                        var bBrs = bClone.querySelectorAll ? bClone.querySelectorAll('br') : [];
                        for (var brI = 0; brI < bBrs.length; brI++) {
                            var brEl = bBrs[brI];
                            if (brEl.parentNode) {
                                brEl.parentNode.replaceChild(document.createTextNode('\n'), brEl);
                            }
                        }
                        lines.push(bClone.textContent);
                    }
                    codeText = lines.join('\n');
                } else {
                    var fClone = cloneFrag.cloneNode(true);
                    var fBrs = fClone.querySelectorAll ? fClone.querySelectorAll('br') : [];
                    for (var fI = 0; fI < fBrs.length; fI++) {
                        var fBrEl = fBrs[fI];
                        if (fBrEl.parentNode) {
                            fBrEl.parentNode.replaceChild(document.createTextNode('\n'), fBrEl);
                        }
                    }
                    var fBlocks = fClone.querySelectorAll ? fClone.querySelectorAll('p, div, li, h1, h2, h3, blockquote, pre') : [];
                    for (var fB = 0; fB < fBlocks.length; fB++) {
                        fBlocks[fB].appendChild(document.createTextNode('\n'));
                    }
                    codeText = (fClone.textContent || '').replace(/\r\n/g, '\n').replace(/\r/g, '\n').replace(/\n+$/, '');
                }

                // Select all affected blocks before replacement so insertHTML replaces all and records in Undo stack
                if (blocks.length > 0 && blocks[0].parentNode === editorEl) {
                    var replaceRange = document.createRange();
                    replaceRange.setStartBefore(blocks[0]);
                    replaceRange.setEndAfter(blocks[blocks.length - 1]);
                    sel.removeAllRanges();
                    sel.addRange(replaceRange);
                }

                var preHtml = '<pre class="editor-code-block"><code>' + escapeHtml(codeText) + '</code></pre><p><br></p>';
                document.execCommand('insertHTML', false, preHtml);

                this.saveSelection();
                return;
            } else {
                // Single-paragraph selection -> Inline code
                toggleCustomInlineTag('code', '', 'код');
                return;
            }
        } else {
            // Collapsed selection
            toggleCustomInlineTag('code', '', 'код');
            return;
        }
    };

    ForumEditor.prototype.toggleMarkdownCode = function() {
        var el = this.$textarea[0];
        var start = el.selectionStart;
        var end = el.selectionEnd;
        var val = el.value;
        var selected = val.substring(start, end);

        // 1. Collapsed selection
        if (start === end) {
            wrapTextareaSelection(this.$textarea, '`', '`', 'код');
            return;
        }

        // 2. Multi-line selection -> Block Code (```...```)
        if (selected.indexOf('\n') !== -1) {
            var trimmed = selected.trim();
            if (/^```[a-zA-Z0-9_-]*\n[\s\S]*```$/.test(trimmed)) {
                // Unwrap code block
                var unwrapped = trimmed.replace(/^```[a-zA-Z0-9_-]*\n?/, '').replace(/\n?```$/, '');
                el.value = val.substring(0, start) + unwrapped + val.substring(end);
                el.focus();
                el.setSelectionRange(start, start + unwrapped.length);
                this.$textarea.trigger('input');
                return;
            }

            // Wrap into code block
            var prefix = (start > 0 && val.charAt(start - 1) !== '\n') ? '\n```\n' : '```\n';
            var suffix = (end < val.length && val.charAt(end) !== '\n') ? '\n```\n' : '\n```';
            var replacement = prefix + selected + suffix;
            el.value = val.substring(0, start) + replacement + val.substring(end);
            el.focus();
            el.setSelectionRange(start, start + replacement.length);
            this.$textarea.trigger('input');
            return;
        }

        // 3. Single-line selection -> Inline Code (`...`)
        if (selected.startsWith('`') && selected.endsWith('`') && selected.length >= 2) {
            var unwrapped = selected.slice(1, -1);
            el.value = val.substring(0, start) + unwrapped + val.substring(end);
            el.focus();
            el.setSelectionRange(start, start + unwrapped.length);
            this.$textarea.trigger('input');
            return;
        } else {
            var replacement = '`' + selected + '`';
            el.value = val.substring(0, start) + replacement + val.substring(end);
            el.focus();
            el.setSelectionRange(start + 1, start + 1 + selected.length);
            this.$textarea.trigger('input');
            return;
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
                        var imgHtml = '<p><img src="' + escapeHtml(imgUrl) + '" alt="' + escapeHtml(altText) + '" title="' + escapeHtml(altText) + '" class="forum-embedded-img"></p><p><br></p>';
                        if ($ph.length) {
                            $ph.replaceWith(imgHtml);
                        } else {
                            document.execCommand('insertHTML', false, imgHtml);
                        }
                        self.syncMarkdownFromVisual();
                    } else {
                        var currentVal = self.$textarea.val();
                        var finalMd = '![' + altText + '](' + imgUrl + ' "' + altText + '")';
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
