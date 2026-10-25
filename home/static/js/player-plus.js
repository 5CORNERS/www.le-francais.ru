(function ($) {
    'use strict';

    $(document).ready(function () {
        const $playerPlusTab = $('#playerPlusTab');
        const $playerPlusPane = $('#playerPlus');

        // Only initialize if Player+ tab exists on this page
        if (!$playerPlusTab.length && !$playerPlusPane.length) {
            return;
        }

        const transcriptMap = (typeof window.transcriptMap === 'string')
            ? (function () { try { return JSON.parse(window.transcriptMap); } catch (e) { return []; } })()
            : (window.transcriptMap || []);
        let chapters = [];
        let chaptersById = {};
        let currentDepth = 3;

        // --- Settings & LocalStorage ---
        let isAutoScrollEnabled = localStorage.getItem('playerPlus_autoscroll') !== 'false'; // default true
        let isStickyMaterialsEnabled = localStorage.getItem('playerPlus_stickyMaterials') !== 'false'; // default true
        let isUserInteracting = false;
        let userInteractTimer = null;
        let isAutoscrollPausedByManualScroll = false;
        let isScrubbing = false;
        let activeLineId = null;
        let pausedLineId = null;

        let activeScrollAnim = null;
        let stickyMaterials = [];
        let stickyMaterialsInitialized = false;
        let currentPinnedItem = null;
        let $stickyControls = null;
        let stickyRafPending = false;
        const requestAnimFrame = window.requestAnimationFrame || function (cb) { return setTimeout(cb, 16); };
        const cancelAnimFrame = window.cancelAnimationFrame || function (id) { clearTimeout(id); };

        // S-curve smooth scroll with gentle acceleration and deceleration (cosine S-curve)
        function smoothScrollTo(targetY, customDuration) {
            if (activeScrollAnim) {
                cancelAnimFrame(activeScrollAnim);
                activeScrollAnim = null;
            }

            const startY = window.scrollY || window.pageYOffset || document.documentElement.scrollTop || 0;
            const distance = targetY - startY;
            if (Math.abs(distance) < 2) return;

            // Slower, comfortable reading speed: 850ms to 1250ms depending on distance
            const duration = customDuration || Math.max(850, Math.min(1250, Math.round(700 + Math.abs(distance) * 0.9)));
            let startTime = null;

            function sCurveEase(t) {
                // Cosine S-curve: f(0)=0 (zero slope), f(0.5)=0.5, f(1)=1 (zero slope)
                return (1 - Math.cos(t * Math.PI)) / 2;
            }

            function step(timestamp) {
                if (!startTime) startTime = timestamp;
                const elapsed = timestamp - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const ease = sCurveEase(progress);

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
                const $active = activeLineId ? $('#' + activeLineId) : null;
                if ($active && $active.length) {
                    const zone = getViewingZone();
                    const lineTopInView = $active.offset().top - (window.scrollY || window.pageYOffset || 0);
                    const lineBottomInView = lineTopInView + ($active.outerHeight() || 24);
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
            const $topMenu = $('#topMenu');
            return ($topMenu.length && $topMenu.is(':visible')) ? $topMenu.outerHeight() : 48;
        }

        function getStickyPinTop() {
            const navH = getNavbarHeight();
            const $floatingWrapper = $('#lessonTabsFloatingWrapper');
            const isDockVisible = ($floatingWrapper.length && $floatingWrapper.is(':visible') && !$floatingWrapper.hasClass('is-hidden') && $floatingWrapper.css('opacity') !== '0');
            const dockH = isDockVisible ? $floatingWrapper.outerHeight() : 0;
            return navH + dockH;
        }

        function getAudio() {
            return $('#newAudioTranscript')[0];
        }

        function isPlayerPlusActive() {
            const $p = $('#playerPlus');
            const $t = $('#playerPlusTab');
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
            const rawItems = [];
            const rawLevelsSet = {};

            $('#playerPlus').find('h1, h2, h3, h4, h5, h6').each(function (idx) {
                const $h = $(this);
                const title = $h.text().replace(/\s+/g, ' ').trim();
                if (!title || title.indexOf('Этот транскрипт') !== -1) return;

                let hId = $h.attr('id');
                if (!hId) {
                    hId = 'pp_heading_' + idx;
                    $h.attr('id', hId);
                }

                const rawLevel = parseInt(this.tagName.substring(1), 10) || 2;

                // Traverse DOM to find the first .transcript-line following this heading
                let $nextLine = $h.nextAll().find('.transcript-line').add($h.nextAll('.transcript-line')).first();
                if (!$nextLine.length) {
                    let $parent = $h.parent();
                    while ($parent.length && !$parent.is('#playerPlus') && !$nextLine.length) {
                        $nextLine = $parent.nextAll().find('.transcript-line').add($parent.nextAll('.transcript-line')).first();
                        $parent = $parent.parent();
                    }
                }

                if ($nextLine.length) {
                    const startMs = parseFloat($nextLine.data('start')) || 0;
                    const startSec = startMs / 1000;
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
            const sortedRawLevels = Object.keys(rawLevelsSet).map(function (k) {
                return parseInt(k, 10);
            }).sort(function (a, b) {
                return a - b;
            });

            rawItems.forEach(function (item) {
                const normLevel = sortedRawLevels.indexOf(item.rawLevel) + 1;
                item.level = Math.min(normLevel, 3);
                item.hasChildren = false;
                item.parentId = null;
                item.childIds = [];
                item.isExpanded = true;
            });

            // Build hierarchy links
            const lastAtLevel = {};
            rawItems.forEach(function (item) {
                let parent = null;
                for (let lvl = item.level - 1; lvl >= 1; lvl--) {
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
                for (let d = item.level + 1; d <= 3; d++) {
                    delete lastAtLevel[d];
                }
            });

            return rawItems;
        }

        // --- TOC Visibility & Accordion Helpers ---
        function isChapterVisible(ch) {
            let cur = ch;
            while (cur && cur.parentId) {
                const parent = chaptersById[cur.parentId];
                if (!parent || !parent.isExpanded) {
                    return false;
                }
                cur = parent;
            }
            return true;
        }

        function updateTOCVisibilityDOM() {
            chapters.forEach(function (ch) {
                const isVis = isChapterVisible(ch);
                const $items = $('.player-plus-toc-item[data-ch-id="' + ch.id + '"]');
                if (isVis) {
                    $items.removeClass('is-hidden').show();
                } else {
                    $items.addClass('is-hidden').hide();
                }

                if (ch.hasChildren) {
                    const $chevrons = $items.find('.player-plus-toc-chevron');
                    if (ch.isExpanded) {
                        $chevrons.removeClass('is-collapsed').addClass('is-expanded');
                    } else {
                        $chevrons.removeClass('is-expanded').addClass('is-collapsed');
                    }
                }
            });
        }

        function updateSegmentedSwitcherState() {
            const l1WithChildren = chapters.filter(function (c) { return c.level === 1 && c.hasChildren; });
            const l2WithChildren = chapters.filter(function (c) { return c.level === 2 && c.hasChildren; });

            const allL1Expanded = l1WithChildren.length > 0 && l1WithChildren.every(function (c) { return c.isExpanded; });
            const allL1Collapsed = l1WithChildren.length > 0 && l1WithChildren.every(function (c) { return !c.isExpanded; });

            const allL2Expanded = l2WithChildren.length > 0 && l2WithChildren.every(function (c) { return c.isExpanded; });
            const allL2Collapsed = l2WithChildren.length > 0 && l2WithChildren.every(function (c) { return !c.isExpanded; });

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

            let maxDepth = 1;
            chapters.forEach(function (ch) {
                if (ch.level > maxDepth) maxDepth = ch.level;
            });

            $('.player-plus-toc-list').each(function () {
                const $list = $(this);
                $list.empty();
                if (!chapters.length) {
                    $list.append('<div style="padding: 12px 16px; color: #adb5bd; font-size: 0.8rem; text-align: center;">Оглавление не найдено</div>');
                    return;
                }
                chapters.forEach(function (ch) {
                    let chevronOrSpacerHtml = '';
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

                    const $item = $(
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

            const $switchers = $('.player-plus-toc-level-switcher');
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
        const $naturalContainer = $('#playerPlusNaturalContainer');
        if ($naturalContainer.length && !$('#naturalPlayerPlusBar').length) {
            $naturalContainer.append(getPlayerPlusBarHtml('natural', 'player-plus-bar-natural'));
        }

        // 2. Floating bar: attach inside floating tabs dock
        function attachFloatingBar() {
            const $floatingWrapper = $('#lessonTabsFloatingWrapper');
            if ($floatingWrapper.length && !$('#floatingPlayerPlusBar').length) {
                const $inner = $floatingWrapper.find('.lesson-tabs-floating-inner');
                if ($inner.length) {
                    const $floatingBar = $(getPlayerPlusBarHtml('floating', 'player-plus-bar-floating'));
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
            const isPlayerPlus = isPlayerPlusActive();
            const $floatingWrapper = $('#lessonTabsFloatingWrapper');
            const isDockHidden = $floatingWrapper.length ? $floatingWrapper.hasClass('is-hidden') : true;
            const $floatingBar = $('#floatingPlayerPlusBar');
            const $floatingToc = $('#floatingPlayerPlusTocWrapper');

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

        // --- Mobile Device Helper ---
        function isMobileDevice() {
            const width = window.innerWidth || document.documentElement.clientWidth || 0;
            const hasTouch = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0) || (navigator.msMaxTouchPoints > 0);
            return width < 768 || (hasTouch && width < 992);
        }

        // --- Time Formatting Helper ---
        function formatTime(seconds) {
            if (isNaN(seconds) || seconds < 0) return '00:00';
            const s = Math.floor(seconds);
            const m = Math.floor(s / 60);
            const ss = s % 60;
            const h = Math.floor(m / 60);
            const mm = m % 60;
            if (h > 0) {
                return h + ':' + (mm < 10 ? '0' : '') + mm + ':' + (ss < 10 ? '0' : '') + ss;
            }
            return (mm < 10 ? '0' : '') + mm + ':' + (ss < 10 ? '0' : '') + ss;
        }

        // --- Sync Play/Pause State ---
        function syncPlayPauseUI(isPlaying) {
            const $bars = $('.player-plus-bar');
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
            const a = getAudio();
            if (!a) return;
            if (a.paused) {
                if (pausedLineId) {
                    setPlayingHighlight(pausedLineId);
                    if (isAutoScrollEnabled) {
                        scrollToLine($('#' + pausedLineId));
                    }
                }
                const p = a.play();
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

                const tag = (document.activeElement && document.activeElement.tagName)
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
            const a = getAudio();
            if (!a) return;
            const cur = a.currentTime || 0;
            const dur = a.duration || 0;

            $('.player-plus-current-time').text(formatTime(cur));
            if (dur > 0) {
                $('.player-plus-total-time').text(formatTime(dur));
                const percent = Math.min(100, Math.max(0, (cur / dur) * 100));
                $('.player-plus-progress-bar-fill').css('width', percent + '%');
            }

            // Update buffered
            if (a.buffered && a.buffered.length > 0 && dur > 0) {
                try {
                    const bufferedEnd = a.buffered.end(a.buffered.length - 1);
                    const bufPercent = Math.min(100, Math.max(0, (bufferedEnd / dur) * 100));
                    $('.player-plus-progress-buffered').css('width', bufPercent + '%');
                } catch (err) {}
            }

            // Update active chapter in curtain
            if (chapters && chapters.length) {
                let activeChapIdx = -1;
                for (let i = 0; i < chapters.length; i++) {
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
            const a = getAudio();
            if (!a) return;

            // Remove prior listeners to avoid duplicate firing
            $(a).off('.playerPlus');

            $(a).on('timeupdate.playerPlus', function () {
                updateProgressAndTimes();

                // On pause, do not update playback highlighting
                if (a.paused) return;

                const currentMs = a.currentTime * 1000;
                const item = findItemAtTime(currentMs);
                const newId = item ? item.id : null;

                if (newId && newId !== activeLineId) {
                    setPlayingHighlight(newId);
                    if (isAutoScrollEnabled) {
                        scrollToLine($('#' + newId));
                    }
                    requestUpdateStickyMaterials();
                } else if (activeLineId && isAutoScrollEnabled && !isAutoscrollPausedByManualScroll && !isUserInteracting) {
                    const $active = $('#' + activeLineId);
                    if ($active.length) {
                        const z = getViewingZone($active);
                        const topInView = $active.offset().top - (window.scrollY || window.pageYOffset || 0);
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
                    const currentMs = a.currentTime * 1000;
                    const item = findItemAtTime(currentMs);
                    setPlayingHighlight(item ? item.id : null);
                }
            });

            $(a).on('pause.playerPlus', function () {
                syncPlayPauseUI(false);
                let lineToPause = activeLineId;
                if (!lineToPause) {
                    const currentMs = a.currentTime * 1000;
                    const item = findItemAtTime(currentMs);
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
            const a = getAudio();
            if (!a || !a.duration) return;

            const $track = $container.first().find('.player-plus-progress-track');
            const offset = $track.offset();
            const width = $track.width();
            if (width <= 0) return;

            const clientX = (e.originalEvent && e.originalEvent.touches)
                ? e.originalEvent.touches[0].clientX
                : e.clientX;

            const percent = Math.max(0, Math.min(1, (clientX - offset.left) / width));
            a.currentTime = percent * a.duration;

            if (a.paused) {
                const currentMs = a.currentTime * 1000;
                const item = findItemAtTime(currentMs);
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
            const firstStart = parseFloat(transcriptMap[0].start);
            if (!isNaN(firstStart) && timeMs < firstStart) {
                return transcriptMap[0];
            }

            const epsilon = 60; // 60ms tolerance for audio keyframe seeking & float precision

            // 1. Primary check: search backwards so the newest started phrase takes precedence in overlaps
            for (let i = transcriptMap.length - 1; i >= 0; i--) {
                const it = transcriptMap[i];
                const s = parseFloat(it.start);
                const e = parseFloat(it.end);
                if (timeMs >= (s - epsilon) && timeMs <= e) {
                    return it;
                }
            }

            // 2. Secondary fallback for gaps between phrases
            for (let j = transcriptMap.length - 1; j >= 0; j--) {
                const item = transcriptMap[j];
                const start = parseFloat(item.start);
                const end = parseFloat(item.end);
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
            const $first = $('#playerPlus .transcript-line').first();
            return $first.length ? $first.attr('id') : null;
        }

        function initInitialHighlight() {
            const a = getAudio();
            if (a && !a.paused) return;
            if (activeLineId || pausedLineId) return;
            const firstId = getFirstLineId();
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
                const $el = $('#' + lineId);
                $el.addClass('transcript-line-selected');

                // Prepend the small inline play button at the beginning of the replica
                if (!$el.find('.transcript-line-play-btn').length) {
                    const $playBtn = $(
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
            const startSec = parseFloat($(this).data('start')) / 1000;
            const lineId = $(this).attr('id');
            const a = getAudio();
            if (a) {
                // On mobile devices: tapping the currently sounding replica pauses playback
                if (isMobileDevice() && !a.paused && (lineId === activeLineId || $(this).hasClass('transcript-line-playing'))) {
                    a.pause();
                    return;
                }

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
            const a = getAudio();
            if (!a) return;
            const $line = $(this).closest('.transcript-line');
            const lineId = $line.attr('id');
            const startSec = parseFloat($line.data('start')) / 1000;
            if (lineId) {
                setPlayingHighlight(lineId);
                if (isAutoScrollEnabled) {
                    scrollToLine($line);
                }
            }
            a.currentTime = startSec;
            const p = a.play();
            if (p && p.catch) p.catch(function () {});
        });

        // --- Viewing Zone & Autoscroll Implementation ---
        function getViewingZone($line) {
            const pinTop = getStickyPinTop();
            let topObstruction = pinTop;

            // 1. Check if any sticky material is currently pinned
            if (isStickyMaterialsEnabled && currentPinnedItem) {
                const pinnedActualH = currentPinnedItem.$el.outerHeight() || currentPinnedItem.pinnedHeight || 0;
                const pinnedBottom = currentPinnedItem.currentTop + pinnedActualH + 20;
                if (pinnedBottom > topObstruction) {
                    topObstruction = pinnedBottom;
                }
            }

            // 2. Predictive check: will any sticky material be pinned when viewing $line?
            if (isStickyMaterialsEnabled && $line && $line.length) {
                const lineDocTop = $line.offset().top;
                for (let i = 0; i < stickyMaterials.length; i++) {
                    const item = stickyMaterials[i];
                    if (item.isDismissed || !item.$anchor || !item.$anchor.length) continue;
                    const origTop = item.isPinned ? getElementDocTop(item.$placeholder) : getElementDocTop(item.$el);
                    const anchorTop = getElementDocTop(item.$anchor);
                    const natH = item.isPinned ? item.naturalHeight : (item.$el.outerHeight() || 100);

                    // If line is in the range where this material pins (from card natural top until anchor release)
                    if (lineDocTop >= origTop && lineDocTop <= anchorTop) {
                        const cardH = item.isExpanded
                            ? Math.min(natH, Math.round(window.innerHeight * 0.78))
                            : Math.min(natH, getMaxPinnedHeight());
                        const expectedBottom = pinTop + cardH + 24; // Card height + pinTop + 24px safety buffer
                        if (expectedBottom > topObstruction) {
                            topObstruction = expectedBottom;
                        }
                    }
                }
            }

            const viewportH = window.innerHeight || 600;
            const availableH = Math.max(160, viewportH - topObstruction);

            // Viewing zone: top ~15% of available space below obstruction, bottom ~70%
            const zoneTop = topObstruction + Math.round(availableH * 0.15);
            const zoneBottom = topObstruction + Math.round(availableH * 0.70);

            return {
                topObstruction: topObstruction,
                zoneTop: zoneTop,
                zoneBottom: zoneBottom,
                viewportH: viewportH
            };
        }

        function scrollToLine($line) {
            if (!isAutoScrollEnabled || !$line || !$line.length || isUserInteracting) return;

            const zone = getViewingZone($line);
            const elTop = $line.offset().top;
            const elHeight = $line.outerHeight() || 24;
            const viewportTop = window.scrollY || window.pageYOffset || 0;

            const lineTopInView = elTop - viewportTop;
            const lineBottomInView = lineTopInView + elHeight;

            const inZone = (lineTopInView >= (zone.zoneTop - 20) && lineBottomInView <= (zone.zoneBottom + 20));

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
                const targetScrollY = elTop - zone.zoneTop;
                smoothScrollTo(Math.max(0, targetScrollY));
                return;
            }

            // If line is above or hidden behind the header/pinned obstruction, bring it to zone top with S-curve
            if (lineTopInView < zone.topObstruction || lineTopInView < zone.zoneTop) {
                const targetScrollYTop = elTop - zone.zoneTop;
                smoothScrollTo(Math.max(0, targetScrollYTop));
            }
        }

        // --- Locate Button Controller ---
        function updateLocateButtonVisibility() {
            if (!isPlayerPlusActive()) {
                $('.player-plus-btn-locate').removeClass('is-visible');
                return;
            }

            const cursorId = activeLineId || pausedLineId;
            if (!cursorId) {
                $('.player-plus-btn-locate').removeClass('is-visible');
                return;
            }

            const $el = $('#' + cursorId);
            if (!$el.length || !$el.is(':visible')) {
                $('.player-plus-btn-locate').removeClass('is-visible');
                return;
            }

            const zone = getViewingZone($el);
            const rect = $el[0].getBoundingClientRect();
            const winH = window.innerHeight || document.documentElement.clientHeight || 600;

            // Visible in field: element's top is below top obstruction and its top is above viewport bottom
            const isVisibleInField = (rect.top >= zone.topObstruction && rect.bottom > (zone.topObstruction + 10) && rect.top < (winH - 10));

            // User directive: "если курсор за пределами поля, то показывать. А если он виден, то не показывать."
            $('.player-plus-btn-locate').toggleClass('is-visible', !isVisibleInField);
        }

        function locateActiveLine() {
            let cursorId = activeLineId || pausedLineId;
            if (!cursorId) {
                cursorId = getFirstLineId();
            }
            if (!cursorId) return;

            const $line = $('#' + cursorId);
            if (!$line.length) return;

            isAutoscrollPausedByManualScroll = false;

            isUserInteracting = true;
            clearTimeout(userInteractTimer);
            userInteractTimer = setTimeout(function () {
                isUserInteracting = false;
                updateLocateButtonVisibility();
            }, 800);

            const zone = getViewingZone($line);
            const elTop = $line.offset().top;
            const targetScrollY = elTop - zone.zoneTop;
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
            const el = $el[0];
            if (el.getClientRects && el.getClientRects().length > 0) {
                const t = $el.offset().top;
                if (t > 0) return t;
            }
            // Fallback for empty inline spans: use parent element (h3, p, etc.)
            const $parent = $el.parent();
            if ($parent.length && !$parent.is('body, html, #playerPlus')) {
                const pTop = $parent.offset().top;
                if (pTop > 0) return pTop;
            }
            const $next = $el.next();
            if ($next.length) {
                const nTop = $next.offset().top;
                if (nTop > 0) return nTop;
            }
            return $el.offset().top || 0;
        }

        function getMaxPinnedHeight() {
            const vh = window.innerHeight || document.documentElement.clientHeight || 700;
            const pinTop = getStickyPinTop();
            // Allow card to occupy full available vertical viewport space minus 24px bottom buffer
            return Math.max(200, Math.round(vh - pinTop - 24));
        }

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
                            const $btn = $(this);
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
            const $ctrl = getStickyControls();
            const $el = item.$el;
            const elH = (item.pinnedIsTruncated && activeHeight !== undefined) ? activeHeight : $el.outerHeight();
            const topY = item.currentTop;
            const cardLeft = item.currentLeft || ($el.offset().left - (window.pageXOffset || document.documentElement.scrollLeft || 0));
            const cardWidth = item.currentWidth || $el.outerWidth();

            const winW = window.innerWidth || document.documentElement.clientWidth || 360;
            const winH = window.innerHeight || document.documentElement.clientHeight || 600;

            const ctrlW = $ctrl.outerWidth() || 56;
            let btnTop = Math.round(topY + elH + 4);
            let btnLeft = Math.round(cardLeft + cardWidth - ctrlW);

            btnLeft = Math.max(10, Math.min(winW - ctrlW - 12, btnLeft));
            if (btnTop > winH - 34) {
                btnTop = winH - 34;
            }

            const maxPinnedH = getMaxPinnedHeight();
            const canExpand = item.naturalHeight > (maxPinnedH + 20);
            $ctrl.find('.sticky-material-btn-expand').toggle(canExpand);
            $ctrl.find('.sticky-material-ctrl-divider').toggle(canExpand);

            const $expandBtn = $ctrl.find('.sticky-material-btn-expand');
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
            for (let k = 0; k < stickyMaterials.length; k++) {
                if (stickyMaterials[k].isPinned) {
                    unpinItem(stickyMaterials[k]);
                }
            }
            stickyMaterials = [];

            $('#playerPlus [data-sticky-until]').each(function (idx) {
                const $el = $(this);
                const anchorId = $el.attr('data-sticky-until');
                const anchorEl = anchorId ? document.getElementById(anchorId) : null;
                if (!anchorEl) return;

                // Cache original style in jQuery data once
                let origStyle = $el.data('original-inline-style');
                if (origStyle === undefined) {
                    origStyle = $el.attr('style') || '';
                    $el.data('original-inline-style', origStyle);
                }

                let $placeholder = $el.prev('.sticky-material-placeholder');
                if (!$placeholder.length) {
                    $placeholder = $('<div class="sticky-material-placeholder" style="display:none;"></div>');
                    $el.before($placeholder);
                }

                const $img = $el.find('img').first();
                const isImageWrapper = $img.length > 0 && !$el.hasClass('bs-callout');

                stickyMaterials.push({
                    id: 'sticky_mat_' + idx,
                    $el: $el,
                    $placeholder: $placeholder,
                    anchorId: anchorId,
                    $anchor: $(anchorEl),
                    originalStyle: origStyle,
                    isImageWrapper: isImageWrapper,
                    isPinned: false,
                    isDismissed: false,
                    isExpanded: false,
                    currentTop: 0,
                    currentLeft: 0,
                    currentWidth: 0,
                    naturalHeight: 0,
                    naturalWidth: 0,
                    naturalLeft: 0,
                    imgWidth: 0,
                    imgHeight: 0,
                    imgRelLeft: 0,
                    pinnedHeight: 0
                });
            });
        }

        function unpinItem(item, immediate) {
            if (!item || !item.isPinned) return;
            if (item.isLeaving) return; // Exit transition already running; keep going

            if (item.unpinTimer) {
                clearTimeout(item.unpinTimer);
                item.unpinTimer = null;
            }

            if (immediate) {
                cleanupUnpinnedItem(item);
                return;
            }

            // Animate exit: float up and blur/dissolve out over 350ms
            item.isLeaving = true;
            item.$el.addClass('is-sticky-leaving');
            if ($stickyControls && currentPinnedItem === item) {
                $stickyControls.addClass('is-leaving');
            }

            item.unpinTimer = setTimeout(function () {
                cleanupUnpinnedItem(item);
            }, 350);
        }

        function cleanupUnpinnedItem(item) {
            item.isPinned = false;
            item.isLeaving = false;
            item.isExpanded = false;
            item.currentLeft = 0;
            item.currentWidth = 0;
            item.unpinTimer = null;
            item.$el.removeClass('is-sticky-pinned is-sticky-entering is-sticky-leaving has-scrollbar is-expanded');
            const origStyle = item.$el.data('original-inline-style');
            if (origStyle !== undefined && origStyle !== null && origStyle !== '') {
                item.$el.attr('style', origStyle);
            } else {
                item.$el.removeAttr('style');
            }
            if (item.$placeholder) {
                item.$placeholder.hide();
            }
            if ($stickyControls && currentPinnedItem === item) {
                $stickyControls.removeClass('is-visible is-leaving');
            }
            if (currentPinnedItem === item) {
                currentPinnedItem = null;
            }
        }

        function pinItem(item, topY, navH, activeHeight, enteringFromBelow) {
            const $placeholder = item.$placeholder;
            const $el = item.$el;

            // If item was currently leaving, cancel exit and resume pinned state
            if (item.unpinTimer) {
                clearTimeout(item.unpinTimer);
                item.unpinTimer = null;
            }
            if (item.isLeaving) {
                item.isLeaving = false;
                $el.removeClass('is-sticky-leaving');
                if ($stickyControls) {
                    $stickyControls.removeClass('is-leaving');
                }
            }

            if (!item.isPinned) {
                // Measure natural dimensions in flow before detaching
                const naturalHeight = $el.outerHeight();
                const naturalWidth = $el.outerWidth();
                const elOffset = $el.offset();

                if (naturalWidth < 50 || naturalHeight < 20) {
                    return;
                }

                item.naturalHeight = naturalHeight;
                item.naturalWidth = naturalWidth;
                item.naturalLeft = elOffset.left;

                if (item.isImageWrapper) {
                    const $img = $el.find('img').first();
                    item.imgWidth = $img.outerWidth();
                    item.imgHeight = $img.outerHeight();
                    // Measure exact relative horizontal offset of image within container in flow
                    item.imgRelLeft = Math.max(0, $img.offset().left - elOffset.left);
                }

                $placeholder.css({
                    width: naturalWidth + 'px',
                    height: naturalHeight + 'px',
                    marginTop: $el.css('marginTop'),
                    marginBottom: $el.css('marginBottom'),
                    marginLeft: $el.css('marginLeft'),
                    marginRight: $el.css('marginRight')
                }).show();

                item.isPinned = true;

                if (enteringFromBelow) {
                    $el.addClass('is-sticky-pinned is-sticky-entering');
                    $el.scrollTop(0);
                    // Force synchronous reflow so starting state is registered before transition
                    void $el[0].offsetHeight;
                    requestAnimFrame(function () {
                        $el.removeClass('is-sticky-entering');
                    });
                } else {
                    $el.addClass('is-sticky-pinned');
                    $el.scrollTop(0);
                }
            }

            const pOffset = $placeholder.offset();
            const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft || 0;
            const pLeft = pOffset.left - scrollLeft;
            const pWidth = $placeholder.outerWidth() || item.naturalWidth;

            let targetLeft = pLeft;
            let targetWidth = pWidth;

            if (item.isImageWrapper && item.imgWidth > 0) {
                // Keep image at its EXACT horizontal pixel position from the flow (pLeft + imgRelLeft).
                // Card has 8px padding + 1px border on each side (total 18px).
                // Placing card at (pLeft + imgRelLeft - 9) keeps the image at EXACTLY (pLeft + imgRelLeft).
                // Zero horizontal movement whether image was left-aligned, centered, or indented!
                targetWidth = item.imgWidth + 18;
                targetLeft = pLeft + item.imgRelLeft - 9;
            } else if (pLeft <= 0 && item.naturalLeft > 0) {
                targetLeft = item.naturalLeft - scrollLeft;
            }

            item.currentTop = topY;
            item.currentLeft = targetLeft;
            item.currentWidth = targetWidth;
            item.pinnedHeight = activeHeight;

            // Determine if card needs a scrollbar:
            // Only if activeHeight is genuinely less than natural height (truncated/compressed)
            const isTruncated = activeHeight < (item.naturalHeight - 4);
            item.pinnedIsTruncated = isTruncated;
            $el.toggleClass('has-scrollbar', isTruncated);

            if (!isTruncated) {
                $el.css({
                    position: 'fixed',
                    top: Math.round(topY) + 'px',
                    left: Math.round(targetLeft) + 'px',
                    width: Math.round(targetWidth) + 'px',
                    maxWidth: '100%',
                    height: 'auto',
                    maxHeight: '', // Never clip bottom border/padding when card fits naturally!
                    marginTop: 0,
                    marginBottom: 0
                });
            } else {
                $el.css({
                    position: 'fixed',
                    top: Math.round(topY) + 'px',
                    left: Math.round(targetLeft) + 'px',
                    width: Math.round(targetWidth) + 'px',
                    maxWidth: '100%',
                    height: Math.round(activeHeight) + 'px',
                    maxHeight: '',
                    marginTop: 0,
                    marginBottom: 0
                });
            }

            currentPinnedItem = item;
            updateStickyControlsPosition(item, activeHeight);
        }

        function updateStickyMaterials() {
            if (!isPlayerPlusActive() || !isStickyMaterialsEnabled) {
                if (currentPinnedItem) {
                    unpinItem(currentPinnedItem, true);
                }
                for (let k = 0; k < stickyMaterials.length; k++) {
                    if (stickyMaterials[k].isPinned) {
                        unpinItem(stickyMaterials[k], true);
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

            const scrollY = window.pageYOffset || document.documentElement.scrollTop || 0;
            const pinTop = getStickyPinTop();

            let activeCandidate = null;
            let candidateTop = pinTop;
            let candidateHeight = 0;
            let enteringFromBelow = false;

            for (let i = 0; i < stickyMaterials.length; i++) {
                const item = stickyMaterials[i];
                if (!item.$anchor || !item.$anchor.length) continue;

                const origTop = item.isPinned ? getElementDocTop(item.$placeholder) : getElementDocTop(item.$el);
                const natH = item.isPinned ? item.naturalHeight : (item.$el.outerHeight() || 100);
                const anchorTop = getElementDocTop(item.$anchor);

                // CRITICAL SAFETY GUARDS:
                if (origTop <= (pinTop + 10)) {
                    continue;
                }
                if (anchorTop <= origTop) {
                    continue;
                }

                // If user scrolled back up above the item's natural top position, clear dismissed state
                if (item.isDismissed && scrollY < (origTop - pinTop - 40)) {
                    item.isDismissed = false;
                }

                if (item.isDismissed) {
                    continue;
                }

                const maxPinnedH = getMaxPinnedHeight();
                const targetH = item.isExpanded ? Math.min(natH, Math.round(window.innerHeight * 0.85)) : Math.min(natH, maxPinnedH);

                let currentH = targetH;
                if (!item.isExpanded) {
                    // Dynamic text-following compression:
                    // If card is taller than available viewport (targetH < natH), incoming text pushes
                    // bottom border up until it reaches targetH, then slides underneath.
                    // If card fits on screen, targetH == natH, so currentH stays at natH (no compression, no scrollbars).
                    const distanceToText = (origTop + natH) - scrollY - pinTop;
                    currentH = Math.max(targetH, Math.min(natH, distanceToText));
                }

                const pinStart = origTop - pinTop;
                const releaseEnd = anchorTop - pinTop;

                if (scrollY >= pinStart && scrollY < releaseEnd) {
                    activeCandidate = item;
                    candidateTop = pinTop;
                    candidateHeight = currentH;
                    if (!item.isPinned && scrollY > (pinStart + 40)) {
                        enteringFromBelow = true;
                    }
                }
            }

            for (let j = 0; j < stickyMaterials.length; j++) {
                const it = stickyMaterials[j];
                if (it !== activeCandidate && it.isPinned) {
                    const itOrigTop = it.$placeholder ? getElementDocTop(it.$placeholder) : 0;
                    // If scrolled above original spot, immediately dock into flow; if past anchor, dissolve smoothly
                    const immediateUnpin = scrollY < (itOrigTop - pinTop);
                    unpinItem(it, immediateUnpin);
                }
            }

            if (activeCandidate) {
                pinItem(activeCandidate, candidateTop, pinTop, candidateHeight, enteringFromBelow);
            } else if (currentPinnedItem) {
                unpinItem(currentPinnedItem, false);
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
            const $bar = $(this).closest('.player-plus-bar');
            const $drawer = $bar.find('.player-plus-drawer');
            const isOpen = $drawer.hasClass('is-open');

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
            const $wrapper = $(this).closest('.player-plus-toc-wrapper');
            const isOpen = $wrapper.hasClass('is-open');
            $('.player-plus-toc-wrapper').removeClass('is-open');
            $('.player-plus-drawer').removeClass('is-open');
            $('.player-plus-btn-settings').removeClass('is-active');
            if (!isOpen) {
                $wrapper.addClass('is-open');
                const $curr = $wrapper.find('.player-plus-toc-item.is-current:visible');
                if ($curr.length) {
                    const $list = $wrapper.find('.player-plus-toc-list');
                    const currTop = $curr.position().top;
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
            const depth = parseInt($(this).data('depth'), 10) || 1;
            applyTOCDepth(depth);
        });

        // Chevron click: expand / collapse individual branch in accordion
        $(document).on('click', '.player-plus-toc-chevron', function (e) {
            e.stopPropagation();
            e.preventDefault();
            const $item = $(this).closest('.player-plus-toc-item');
            const chId = $item.data('ch-id');
            const ch = chaptersById[chId];
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
            const $item = $(this);
            const startSec = parseFloat($item.data('start-sec'));
            const headingId = $item.data('heading-id');
            const lineId = $item.data('line-id');

            const a = getAudio();
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

            const $h = $('#' + headingId);
            if ($h.length) {
                isUserInteracting = true;
                clearTimeout(userInteractTimer);
                userInteractTimer = setTimeout(function () {
                    isUserInteracting = false;
                }, 1500);

                const headingTop = $h.offset().top;
                const headingHeight = $h.outerHeight() || 0;
                const targetY = headingTop - (window.innerHeight / 2) + (headingHeight / 2);
                smoothScrollTo(Math.max(0, targetY));
            }
        });
    });
})(jQuery);
