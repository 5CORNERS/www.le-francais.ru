(function ($) {
    'use strict';

    $(document).ready(function () {
        var $playerPlusTab = $('#playerPlusTab');
        var $playerPlusPane = $('#playerPlus');

        // Only initialize if Player+ tab exists on this page
        if (!$playerPlusTab.length && !$playerPlusPane.length) {
            return;
        }

        var transcriptMap = window.transcriptMap || [];
        var chapters = [];
        var chaptersById = {};
        var currentDepth = 3;

        // --- Settings & LocalStorage ---
        var isAutoScrollEnabled = localStorage.getItem('playerPlus_autoscroll') !== 'false'; // default true
        var isStickyMaterialsEnabled = localStorage.getItem('playerPlus_stickyMaterials') !== 'false'; // default true
        var isUserInteracting = false;
        var userInteractTimer = null;
        var isAutoscrollPausedByManualScroll = false;
        var isScrubbing = false;
        var activeLineId = null;
        var pausedLineId = null;

        var activeScrollAnim = null;
        var stickyMaterials = [];
        var stickyMaterialsInitialized = false;
        var currentPinnedItem = null;
        var $stickyControls = null;
        var stickyRafPending = false;
        var requestAnimFrame = window.requestAnimationFrame || function (cb) { return setTimeout(cb, 16); };
        var cancelAnimFrame = window.cancelAnimationFrame || function (id) { clearTimeout(id); };

        // S-curve smooth scroll with gentle acceleration and deceleration (cosine S-curve)
        function smoothScrollTo(targetY, customDuration) {
            if (activeScrollAnim) {
                cancelAnimFrame(activeScrollAnim);
                activeScrollAnim = null;
            }

            var startY = window.scrollY || window.pageYOffset || document.documentElement.scrollTop || 0;
            var distance = targetY - startY;
            if (Math.abs(distance) < 2) return;

            // Slower, comfortable reading speed: 850ms to 1250ms depending on distance
            var duration = customDuration || Math.max(850, Math.min(1250, Math.round(700 + Math.abs(distance) * 0.9)));
            var startTime = null;

            function sCurveEase(t) {
                // Cosine S-curve: f(0)=0 (zero slope), f(0.5)=0.5, f(1)=1 (zero slope)
                return (1 - Math.cos(t * Math.PI)) / 2;
            }

            function step(timestamp) {
                if (!startTime) startTime = timestamp;
                var elapsed = timestamp - startTime;
                var progress = Math.min(elapsed / duration, 1);
                var ease = sCurveEase(progress);

                window.scrollTo(0, Math.round(startY + distance * ease));

                if (progress < 1) {
                    activeScrollAnim = requestAnimFrame(step);
                } else {
                    activeScrollAnim = null;
                }
            }

            activeScrollAnim = requestAnimFrame(step);
        }

        // Detect manual scrolling: pause autoscroll only if active replica exits reading zone
        function onUserScrollEvent() {
            if (activeScrollAnim) {
                cancelAnimFrame(activeScrollAnim);
                activeScrollAnim = null;
            }
            isUserInteracting = true;
            clearTimeout(userInteractTimer);
            userInteractTimer = setTimeout(function () {
                isUserInteracting = false;
                var $active = activeLineId ? $('#' + activeLineId) : null;
                if ($active && $active.length) {
                    var zone = getViewingZone();
                    var lineTopInView = $active.offset().top - (window.scrollY || window.pageYOffset || 0);
                    var lineBottomInView = lineTopInView + ($active.outerHeight() || 24);
                    // If active line moved outside viewing zone, pause autoscroll gently
                    if (lineBottomInView < zone.zoneTop || lineTopInView > zone.zoneBottom) {
                        isAutoscrollPausedByManualScroll = true;
                    } else {
                        isAutoscrollPausedByManualScroll = false;
                    }
                }
            }, 1500);
        }

        if (window.addEventListener) {
            window.addEventListener('wheel', onUserScrollEvent, { passive: true });
            window.addEventListener('touchmove', onUserScrollEvent, { passive: true });
        }

        function getNavbarHeight() {
            var $topMenu = $('#topMenu');
            return ($topMenu.length && $topMenu.is(':visible')) ? $topMenu.outerHeight() : 48;
        }

        function getAudio() {
            return $('#newAudioTranscript')[0];
        }

        function isPlayerPlusActive() {
            var $p = $('#playerPlus');
            var $t = $('#playerPlusTab');
            return $p.hasClass('active') || $t.hasClass('active') || $p.is(':visible');
        }

        // --- Helper: HTML Template for Player+ Toolbar & Curtain ---
        function getPlayerPlusBarHtml(idPrefix, extraClass) {
            return [
                '<div class="player-plus-bar ' + (extraClass || '') + '" id="' + idPrefix + 'PlayerPlusBar">',
                '    <button type="button" class="player-plus-btn-playpause" title="Воспроизвести / Пауза (Пробел)" aria-label="Воспроизвести">',
                '        <svg class="player-plus-icon-play" viewBox="0 0 24 24" width="16" height="16" fill="currentColor">',
                '            <polygon points="6,4 20,12 6,20"></polygon>',
                '        </svg>',
                '        <svg class="player-plus-icon-pause" viewBox="0 0 24 24" width="16" height="16" fill="currentColor" style="display:none;">',
                '            <rect x="5" y="4" width="4" height="16"></rect>',
                '            <rect x="15" y="4" width="4" height="16"></rect>',
                '        </svg>',
                '    </button>',
                '    <div class="player-plus-time">',
                '        <span class="player-plus-current-time">00:00</span>',
                '        <span class="player-plus-time-separator">/</span>',
                '        <span class="player-plus-total-time">00:00</span>',
                '    </div>',
                '    <div class="player-plus-progress-container" title="Перемотка">',
                '        <div class="player-plus-progress-track">',
                '            <div class="player-plus-progress-buffered"></div>',
                '            <div class="player-plus-progress-bar-fill"></div>',
                '        </div>',
                '    </div>',
                '    <button type="button" class="player-plus-btn-locate" title="К текущей фразе" aria-label="К текущей фразе">',
                '        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">',
                '            <path d="M12 21.5 C 7.5 16.5 4.5 12.8 4.5 9.5 A 7.5 7.5 0 1 1 19.5 9.5 C 19.5 12.8 16.5 16.5 12 21.5 Z"></path>',
                '            <circle cx="12" cy="9.5" r="3.2"></circle>',
                '        </svg>',
                '    </button>',
                '    <button type="button" class="player-plus-btn-settings" title="Настройки плеера" aria-label="Настройки плеера">',
                '        <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">',
                '            <line x1="4" y1="21" x2="4" y2="14"></line>',
                '            <line x1="4" y1="10" x2="4" y2="3"></line>',
                '            <line x1="12" y1="21" x2="12" y2="12"></line>',
                '            <line x1="12" y1="8" x2="12" y2="3"></line>',
                '            <line x1="20" y1="21" x2="20" y2="16"></line>',
                '            <line x1="20" y1="12" x2="20" y2="3"></line>',
                '            <line x1="1" y1="14" x2="7" y2="14"></line>',
                '            <line x1="9" y1="8" x2="15" y2="8"></line>',
                '            <line x1="17" y1="16" x2="23" y2="16"></line>',
                '        </svg>',
                '    </button>',
                '    <div class="player-plus-drawer">',
                '        <div class="player-plus-drawer-content">',
                '            <label class="player-plus-switch-item" title="Автоматически подматывать текст к текущей реплике">',
                '                <span class="player-plus-switch-label">Автоподмотка</span>',
                '                <span class="player-plus-switch">',
                '                    <input type="checkbox" class="player-plus-toggle-autoscroll"' + (isAutoScrollEnabled ? ' checked' : '') + '>',
                '                    <span class="player-plus-slider"></span>',
                '                </span>',
                '            </label>',
                '            <label class="player-plus-switch-item" title="Фиксировать сопутствующие материалы">',
                '                <span class="player-plus-switch-label">Материалы</span>',
                '                <span class="player-plus-switch">',
                '                    <input type="checkbox" class="player-plus-toggle-stickymaterials"' + (isStickyMaterialsEnabled ? ' checked' : '') + '>',
                '                    <span class="player-plus-slider"></span>',
                '                </span>',
                '            </label>',
                '            <button type="button" class="player-plus-drawer-close" title="Закрыть настройки" aria-label="Закрыть">',
                '                <svg viewBox="0 0 24 24" width="13" height="13" stroke="currentColor" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round">',
                '                    <line x1="18" y1="6" x2="6" y2="18"></line>',
                '                    <line x1="6" y1="6" x2="18" y2="18"></line>',
                '                </svg>',
                '            </button>',
                '        </div>',
                '    </div>',
                '</div>',
                '<div class="player-plus-toc-wrapper" id="' + idPrefix + 'PlayerPlusTocWrapper">',
                '    <div class="player-plus-toc-curtain is-closed">',
                '        <div class="player-plus-toc-header">',
                '            <div class="player-plus-toc-header-left">',
                '                <span class="player-plus-toc-title">Оглавление</span>',
                '                <div class="player-plus-toc-level-switcher" role="group" aria-label="Уровень вложенности оглавления">',
                '                    <button type="button" class="player-plus-toc-level-btn" data-depth="1" title="Только основные разделы (I)">I</button>',
                '                    <button type="button" class="player-plus-toc-level-btn" data-depth="2" title="Разделы и подразделы (I.1)">I.1</button>',
                '                    <button type="button" class="player-plus-toc-level-btn is-active" data-depth="3" title="Все уровни (I.1.a)">I.1.a</button>',
                '                </div>',
                '            </div>',
                '            <button type="button" class="player-plus-toc-close" title="Закрыть оглавление">',
                '                <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2.5" fill="none"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>',
                '            </button>',
                '        </div>',
                '        <div class="player-plus-toc-list"></div>',
                '    </div>',
                '    <button type="button" class="player-plus-toc-tab" title="Оглавление и таймкоды" aria-label="Оглавление и таймкоды">',
                '        <span class="player-plus-toc-pill">',
                '            <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">',
                '                <path d="M4 6h16M4 12h16M4 18h10"></path>',
                '            </svg>',
                '            <span class="player-plus-toc-pill-text">Оглавление</span>',
                '            <span class="player-plus-toc-arrow">▾</span>',
                '        </span>',
                '    </button>',
                '</div>'
            ].join('\n');
        }

        // --- Extract Chapters from Headings in HTML (Hierarchical Tree) ---
        function extractChapters() {
            var rawItems = [];
            var rawLevelsSet = {};

            $('#playerPlus').find('h1, h2, h3, h4, h5, h6').each(function (idx) {
                var $h = $(this);
                var title = $h.text().replace(/\s+/g, ' ').trim();
                if (!title || title.indexOf('Этот транскрипт') !== -1) return;

                var hId = $h.attr('id');
                if (!hId) {
                    hId = 'pp_heading_' + idx;
                    $h.attr('id', hId);
                }

                var rawLevel = parseInt(this.tagName.substring(1), 10) || 2;

                // Traverse DOM to find the first .transcript-line following this heading
                var $nextLine = $h.nextAll().find('.transcript-line').add($h.nextAll('.transcript-line')).first();
                if (!$nextLine.length) {
                    var $parent = $h.parent();
                    while ($parent.length && !$parent.is('#playerPlus') && !$nextLine.length) {
                        $nextLine = $parent.nextAll().find('.transcript-line').add($parent.nextAll('.transcript-line')).first();
                        $parent = $parent.parent();
                    }
                }

                if ($nextLine.length) {
                    var startMs = parseFloat($nextLine.data('start')) || 0;
                    var startSec = startMs / 1000;
                    rawLevelsSet[rawLevel] = true;
                    rawItems.push({
                        idx: rawItems.length,
                        id: 'pp_ch_' + rawItems.length,
                        title: title,
                        startSec: startSec,
                        lineId: $nextLine.attr('id'),
                        headingId: hId,
                        rawLevel: rawLevel,
                        timeFormatted: formatTime(startSec)
                    });
                }
            });

            if (!rawItems.length) return [];

            // Map sorted unique raw levels to normalized levels 1, 2, 3
            var sortedRawLevels = Object.keys(rawLevelsSet).map(function (k) {
                return parseInt(k, 10);
            }).sort(function (a, b) {
                return a - b;
            });

            rawItems.forEach(function (item) {
                var normLevel = sortedRawLevels.indexOf(item.rawLevel) + 1;
                item.level = Math.min(normLevel, 3);
                item.hasChildren = false;
                item.parentId = null;
                item.childIds = [];
                item.isExpanded = true;
            });

            // Build hierarchy links
            var lastAtLevel = {};
            rawItems.forEach(function (item) {
                var parent = null;
                for (var lvl = item.level - 1; lvl >= 1; lvl--) {
                    if (lastAtLevel[lvl]) {
                        parent = lastAtLevel[lvl];
                        break;
                    }
                }
                if (parent) {
                    item.parentId = parent.id;
                    parent.hasChildren = true;
                    parent.childIds.push(item.id);
                }
                lastAtLevel[item.level] = item;
                for (var d = item.level + 1; d <= 3; d++) {
                    delete lastAtLevel[d];
                }
            });

            return rawItems;
        }

        // --- TOC Visibility & Accordion Helpers ---
        function isChapterVisible(ch) {
            var cur = ch;
            while (cur && cur.parentId) {
                var parent = chaptersById[cur.parentId];
                if (!parent || !parent.isExpanded) {
                    return false;
                }
                cur = parent;
            }
            return true;
        }

        function updateTOCVisibilityDOM() {
            chapters.forEach(function (ch) {
                var isVis = isChapterVisible(ch);
                var $items = $('.player-plus-toc-item[data-ch-id="' + ch.id + '"]');
                if (isVis) {
                    $items.removeClass('is-hidden').show();
                } else {
                    $items.addClass('is-hidden').hide();
                }

                if (ch.hasChildren) {
                    var $chevrons = $items.find('.player-plus-toc-chevron');
                    if (ch.isExpanded) {
                        $chevrons.removeClass('is-collapsed').addClass('is-expanded');
                    } else {
                        $chevrons.removeClass('is-expanded').addClass('is-collapsed');
                    }
                }
            });
        }

        function updateSegmentedSwitcherState() {
            var l1WithChildren = chapters.filter(function (c) { return c.level === 1 && c.hasChildren; });
            var l2WithChildren = chapters.filter(function (c) { return c.level === 2 && c.hasChildren; });

            var allL1Expanded = l1WithChildren.length > 0 && l1WithChildren.every(function (c) { return c.isExpanded; });
            var allL1Collapsed = l1WithChildren.length > 0 && l1WithChildren.every(function (c) { return !c.isExpanded; });

            var allL2Expanded = l2WithChildren.length > 0 && l2WithChildren.every(function (c) { return c.isExpanded; });
            var allL2Collapsed = l2WithChildren.length > 0 && l2WithChildren.every(function (c) { return !c.isExpanded; });

            $('.player-plus-toc-level-btn').removeClass('is-active');

            if (allL1Collapsed) {
                $('.player-plus-toc-level-btn[data-depth="1"]').addClass('is-active');
            } else if (allL1Expanded && (l2WithChildren.length === 0 || allL2Collapsed)) {
                $('.player-plus-toc-level-btn[data-depth="2"]').addClass('is-active');
            } else if (allL1Expanded && allL2Expanded) {
                $('.player-plus-toc-level-btn[data-depth="3"]').addClass('is-active');
            }
        }

        function applyTOCDepth(depth) {
            depth = parseInt(depth, 10) || 1;
            currentDepth = depth;

            chapters.forEach(function (ch) {
                if (ch.hasChildren) {
                    ch.isExpanded = (ch.level < depth);
                }
            });

            updateTOCVisibilityDOM();
            updateSegmentedSwitcherState();
        }

        function populateAllCurtains() {
            chapters = extractChapters();
            chaptersById = {};
            chapters.forEach(function (ch) {
                chaptersById[ch.id] = ch;
            });

            var maxDepth = 1;
            chapters.forEach(function (ch) {
                if (ch.level > maxDepth) maxDepth = ch.level;
            });

            $('.player-plus-toc-list').each(function () {
                var $list = $(this);
                $list.empty();
                if (!chapters.length) {
                    $list.append('<div style="padding: 12px 16px; color: #adb5bd; font-size: 0.8rem; text-align: center;">Оглавление не найдено</div>');
                    return;
                }
                chapters.forEach(function (ch) {
                    var chevronOrSpacerHtml = '';
                    if (ch.hasChildren) {
                        chevronOrSpacerHtml = [
                            '<button type="button" class="player-plus-toc-chevron ' + (ch.isExpanded ? 'is-expanded' : 'is-collapsed') + '" title="Свернуть / развернуть подраздел" aria-label="Свернуть / развернуть подраздел">',
                            '    <svg class="player-plus-toc-chevron-svg" viewBox="0 0 24 24" width="12" height="12" stroke="currentColor" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round">',
                            '        <polyline points="9 18 15 12 9 6"></polyline>',
                            '    </svg>',
                            '</button>'
                        ].join('');
                    } else {
                        chevronOrSpacerHtml = '<span class="player-plus-toc-spacer"><span class="player-plus-toc-bullet"></span></span>';
                    }

                    var $item = $(
                        '<div class="player-plus-toc-item level-' + ch.level + '" data-ch-id="' + ch.id + '" data-start-sec="' + ch.startSec + '" data-heading-id="' + ch.headingId + '" data-line-id="' + (ch.lineId || '') + '">' +
                        chevronOrSpacerHtml +
                        '    <div class="player-plus-toc-item-content">' +
                        '        <span class="player-plus-toc-item-title" title="' + ch.title + '">' + ch.title + '</span>' +
                        '        <span class="player-plus-toc-item-time">' + ch.timeFormatted + '</span>' +
                        '    </div>' +
                        '</div>'
                    );
                    $list.append($item);
                });
            });

            var $switchers = $('.player-plus-toc-level-switcher');
            if (maxDepth <= 1) {
                $switchers.hide();
            } else {
                $switchers.show();
                if (maxDepth === 2) {
                    $switchers.find('[data-depth="3"]').hide();
                    $switchers.find('[data-depth="2"]').show();
                    $switchers.find('[data-depth="1"]').show();
                } else {
                    $switchers.find('[data-depth="3"]').show();
                    $switchers.find('[data-depth="2"]').show();
                    $switchers.find('[data-depth="1"]').show();
                }
            }

            applyTOCDepth(maxDepth);
        }

        // --- Mount Player+ Bars ---
        // 1. Natural bar: place at top of #playerPlus
        var $naturalContainer = $('#playerPlusNaturalContainer');
        if ($naturalContainer.length && !$('#naturalPlayerPlusBar').length) {
            $naturalContainer.append(getPlayerPlusBarHtml('natural', 'player-plus-bar-natural'));
        }

        // 2. Floating bar: attach inside floating tabs dock
        function attachFloatingBar() {
            var $floatingWrapper = $('#lessonTabsFloatingWrapper');
            if ($floatingWrapper.length && !$('#floatingPlayerPlusBar').length) {
                var $inner = $floatingWrapper.find('.lesson-tabs-floating-inner');
                if ($inner.length) {
                    var $floatingBar = $(getPlayerPlusBarHtml('floating', 'player-plus-bar-floating'));
                    $floatingBar.css('display', 'none');
                    $inner.after($floatingBar);
                    updateFloatingBarVisibility();
                    populateAllCurtains();
                }
            }
        }
        attachFloatingBar();
        setTimeout(attachFloatingBar, 200);

        // --- Visibility Management ---
        function updateFloatingBarVisibility() {
            var isPlayerPlus = isPlayerPlusActive();
            var $floatingWrapper = $('#lessonTabsFloatingWrapper');
            var isDockHidden = $floatingWrapper.length ? $floatingWrapper.hasClass('is-hidden') : true;
            var $floatingBar = $('#floatingPlayerPlusBar');
            var $floatingToc = $('#floatingPlayerPlusTocWrapper');

            if ($floatingBar.length) {
                if (isPlayerPlus) {
                    $floatingBar.css('display', 'flex');
                    if ($floatingToc.length) {
                        if (isDockHidden) {
                            $floatingToc.hide();
                        } else {
                            $floatingToc.show();
                        }
                    }
                } else {
                    $floatingBar.css('display', 'none');
                    $floatingBar.find('.player-plus-drawer').removeClass('is-open');
                    $floatingBar.find('.player-plus-btn-settings').removeClass('is-active');
                    if ($floatingToc.length) {
                        $floatingToc.hide();
                        $floatingToc.removeClass('is-open');
                    }
                }
            }
        }

        $(document).on('shown.bs.tab', function () {
            updateFloatingBarVisibility();
            if (isPlayerPlusActive()) {
                initInitialHighlight();
            }
        });
        updateFloatingBarVisibility();
        if (isPlayerPlusActive()) {
            initInitialHighlight();
        }

        // --- Time Formatting Helper ---
        function formatTime(seconds) {
            if (isNaN(seconds) || seconds < 0) return '00:00';
            var s = Math.floor(seconds);
            var m = Math.floor(s / 60);
            var ss = s % 60;
            var h = Math.floor(m / 60);
            var mm = m % 60;
            if (h > 0) {
                return h + ':' + (mm < 10 ? '0' : '') + mm + ':' + (ss < 10 ? '0' : '') + ss;
            }
            return (mm < 10 ? '0' : '') + mm + ':' + (ss < 10 ? '0' : '') + ss;
        }

        // --- Sync Play/Pause State ---
        function syncPlayPauseUI(isPlaying) {
            var $bars = $('.player-plus-bar');
            if (isPlaying) {
                $bars.find('.player-plus-icon-play').hide();
                $bars.find('.player-plus-icon-pause').show();
                $bars.find('.player-plus-btn-playpause').attr('aria-label', 'Пауза');
            } else {
                $bars.find('.player-plus-icon-play').show();
                $bars.find('.player-plus-icon-pause').hide();
                $bars.find('.player-plus-btn-playpause').attr('aria-label', 'Воспроизвести');
            }
        }

        function togglePlayPause() {
            var a = getAudio();
            if (!a) return;
            if (a.paused) {
                if (pausedLineId) {
                    setPlayingHighlight(pausedLineId);
                    if (isAutoScrollEnabled) {
                        scrollToLine($('#' + pausedLineId));
                    }
                }
                var p = a.play();
                if (p && p.catch) {
                    p.catch(function (err) {
                        console.warn('Playback error / gesture needed:', err);
                    });
                }
            } else {
                a.pause();
            }
        }

        // --- Spacebar Handler ---
        $(window).on('keydown.playerPlus', function (event) {
            if (event.keyCode === 32 || event.key === ' ' || event.code === 'Space') {
                if (!isPlayerPlusActive()) return;

                var tag = (document.activeElement && document.activeElement.tagName)
                    ? document.activeElement.tagName.toLowerCase()
                    : '';
                if (tag === 'input' || tag === 'textarea' || tag === 'select' || (document.activeElement && document.activeElement.isContentEditable)) {
                    return;
                }

                event.preventDefault();
                togglePlayPause();
            }
        });

        // Click on play/pause button
        $(document).on('click', '.player-plus-btn-playpause', function (e) {
            e.preventDefault();
            togglePlayPause();
        });

        // --- Progress & Time Updates ---
        function updateProgressAndTimes() {
            var a = getAudio();
            if (!a) return;
            var cur = a.currentTime || 0;
            var dur = a.duration || 0;

            $('.player-plus-current-time').text(formatTime(cur));
            if (dur > 0) {
                $('.player-plus-total-time').text(formatTime(dur));
                var percent = Math.min(100, Math.max(0, (cur / dur) * 100));
                $('.player-plus-progress-bar-fill').css('width', percent + '%');
            }

            // Update buffered
            if (a.buffered && a.buffered.length > 0 && dur > 0) {
                try {
                    var bufferedEnd = a.buffered.end(a.buffered.length - 1);
                    var bufPercent = Math.min(100, Math.max(0, (bufferedEnd / dur) * 100));
                    $('.player-plus-progress-buffered').css('width', bufPercent + '%');
                } catch (err) {}
            }

            // Update active chapter in curtain
            if (chapters && chapters.length) {
                var activeChapIdx = -1;
                for (var i = 0; i < chapters.length; i++) {
                    if (chapters[i].startSec <= cur) {
                        activeChapIdx = i;
                    } else {
                        break;
                    }
                }
                $('.player-plus-toc-item').removeClass('is-current');
                if (activeChapIdx >= 0) {
                    $('.player-plus-toc-item[data-ch-id="' + chapters[activeChapIdx].id + '"]').addClass('is-current');
                }
            }
        }

        // --- Audio Events Registration ---
        function bindAudioEvents() {
            var a = getAudio();
            if (!a) return;

            // Remove prior listeners to avoid duplicate firing
            $(a).off('.playerPlus');

            $(a).on('timeupdate.playerPlus', function () {
                updateProgressAndTimes();

                // On pause, do not update playback highlighting
                if (a.paused) return;

                var currentMs = a.currentTime * 1000;
                var item = findItemAtTime(currentMs);
                var newId = item ? item.id : null;

                if (newId && newId !== activeLineId) {
                    setPlayingHighlight(newId);
                    if (isAutoScrollEnabled) {
                        scrollToLine($('#' + newId));
                    }
                    requestUpdateStickyMaterials();
                } else if (activeLineId && isAutoScrollEnabled && !isAutoscrollPausedByManualScroll && !isUserInteracting) {
                    var $active = $('#' + activeLineId);
                    if ($active.length) {
                        var z = getViewingZone($active);
                        var topInView = $active.offset().top - (window.scrollY || window.pageYOffset || 0);
                        if (topInView < z.topObstruction) {
                            scrollToLine($active);
                        }
                    }
                }
            });

            $(a).on('progress.playerPlus loadedmetadata.playerPlus durationchange.playerPlus canplay.playerPlus', function () {
                updateProgressAndTimes();
            });

            $(a).on('play.playerPlus', function () {
                syncPlayPauseUI(true);
                if (!activeLineId) {
                    var currentMs = a.currentTime * 1000;
                    var item = findItemAtTime(currentMs);
                    setPlayingHighlight(item ? item.id : null);
                }
            });

            $(a).on('pause.playerPlus', function () {
                syncPlayPauseUI(false);
                var lineToPause = activeLineId;
                if (!lineToPause) {
                    var currentMs = a.currentTime * 1000;
                    var item = findItemAtTime(currentMs);
                    lineToPause = item ? item.id : null;
                }
                setPausedHighlight(lineToPause);
            });

            $(a).on('ended.playerPlus', function () {
                syncPlayPauseUI(false);
                clearAllHighlights();
            });

            syncPlayPauseUI(!a.paused);
            updateProgressAndTimes();
        }

        // Bind when audioplayer.js finishes cloning, or immediately
        window.addEventListener('audioplayerReady', function () {
            bindAudioEvents();
            populateAllCurtains();
            initInitialHighlight();
            initStickyMaterials();
            updateStickyMaterials();
        });
        bindAudioEvents();
        populateAllCurtains();
        initInitialHighlight();
        initStickyMaterials();
        updateStickyMaterials();

        // --- Progress Bar Seeking & Scrubbing ---
        function seekFromEvent(e, $container) {
            var a = getAudio();
            if (!a || !a.duration) return;

            var $track = $container.first().find('.player-plus-progress-track');
            var offset = $track.offset();
            var width = $track.width();
            if (width <= 0) return;

            var clientX = (e.originalEvent && e.originalEvent.touches)
                ? e.originalEvent.touches[0].clientX
                : e.clientX;

            var percent = Math.max(0, Math.min(1, (clientX - offset.left) / width));
            a.currentTime = percent * a.duration;

            if (a.paused) {
                var currentMs = a.currentTime * 1000;
                var item = findItemAtTime(currentMs);
                setPausedHighlight(item ? item.id : null);
            }
        }

        function onScrubMove(e) {
            if (isScrubbing) {
                seekFromEvent(e, $('.player-plus-progress-container'));
            }
        }

        function onScrubEnd() {
            if (isScrubbing) {
                isScrubbing = false;
                $(document).off('mousemove.playerPlusScrub touchmove.playerPlusScrub', onScrubMove);
                $(document).off('mouseup.playerPlusScrub touchend.playerPlusScrub', onScrubEnd);
            }
        }

        $(document).on('mousedown touchstart', '.player-plus-progress-container', function (e) {
            isScrubbing = true;
            seekFromEvent(e, $(this));
            $(document).on('mousemove.playerPlusScrub touchmove.playerPlusScrub', onScrubMove);
            $(document).on('mouseup.playerPlusScrub touchend.playerPlusScrub', onScrubEnd);
        });

        // --- Highlighting Logic ---
        function findItemAtTime(timeMs) {
            if (!transcriptMap || !transcriptMap.length) return null;

            // If playback position is before the first phrase, attribute it to the first phrase
            var firstStart = parseFloat(transcriptMap[0].start);
            if (!isNaN(firstStart) && timeMs < firstStart) {
                return transcriptMap[0];
            }

            var epsilon = 60; // 60ms tolerance for audio keyframe seeking & float precision

            // 1. Primary check: search backwards so the newest started phrase takes precedence in overlaps
            for (var i = transcriptMap.length - 1; i >= 0; i--) {
                var it = transcriptMap[i];
                var s = parseFloat(it.start);
                var e = parseFloat(it.end);
                if (timeMs >= (s - epsilon) && timeMs <= e) {
                    return it;
                }
            }

            // 2. Secondary fallback for gaps between phrases
            for (var j = transcriptMap.length - 1; j >= 0; j--) {
                var item = transcriptMap[j];
                var start = parseFloat(item.start);
                var end = parseFloat(item.end);
                if (timeMs >= (start - epsilon) && timeMs <= (end + 150)) {
                    return item;
                }
            }

            return null;
        }

        function getFirstLineId() {
            if (transcriptMap && transcriptMap.length && transcriptMap[0].id) {
                return transcriptMap[0].id;
            }
            var $first = $('#playerPlus .transcript-line').first();
            return $first.length ? $first.attr('id') : null;
        }

        function initInitialHighlight() {
            var a = getAudio();
            if (a && !a.paused) return;
            if (activeLineId || pausedLineId) return;
            var firstId = getFirstLineId();
            if (firstId) {
                setPausedHighlight(firstId);
            }
        }

        function clearAllHighlights() {
            $('.transcript-line-play-btn').remove();
            $('.transcript-line').removeClass('transcript-line-playing bg-primary text-white transcript-line-selected');
            activeLineId = null;
            pausedLineId = null;
            updateLocateButtonVisibility();
        }

        function setPausedHighlight(lineId) {
            clearAllHighlights();
            pausedLineId = lineId;
            if (lineId) {
                var $el = $('#' + lineId);
                $el.addClass('transcript-line-selected');

                // Prepend the small inline play button at the beginning of the replica
                if (!$el.find('.transcript-line-play-btn').length) {
                    var $playBtn = $(
                        '<button type="button" class="transcript-line-play-btn" title="Воспроизвести с этого места" aria-label="Воспроизвести">' +
                        '    <svg viewBox="0 0 16 16" width="10" height="10" fill="currentColor" style="margin-left: 1px;">' +
                        '        <path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"/>' +
                        '    </svg>' +
                        '</button>'
                    );
                    $el.prepend($playBtn);
                }
            }
            updateLocateButtonVisibility();
        }

        function setPlayingHighlight(lineId) {
            $('.transcript-line-play-btn').remove();
            $('.transcript-line').removeClass('transcript-line-selected');
            if (activeLineId === lineId) return;

            if (activeLineId) {
                $('#' + activeLineId).removeClass('transcript-line-playing bg-primary text-white');
            }
            activeLineId = lineId;
            if (lineId) {
                $('#' + lineId).addClass('transcript-line-playing');
            }
            updateLocateButtonVisibility();
        }

        // Clicking a transcript line: seek and highlight on pause, or update highlight immediately if playing
        $(document).on('click', '.transcript-line', function (e) {
            if ($(e.target).closest('.transcript-line-play-btn').length) {
                return; // handled by play button handler below
            }
            isAutoscrollPausedByManualScroll = false;
            var startSec = parseFloat($(this).data('start')) / 1000;
            var lineId = $(this).attr('id');
            var a = getAudio();
            if (a) {
                a.currentTime = startSec;
                if (a.paused) {
                    setPausedHighlight(lineId);
                } else {
                    setPlayingHighlight(lineId);
                    if (isAutoScrollEnabled) {
                        scrollToLine($(this));
                    }
                }
            }
        });

        // Clicking the inline mini Play button on selected replica
        $(document).on('click', '.transcript-line-play-btn', function (e) {
            e.stopPropagation();
            e.preventDefault();
            isAutoscrollPausedByManualScroll = false;
            var a = getAudio();
            if (!a) return;
            var $line = $(this).closest('.transcript-line');
            var lineId = $line.attr('id');
            var startSec = parseFloat($line.data('start')) / 1000;
            if (lineId) {
                setPlayingHighlight(lineId);
                if (isAutoScrollEnabled) {
                    scrollToLine($line);
                }
            }
            a.currentTime = startSec;
            var p = a.play();
            if (p && p.catch) p.catch(function () {});
        });

        // --- Viewing Zone & Autoscroll Implementation ---
        function getViewingZone($line) {
            var navH = getNavbarHeight();
            var $floatingWrapper = $('#lessonTabsFloatingWrapper');
            var isDockVisible = ($floatingWrapper.length && $floatingWrapper.is(':visible') && !$floatingWrapper.hasClass('is-hidden'));
            var dockH = isDockVisible ? $floatingWrapper.outerHeight() : 0;
            var topObstruction = navH + dockH;

            // 1. Check if any sticky material is currently pinned
            if (isStickyMaterialsEnabled && currentPinnedItem) {
                var pinnedActualH = currentPinnedItem.$el.outerHeight() || currentPinnedItem.pinnedHeight || 0;
                var pinnedBottom = currentPinnedItem.currentTop + pinnedActualH + 20;
                if (pinnedBottom > topObstruction) {
                    topObstruction = pinnedBottom;
                }
            }

            // 2. Predictive check: will any sticky material be pinned when viewing $line?
            if (isStickyMaterialsEnabled && $line && $line.length) {
                var lineDocTop = $line.offset().top;
                for (var i = 0; i < stickyMaterials.length; i++) {
                    var item = stickyMaterials[i];
                    if (item.isDismissed || !item.$anchor || !item.$anchor.length) continue;
                    var origTop = item.isPinned ? getElementDocTop(item.$placeholder) : getElementDocTop(item.$el);
                    var anchorTop = getElementDocTop(item.$anchor);
                    var natH = item.isPinned ? item.naturalHeight : (item.$el.outerHeight() || 100);

                    // If line is in the range where this material pins (from card natural top until anchor release)
                    if (lineDocTop >= origTop && lineDocTop <= anchorTop) {
                        var cardH = item.isExpanded
                            ? Math.min(natH, Math.round(window.innerHeight * 0.78))
                            : Math.min(natH, getMaxPinnedHeight());
                        var expectedBottom = navH + cardH + 24; // Card height + navbar + 24px safety buffer
                        if (expectedBottom > topObstruction) {
                            topObstruction = expectedBottom;
                        }
                    }
                }
            }

            var viewportH = window.innerHeight || 600;
            var availableH = Math.max(160, viewportH - topObstruction);

            // Viewing zone: top ~15% of available space below obstruction, bottom ~70%
            var zoneTop = topObstruction + Math.round(availableH * 0.15);
            var zoneBottom = topObstruction + Math.round(availableH * 0.70);

            return {
                topObstruction: topObstruction,
                zoneTop: zoneTop,
                zoneBottom: zoneBottom,
                viewportH: viewportH
            };
        }

        function scrollToLine($line) {
            if (!isAutoScrollEnabled || !$line || !$line.length || isUserInteracting) return;

            var zone = getViewingZone($line);
            var elTop = $line.offset().top;
            var elHeight = $line.outerHeight() || 24;
            var viewportTop = window.scrollY || window.pageYOffset || 0;

            var lineTopInView = elTop - viewportTop;
            var lineBottomInView = lineTopInView + elHeight;

            var inZone = (lineTopInView >= (zone.zoneTop - 20) && lineBottomInView <= (zone.zoneBottom + 20));

            if (isAutoscrollPausedByManualScroll) {
                if (inZone) {
                    // Audio naturally caught up with the user's reading position; resume autoscroll
                    isAutoscrollPausedByManualScroll = false;
                } else {
                    // Active line is outside user view: do not yank page
                    return;
                }
            }

            // If line is comfortably inside reading zone and NOT behind top obstruction:
            if (lineTopInView >= zone.topObstruction && lineTopInView >= (zone.zoneTop - 10) && lineBottomInView <= zone.zoneBottom) {
                return;
            }

            // When line reaches or passes bottom boundary, smooth scroll to zone top with S-curve
            if (lineBottomInView > zone.zoneBottom || lineTopInView > zone.zoneBottom) {
                var targetScrollY = elTop - zone.zoneTop;
                smoothScrollTo(Math.max(0, targetScrollY));
                return;
            }

            // If line is above or hidden behind the header/pinned obstruction, bring it to zone top with S-curve
            if (lineTopInView < zone.topObstruction || lineTopInView < zone.zoneTop) {
                var targetScrollYTop = elTop - zone.zoneTop;
                smoothScrollTo(Math.max(0, targetScrollYTop));
            }
        }

        // --- Locate Button Controller ---
        function updateLocateButtonVisibility() {
            if (!isPlayerPlusActive()) {
                $('.player-plus-btn-locate').removeClass('is-visible');
                return;
            }

            var cursorId = activeLineId || pausedLineId;
            if (!cursorId) {
                $('.player-plus-btn-locate').removeClass('is-visible');
                return;
            }

            var $el = $('#' + cursorId);
            if (!$el.length || !$el.is(':visible')) {
                $('.player-plus-btn-locate').removeClass('is-visible');
                return;
            }

            var zone = getViewingZone($el);
            var rect = $el[0].getBoundingClientRect();
            var winH = window.innerHeight || document.documentElement.clientHeight || 600;

            // Visible in field: element's top is below top obstruction and its top is above viewport bottom
            var isVisibleInField = (rect.top >= zone.topObstruction && rect.bottom > (zone.topObstruction + 10) && rect.top < (winH - 10));

            // User directive: "если курсор за пределами поля, то показывать. А если он виден, то не показывать."
            $('.player-plus-btn-locate').toggleClass('is-visible', !isVisibleInField);
        }

        function locateActiveLine() {
            var cursorId = activeLineId || pausedLineId;
            if (!cursorId) {
                cursorId = getFirstLineId();
            }
            if (!cursorId) return;

            var $line = $('#' + cursorId);
            if (!$line.length) return;

            isAutoscrollPausedByManualScroll = false;

            isUserInteracting = true;
            clearTimeout(userInteractTimer);
            userInteractTimer = setTimeout(function () {
                isUserInteracting = false;
                updateLocateButtonVisibility();
            }, 800);

            var zone = getViewingZone($line);
            var elTop = $line.offset().top;
            var targetScrollY = elTop - zone.zoneTop;
            smoothScrollTo(Math.max(0, targetScrollY));

            setTimeout(updateLocateButtonVisibility, 400);
        }

        $(document).on('click', '.player-plus-btn-locate', function (e) {
            e.preventDefault();
            e.stopPropagation();
            locateActiveLine();
        });

        $(document).on('click', '.player-plus-time', function (e) {
            e.preventDefault();
            e.stopPropagation();
            locateActiveLine();
        });

        // --- Sticky Educational Materials Controller ---
        function getElementDocTop($el) {
            if (!$el || !$el.length) return 0;
            var el = $el[0];
            if (el.getClientRects && el.getClientRects().length > 0) {
                var t = $el.offset().top;
                if (t > 0) return t;
            }
            // Fallback for empty inline spans: use parent element (h3, p, etc.)
            var $parent = $el.parent();
            if ($parent.length && !$parent.is('body, html, #playerPlus')) {
                var pTop = $parent.offset().top;
                if (pTop > 0) return pTop;
            }
            var $next = $el.next();
            if ($next.length) {
                var nTop = $next.offset().top;
                if (nTop > 0) return nTop;
            }
            return $el.offset().top || 0;
        }

        function getMaxPinnedHeight() {
            var vh = window.innerHeight || document.documentElement.clientHeight || 600;
            var isMobile = (window.innerWidth || document.documentElement.clientWidth || 360) < 768;
            return isMobile ? Math.min(260, Math.round(vh * 0.38)) : Math.min(340, Math.round(vh * 0.40));
        }

        var $stickyControls = null;

        function getStickyControls() {
            if (!$stickyControls || !$stickyControls.length) {
                $stickyControls = $('#stickyMaterialControls');
                if (!$stickyControls.length) {
                    $stickyControls = $(
                        '<div class="sticky-material-controls" id="stickyMaterialControls">' +
                        '    <button type="button" class="sticky-material-ctrl-btn sticky-material-btn-expand" title="Развернуть" aria-label="Развернуть">' +
                        '        <svg class="sticky-icon-expand" viewBox="0 0 24 24" width="13" height="13" stroke="currentColor" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round">' +
                        '            <polyline points="15 3 21 3 21 9"></polyline>' +
                        '            <polyline points="9 21 3 21 3 15"></polyline>' +
                        '            <line x1="21" y1="3" x2="14" y2="10"></line>' +
                        '            <line x1="3" y1="21" x2="10" y2="14"></line>' +
                        '        </svg>' +
                        '        <svg class="sticky-icon-collapse" viewBox="0 0 24 24" width="13" height="13" stroke="currentColor" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round" style="display:none;">' +
                        '            <polyline points="4 14 10 14 10 20"></polyline>' +
                        '            <polyline points="20 10 14 10 14 4"></polyline>' +
                        '            <line x1="14" y1="10" x2="21" y2="3"></line>' +
                        '            <line x1="3" y1="21" x2="10" y2="14"></line>' +
                        '        </svg>' +
                        '    </button>' +
                        '    <span class="sticky-material-ctrl-divider"></span>' +
                        '    <button type="button" class="sticky-material-ctrl-btn sticky-material-btn-dismiss" title="Открепить" aria-label="Закрыть">' +
                        '        <svg viewBox="0 0 24 24" width="12" height="12" stroke="currentColor" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round">' +
                        '            <line x1="18" y1="6" x2="6" y2="18"></line>' +
                        '            <line x1="6" y1="6" x2="18" y2="18"></line>' +
                        '        </svg>' +
                        '    </button>' +
                        '</div>'
                    );
                    $('body').append($stickyControls);

                    $stickyControls.on('click', '.sticky-material-btn-expand', function (e) {
                        e.preventDefault();
                        e.stopPropagation();
                        if (currentPinnedItem) {
                            currentPinnedItem.isExpanded = !currentPinnedItem.isExpanded;
                            currentPinnedItem.$el.toggleClass('is-expanded', currentPinnedItem.isExpanded);
                            var $btn = $(this);
                            $btn.attr('title', currentPinnedItem.isExpanded ? 'Свернуть' : 'Развернуть');
                            $btn.find('.sticky-icon-expand').toggle(!currentPinnedItem.isExpanded);
                            $btn.find('.sticky-icon-collapse').toggle(currentPinnedItem.isExpanded);
                            updateStickyMaterials();
                        }
                    });

                    $stickyControls.on('click', '.sticky-material-btn-dismiss', function (e) {
                        e.preventDefault();
                        e.stopPropagation();
                        if (currentPinnedItem) {
                            currentPinnedItem.isDismissed = true;
                            unpinItem(currentPinnedItem);
                            requestUpdateStickyMaterials();
                        }
                    });
                }
            }
            return $stickyControls;
        }

        function updateStickyControlsPosition(item, activeHeight) {
            if (!item || !item.isPinned) return;
            var $ctrl = getStickyControls();
            var $el = item.$el;
            var elH = activeHeight !== undefined ? activeHeight : $el.outerHeight();
            var topY = item.currentTop;
            var pOffset = item.$placeholder.offset();
            var pLeft = pOffset.left - (window.pageXOffset || document.documentElement.scrollLeft || 0);
            var pWidth = $el.outerWidth();

            var winW = window.innerWidth || document.documentElement.clientWidth || 360;
            var winH = window.innerHeight || document.documentElement.clientHeight || 600;

            var ctrlW = $ctrl.outerWidth() || 56;
            var btnTop = Math.round(topY + elH + 4);
            var btnLeft = Math.round(pLeft + pWidth - ctrlW - 8);

            btnLeft = Math.max(10, Math.min(winW - ctrlW - 12, btnLeft));
            if (btnTop > winH - 34) {
                btnTop = winH - 34;
            }

            var maxPinnedH = getMaxPinnedHeight();
            var canExpand = item.naturalHeight > (maxPinnedH + 20);
            $ctrl.find('.sticky-material-btn-expand').toggle(canExpand);
            $ctrl.find('.sticky-material-ctrl-divider').toggle(canExpand);

            var $expandBtn = $ctrl.find('.sticky-material-btn-expand');
            $expandBtn.attr('title', item.isExpanded ? 'Свернуть' : 'Развернуть');
            $expandBtn.find('.sticky-icon-expand').toggle(!item.isExpanded);
            $expandBtn.find('.sticky-icon-collapse').toggle(item.isExpanded);

            $ctrl.css({
                top: btnTop + 'px',
                left: btnLeft + 'px'
            }).addClass('is-visible');
        }

        function initStickyMaterials() {
            stickyMaterialsInitialized = true;
            // Unpin any active item before reinitializing
            if (currentPinnedItem) {
                unpinItem(currentPinnedItem);
            }
            for (var k = 0; k < stickyMaterials.length; k++) {
                if (stickyMaterials[k].isPinned) {
                    unpinItem(stickyMaterials[k]);
                }
            }
            stickyMaterials = [];

            $('#playerPlus [data-sticky-until]').each(function (idx) {
                var $el = $(this);
                var anchorId = $el.attr('data-sticky-until');
                var anchorEl = anchorId ? document.getElementById(anchorId) : null;
                if (!anchorEl) return;

                // Cache original style in jQuery data once
                var origStyle = $el.data('original-inline-style');
                if (origStyle === undefined) {
                    origStyle = $el.attr('style') || '';
                    $el.data('original-inline-style', origStyle);
                }

                var $placeholder = $el.prev('.sticky-material-placeholder');
                if (!$placeholder.length) {
                    $placeholder = $('<div class="sticky-material-placeholder" style="display:none;"></div>');
                    $el.before($placeholder);
                }

                stickyMaterials.push({
                    id: 'sticky_mat_' + idx,
                    $el: $el,
                    $placeholder: $placeholder,
                    anchorId: anchorId,
                    $anchor: $(anchorEl),
                    originalStyle: origStyle,
                    isPinned: false,
                    isDismissed: false,
                    isExpanded: false,
                    currentTop: 0,
                    naturalHeight: 0,
                    naturalWidth: 0,
                    naturalLeft: 0,
                    pinnedHeight: 0
                });
            });
        }

        function unpinItem(item) {
            if (!item || !item.isPinned) return;
            item.isPinned = false;
            item.isExpanded = false;
            item.$el.removeClass('is-sticky-pinned is-expanded');
            var origStyle = item.$el.data('original-inline-style');
            if (origStyle !== undefined && origStyle !== null && origStyle !== '') {
                item.$el.attr('style', origStyle);
            } else {
                item.$el.removeAttr('style');
            }
            if (item.$placeholder) {
                item.$placeholder.hide();
            }
            if ($stickyControls) {
                $stickyControls.removeClass('is-visible');
            }
            if (currentPinnedItem === item) {
                currentPinnedItem = null;
            }
        }

        function pinItem(item, topY, navH, activeHeight) {
            var $placeholder = item.$placeholder;
            var $el = item.$el;

            if (!item.isPinned) {
                // Measure natural dimensions in flow before detaching
                var naturalHeight = $el.outerHeight();
                var naturalWidth = $el.outerWidth();
                var elOffset = $el.offset();

                if (naturalWidth < 50 || naturalHeight < 20) {
                    return;
                }

                item.naturalHeight = naturalHeight;
                item.naturalWidth = naturalWidth;
                item.naturalLeft = elOffset.left;

                $placeholder.css({
                    width: naturalWidth + 'px',
                    height: naturalHeight + 'px',
                    marginTop: $el.css('marginTop'),
                    marginBottom: $el.css('marginBottom'),
                    marginLeft: $el.css('marginLeft'),
                    marginRight: $el.css('marginRight')
                }).show();

                item.isPinned = true;
                $el.addClass('is-sticky-pinned');
                $el.scrollTop(0);
            }

            var pOffset = $placeholder.offset();
            var pLeft = pOffset.left - (window.pageXOffset || document.documentElement.scrollLeft || 0);
            var pWidth = $placeholder.outerWidth() || item.naturalWidth;

            if (pLeft <= 0 && item.naturalLeft > 0) {
                pLeft = item.naturalLeft - (window.pageXOffset || document.documentElement.scrollLeft || 0);
            }

            item.currentTop = topY;
            item.pinnedHeight = activeHeight;

            $el.css({
                position: 'fixed',
                top: Math.round(topY) + 'px',
                left: Math.round(pLeft) + 'px',
                width: Math.round(pWidth) + 'px',
                height: Math.round(activeHeight) + 'px',
                marginTop: 0,
                marginBottom: 0
            });

            currentPinnedItem = item;
            updateStickyControlsPosition(item, activeHeight);
        }

        function updateStickyMaterials() {
            if (!isPlayerPlusActive() || !isStickyMaterialsEnabled) {
                if (currentPinnedItem) {
                    unpinItem(currentPinnedItem);
                }
                for (var k = 0; k < stickyMaterials.length; k++) {
                    if (stickyMaterials[k].isPinned) {
                        unpinItem(stickyMaterials[k]);
                    }
                }
                if ($stickyControls) {
                    $stickyControls.removeClass('is-visible');
                }
                return;
            }

            if (!stickyMaterialsInitialized) {
                initStickyMaterials();
            }
            if (!stickyMaterials.length) return;

            var scrollY = window.pageYOffset || document.documentElement.scrollTop || 0;
            var navH = getNavbarHeight();

            var activeCandidate = null;
            var candidateTop = navH;
            var candidateHeight = 0;

            for (var i = 0; i < stickyMaterials.length; i++) {
                var item = stickyMaterials[i];
                if (!item.$anchor || !item.$anchor.length) continue;

                var origTop = item.isPinned ? getElementDocTop(item.$placeholder) : getElementDocTop(item.$el);
                var natH = item.isPinned ? item.naturalHeight : (item.$el.outerHeight() || 100);
                var anchorTop = getElementDocTop(item.$anchor);

                // CRITICAL SAFETY GUARDS:
                if (origTop <= (navH + 10)) {
                    continue;
                }
                if (anchorTop <= origTop) {
                    continue;
                }

                // If user scrolled back up above the item's natural top position, clear dismissed state
                if (item.isDismissed && scrollY < (origTop - navH - 40)) {
                    item.isDismissed = false;
                }

                if (item.isDismissed) {
                    continue;
                }

                var maxPinnedH = getMaxPinnedHeight();
                var targetH = item.isExpanded ? Math.min(natH, Math.round(window.innerHeight * 0.78)) : Math.min(natH, maxPinnedH);

                var currentH = targetH;
                if (!item.isExpanded) {
                    // DYNAMIC TEXT-FOLLOWING COMPRESSION:
                    // 1. As top of card reaches navbar, it pins at navH.
                    // 2. The document text begins at (origTop + natH).
                    // In viewport coordinates, distance from navH down to text is:
                    var distanceToText = (origTop + natH) - scrollY - navH;

                    // 3. While distanceToText > targetH, the bottom border of the card is pushed up
                    // in exact lockstep by the scrolling text: card height = distanceToText.
                    // 4. Once distanceToText <= targetH, height freezes at targetH, and text slides underneath.
                    currentH = Math.max(targetH, Math.min(natH, distanceToText));
                }

                var pinStart = origTop - navH;
                var pushStart = anchorTop - navH - currentH;
                var releaseEnd = anchorTop - navH;

                if (scrollY >= pinStart && scrollY < releaseEnd) {
                    var topY = navH;
                    if (scrollY >= pushStart) {
                        topY = (anchorTop - scrollY) - currentH;
                    }
                    activeCandidate = item;
                    candidateTop = topY;
                    candidateHeight = currentH;
                }
            }

            for (var j = 0; j < stickyMaterials.length; j++) {
                var it = stickyMaterials[j];
                if (it !== activeCandidate && it.isPinned) {
                    unpinItem(it);
                }
            }

            if (activeCandidate) {
                pinItem(activeCandidate, candidateTop, navH, candidateHeight);
            } else if (currentPinnedItem) {
                unpinItem(currentPinnedItem);
            }
            updateLocateButtonVisibility();
        }

        function requestUpdateStickyMaterials() {
            if (!stickyRafPending) {
                stickyRafPending = true;
                requestAnimFrame(function () {
                    stickyRafPending = false;
                    updateStickyMaterials();
                    updateLocateButtonVisibility();
                });
            }
        }

        $(window).on('scroll.playerPlusSticky', requestUpdateStickyMaterials);
        $(window).on('resize.playerPlusSticky', function () {
            updateStickyMaterials();
            updateLocateButtonVisibility();
        });
        $(document).on('shown.bs.tab', function () {
            if (isPlayerPlusActive()) {
                initStickyMaterials();
                updateStickyMaterials();
            } else {
                updateStickyMaterials();
            }
            updateLocateButtonVisibility();
        });

        // --- Settings Drawer & LocalStorage ---
        $(document).on('click', '.player-plus-btn-settings', function (e) {
            e.stopPropagation();
            var $bar = $(this).closest('.player-plus-bar');
            var $drawer = $bar.find('.player-plus-drawer');
            var isOpen = $drawer.hasClass('is-open');

            $('.player-plus-drawer').removeClass('is-open');
            $('.player-plus-btn-settings').removeClass('is-active');
            $('.player-plus-toc-wrapper').removeClass('is-open');

            if (!isOpen) {
                $drawer.addClass('is-open');
                $(this).addClass('is-active');
            }
        });

        $(document).on('click', '.player-plus-drawer-close', function (e) {
            e.stopPropagation();
            $('.player-plus-drawer').removeClass('is-open');
            $('.player-plus-btn-settings').removeClass('is-active');
        });

        $(document).on('click', function (e) {
            if (!$(e.target).closest('.player-plus-bar').length) {
                $('.player-plus-drawer').removeClass('is-open');
                $('.player-plus-btn-settings').removeClass('is-active');
            }
            if (!$(e.target).closest('.player-plus-toc-wrapper').length) {
                $('.player-plus-toc-wrapper').removeClass('is-open');
            }
        });

        // Sync switches
        $(document).on('change', '.player-plus-toggle-autoscroll', function () {
            isAutoScrollEnabled = this.checked;
            localStorage.setItem('playerPlus_autoscroll', isAutoScrollEnabled ? 'true' : 'false');
            $('.player-plus-toggle-autoscroll').prop('checked', isAutoScrollEnabled);
        });

        $(document).on('change', '.player-plus-toggle-stickymaterials', function () {
            isStickyMaterialsEnabled = this.checked;
            localStorage.setItem('playerPlus_stickyMaterials', isStickyMaterialsEnabled ? 'true' : 'false');
            $('.player-plus-toggle-stickymaterials').prop('checked', isStickyMaterialsEnabled);
            updateStickyMaterials();
        });

        // --- Chapter Pull-Tab & Curtain Handlers ---
        $(document).on('click', '.player-plus-toc-tab', function (e) {
            e.stopPropagation();
            var $wrapper = $(this).closest('.player-plus-toc-wrapper');
            var isOpen = $wrapper.hasClass('is-open');
            $('.player-plus-toc-wrapper').removeClass('is-open');
            $('.player-plus-drawer').removeClass('is-open');
            $('.player-plus-btn-settings').removeClass('is-active');
            if (!isOpen) {
                $wrapper.addClass('is-open');
                var $curr = $wrapper.find('.player-plus-toc-item.is-current:visible');
                if ($curr.length) {
                    var $list = $wrapper.find('.player-plus-toc-list');
                    var currTop = $curr.position().top;
                    if (currTop < 0 || currTop > $list.height()) {
                        $list.scrollTop($list.scrollTop() + currTop - 30);
                    }
                }
            }
        });

        $(document).on('click', '.player-plus-toc-close', function (e) {
            e.stopPropagation();
            $('.player-plus-toc-wrapper').removeClass('is-open');
        });

        // Depth switcher: I, I.1, I.1.a
        $(document).on('click', '.player-plus-toc-level-btn', function (e) {
            e.stopPropagation();
            var depth = parseInt($(this).data('depth'), 10) || 1;
            applyTOCDepth(depth);
        });

        // Chevron click: expand / collapse individual branch in accordion
        $(document).on('click', '.player-plus-toc-chevron', function (e) {
            e.stopPropagation();
            e.preventDefault();
            var $item = $(this).closest('.player-plus-toc-item');
            var chId = $item.data('ch-id');
            var ch = chaptersById[chId];
            if (!ch || !ch.hasChildren) return;

            ch.isExpanded = !ch.isExpanded;
            updateTOCVisibilityDOM();
            updateSegmentedSwitcherState();
        });

        // Selecting a chapter in TOC: seek, pause (do not auto-play), highlight replica, center heading, close curtain
        $(document).on('click', '.player-plus-toc-item', function (e) {
            if ($(e.target).closest('.player-plus-toc-chevron').length) {
                return;
            }
            var $item = $(this);
            var startSec = parseFloat($item.data('start-sec'));
            var headingId = $item.data('heading-id');
            var lineId = $item.data('line-id');

            var a = getAudio();
            if (a) {
                a.currentTime = startSec;
                a.pause();
                syncPlayPauseUI(false);
            }

            if (lineId) {
                setPausedHighlight(lineId);
            }

            isAutoscrollPausedByManualScroll = false;
            $('.player-plus-toc-wrapper').removeClass('is-open');

            var $h = $('#' + headingId);
            if ($h.length) {
                isUserInteracting = true;
                clearTimeout(userInteractTimer);
                userInteractTimer = setTimeout(function () {
                    isUserInteracting = false;
                }, 1500);

                var headingTop = $h.offset().top;
                var headingHeight = $h.outerHeight() || 0;
                var targetY = headingTop - (window.innerHeight / 2) + (headingHeight / 2);
                smoothScrollTo(Math.max(0, targetY));
            }
        });
    });
})(jQuery);
