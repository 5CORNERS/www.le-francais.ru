(function ($) {
    $(document).ready(function () {
        const $naturalContainer = $('#lessonTabsContainer');
        const $naturalTabs = $naturalContainer.find('.lesson-tabs');
        const $topMenu = $('#topMenu');

        if (!$naturalContainer.length || !$naturalTabs.length) return;

        // Constants
        const AUTO_HIDE_DELAY_MS = 10000;
        const AUTO_TUCK_DELAY_MS = 350;
        const REVEAL_LOCK_MS = 1000;
        const PULL_TAB_LOCK_MS = 600;
        const DISSOLVE_DISTANCE = 60;
        const SCROLL_HIDE_THRESHOLD_DESKTOP = 50;
        const SCROLL_HIDE_THRESHOLD_MOBILE = 25;
        const SCROLL_REVEAL_THRESHOLD = 15;

        function getNavbarHeight() {
            if ($topMenu.length && $topMenu.is(':visible')) {
                return $topMenu.outerHeight();
            }
            return 48;
        }

        function getTabsScrollTarget() {
            const originalTop = $naturalContainer.offset().top;
            const navH = getNavbarHeight();
            return Math.max(0, originalTop - navH);
        }

        function isMobileMode() {
            return window.innerWidth < 768;
        }

        // 1. Build floating dock clone
        const $floatingWrapper = $(`
            <div class="lesson-tabs-floating-wrapper is-hidden" id="lessonTabsFloatingWrapper" style="opacity: 0; pointer-events: none;">
                <div class="lesson-tabs-floating-inner">
                    <ul class="nav lesson-tabs-floating-list" role="tablist"></ul>
                </div>
                <button type="button" class="lesson-tabs-pull-tab" id="lessonTabsPullTab" title="Показать вкладки" aria-label="Показать вкладки">
                    <span class="pull-tab-pill">
                        <svg viewBox="0 0 24 24" width="13" height="13" stroke="currentColor" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="6 9 12 15 18 9"></polyline>
                        </svg>
                    </span>
                </button>
            </div>
        `);

        const $floatingList = $floatingWrapper.find('.lesson-tabs-floating-list');

        // Clone tabs: strip all IDs to avoid duplicate IDs on page; track tab index
        $naturalTabs.children('li').each(function (index) {
            const $clonedLi = $(this).clone();
            $clonedLi.removeAttr('id');
            $clonedLi.find('[id]').removeAttr('id');
            $clonedLi.attr('data-tab-index', index);
            $floatingList.append($clonedLi);
        });

        $('body').append($floatingWrapper);

        // Floating scroll-to-top button in the bottom-right corner
        const $scrollTopBtn = $(`
            <button type="button" class="lesson-scroll-top-btn is-hidden" id="lessonScrollTopBtn" title="Наверх" aria-label="Наверх">
                <svg viewBox="0 0 24 24" width="22" height="22" stroke="currentColor" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="18 15 12 9 6 15"></polyline>
                </svg>
            </button>
        `);
        $('body').append($scrollTopBtn);

        const $pullTab = $floatingWrapper.find('#lessonTabsPullTab');

        // 2. Geometry & Horizontal Alignment (Cached to prevent layout thrashing on vertical scroll)
        let cachedTabsLeft = 0;
        let cachedTabsWidth = 0;
        let lastScrollLeft = -1;

        function syncTabWidths() {
            if (!$naturalTabs.length) return;
            $naturalTabs.children('li').each(function (index) {
                const naturalLiWidth = $(this).outerWidth();
                if (naturalLiWidth > 0) {
                    $floatingList.children('li[data-tab-index="' + index + '"]').css({
                        'width': naturalLiWidth + 'px'
                    });
                }
            });
        }

        function updateFloatingDimensions() {
            if (!$naturalTabs.length) return;
            const tabsOffset = $naturalTabs.offset();
            cachedTabsLeft = tabsOffset.left;
            cachedTabsWidth = $naturalTabs.outerWidth();
            syncTabWidths();
            updateFloatingPosition();
        }

        function updateFloatingPosition() {
            const currentScrollLeft = window.pageXOffset || document.documentElement.scrollLeft || 0;
            $floatingWrapper.css({
                left: (cachedTabsLeft - currentScrollLeft - 1) + 'px',
                width: (cachedTabsWidth + 2) + 'px'
            });
        }
        updateFloatingDimensions();
        window.addEventListener('load', updateFloatingDimensions);
        if (document.fonts && document.fonts.ready) {
            document.fonts.ready.then(updateFloatingDimensions);
        }

        // 3. Independent Scroll Positions per Tab
        const tabScrollPositions = {};
        let currentTabHref = $naturalTabs.find('.nav-link.active').attr('href') || '#body';
        tabScrollPositions[currentTabHref] = window.scrollY;

        // 4. Scroll Tracking, Detach & Dissolve Transition, and Inactivity Timer
        let lastScrollY = window.scrollY;
        let isHidden = true;
        let downScrollAccumulator = 0;
        let upScrollAccumulator = 0;
        let canHideAfter = 0;
        let isMouseOver = false;
        let wasSticky = false;
        let autoHideTimer = null;

        function clearAutoHideTimer() {
            if (autoHideTimer) {
                clearTimeout(autoHideTimer);
                autoHideTimer = null;
            }
        }

        function startAutoHideTimer(delay) {
            delay = delay || AUTO_HIDE_DELAY_MS;
            clearAutoHideTimer();
            autoHideTimer = setTimeout(function () {
                if (!isMouseOver && !isHidden) {
                    isHidden = true;
                    $floatingWrapper.addClass('is-hidden');
                }
            }, delay);
        }

        // Only track mouse hover on devices that have a real fine pointer (mouse), NOT touchscreens
        if (window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
            $floatingWrapper.on('mouseenter', function () {
                isMouseOver = true;
                clearAutoHideTimer();
            });
            $floatingWrapper.on('mouseleave', function () {
                isMouseOver = false;
                if (!isHidden) {
                    startAutoHideTimer(AUTO_HIDE_DELAY_MS);
                }
            });
        }

        // On touch devices, touching the floating dock resets the inactivity timer
        $floatingWrapper.on('touchstart', function () {
            if (!isHidden) {
                startAutoHideTimer(AUTO_HIDE_DELAY_MS);
            }
        });

        function handleScroll() {
            const currentScrollY = Math.max(0, window.scrollY);
            const navH = getNavbarHeight();
            const stickyTrigger = getTabsScrollTarget();
            const delta = currentScrollY - lastScrollY;
            const isSticky = currentScrollY > stickyTrigger;

            // Toggle floating scroll-to-top button visibility
            $scrollTopBtn.toggleClass('is-hidden', !isSticky);

            // Continually save current tab's scroll position
            if (currentTabHref) {
                tabScrollPositions[currentTabHref] = currentScrollY;
            }

            // Case A: Near or above natural tabs (DETACH & DISSOLVE EFFECT)
            if (!isSticky) {
                wasSticky = false;
                clearAutoHideTimer();
                const distanceBelowMenu = stickyTrigger - currentScrollY; // >= 0

                if (distanceBelowMenu <= DISSOLVE_DISTANCE) {
                    // Floating bar detaches from menu, glides down exactly over natural tabs, and dissolves
                    const currentTop = navH + distanceBelowMenu;
                    const currentOpacity = Math.max(0, 1 - (distanceBelowMenu / DISSOLVE_DISTANCE));

                    $floatingWrapper.css({
                        top: currentTop + 'px',
                        opacity: currentOpacity,
                        pointerEvents: currentOpacity > 0.2 ? 'auto' : 'none'
                    }).removeClass('is-hidden');
                    isHidden = false;
                } else {
                    // Scrolled completely into natural view: fully dissolve floating bar
                    $floatingWrapper.css({
                        opacity: 0,
                        pointerEvents: 'none',
                        top: navH + 'px'
                    }).addClass('is-hidden');
                    isHidden = true;
                }

                lastScrollY = currentScrollY;
                downScrollAccumulator = 0;
                upScrollAccumulator = 0;
                return;
            }

            // Case B: Deep in content past stickyTrigger (STICKY FLOATING MODE)
            $floatingWrapper.css({
                top: navH + 'px',
                opacity: 1,
                pointerEvents: 'auto'
            });

            // If just crossed into sticky mode from above, guarantee initial visibility lock
            if (!wasSticky) {
                wasSticky = true;
                isHidden = false;
                $floatingWrapper.removeClass('is-hidden');
                canHideAfter = Date.now() + REVEAL_LOCK_MS;
                if (!isMobileMode()) {
                    startAutoHideTimer(AUTO_HIDE_DELAY_MS);
                }
            }

            if (delta > 0) {
                // Scrolling DOWN
                upScrollAccumulator = 0;

                // Only block hiding during initial reveal lock or desktop mouse hover
                if (Date.now() < canHideAfter || isMouseOver) {
                    downScrollAccumulator = 0;
                } else {
                    downScrollAccumulator += delta;
                    const hideThreshold = isMobileMode() ? SCROLL_HIDE_THRESHOLD_MOBILE : SCROLL_HIDE_THRESHOLD_DESKTOP;
                    if (downScrollAccumulator >= hideThreshold && !isHidden) {
                        isHidden = true;
                        $floatingWrapper.addClass('is-hidden');
                        clearAutoHideTimer();
                    }
                }
            } else if (delta < 0) {
                // Scrolling UP:
                downScrollAccumulator = 0;

                // On mobile, DO NOT auto-reveal on scroll up (tabs take 5 rows and block the screen).
                // Auto-reveal on scroll up is strictly for desktop:
                if (!isMobileMode()) {
                    upScrollAccumulator += Math.abs(delta);
                    if (isHidden && upScrollAccumulator >= SCROLL_REVEAL_THRESHOLD) {
                        isHidden = false;
                        $floatingWrapper.removeClass('is-hidden');
                        startAutoHideTimer(AUTO_HIDE_DELAY_MS);
                    } else if (!isHidden) {
                        startAutoHideTimer(AUTO_HIDE_DELAY_MS);
                    }
                } else {
                    if (!isHidden) {
                        startAutoHideTimer(AUTO_HIDE_DELAY_MS);
                    }
                }
            }

            lastScrollY = currentScrollY;
        }

        // Throttle scroll events via requestAnimationFrame
        let scrollTicking = false;
        window.addEventListener('scroll', function () {
            if (!scrollTicking) {
                window.requestAnimationFrame(function () {
                    const currentScrollLeft = window.pageXOffset || document.documentElement.scrollLeft || 0;
                    if (currentScrollLeft !== lastScrollLeft) {
                        updateFloatingPosition();
                        lastScrollLeft = currentScrollLeft;
                    }
                    handleScroll();
                    scrollTicking = false;
                });
                scrollTicking = true;
            }
        }, { passive: true });

        window.addEventListener('resize', updateFloatingDimensions);

        // 5. Tab Click Handlers
        // Click on floating tab: forward directly to original tab link so lessons.js paywall or Bootstrap activates!
        $floatingWrapper.on('click', '.nav-link', function (e) {
            e.preventDefault();
            e.stopPropagation();
            $('html, body').stop(true, true);

            const tabIndex = $(this).closest('li').attr('data-tab-index');
            const $origLi = $naturalTabs.children('li').eq(tabIndex);
            const $origLink = $origLi.find('.nav-link, a').first();

            if (isMobileMode()) {
                clearAutoHideTimer();
                setTimeout(function () {
                    isHidden = true;
                    $floatingWrapper.addClass('is-hidden');
                }, AUTO_TUCK_DELAY_MS);
            } else {
                startAutoHideTimer(AUTO_HIDE_DELAY_MS);
            }

            // Forward click to original tab link
            $origLink.trigger('click');
        });

        // Click on natural tab
        $naturalTabs.on('click', 'a[data-toggle="tab"]', function (e) {
            e.preventDefault();
            e.stopPropagation();
            $('html, body').stop(true, true);
            $(this).tab('show');
        });

        // When tab is hidden, record departing tab's position
        $(document).on('hide.bs.tab', '.lesson-tabs a[data-toggle="tab"]', function (e) {
            const leavingHref = $(e.target).attr('href');
            if (leavingHref) {
                tabScrollPositions[leavingHref] = window.scrollY;
            }
        });

        // When tab is shown, synchronize active states and restore position
        $(document).on('shown.bs.tab', '.lesson-tabs a[data-toggle="tab"]', function (e) {
            $('html, body').stop(true, true);
            const enteringHref = $(e.target).attr('href');
            currentTabHref = enteringHref;
            const naturalTarget = getTabsScrollTarget();

            // Synchronize active class in floating bar
            $floatingWrapper.find('.nav-link').removeClass('active');
            $floatingWrapper.find('a[href="' + enteringHref + '"]').addClass('active');

            if (tabScrollPositions[enteringHref] !== undefined) {
                window.scrollTo(0, tabScrollPositions[enteringHref]);
            } else {
                if (window.scrollY > naturalTarget) {
                    window.scrollTo(0, naturalTarget);
                    tabScrollPositions[enteringHref] = naturalTarget;
                } else {
                    tabScrollPositions[enteringHref] = window.scrollY;
                }
            }

            lastScrollY = window.scrollY;
            downScrollAccumulator = 0;
            upScrollAccumulator = 0;
            canHideAfter = Date.now() + REVEAL_LOCK_MS;

            // Make sure floating bar is revealed and geometry updated
            isHidden = false;
            $floatingWrapper.removeClass('is-hidden');
            updateFloatingDimensions();
            if (!isMobileMode()) {
                startAutoHideTimer(AUTO_HIDE_DELAY_MS);
            }
        });

        // 6. Scroll-to-Top (Haut) Button Click
        $scrollTopBtn.on('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            clearAutoHideTimer();
            $('html, body').stop(true, true);
            const targetY = getTabsScrollTarget();
            $('html, body').animate({ scrollTop: targetY }, 450);
            canHideAfter = Date.now() + REVEAL_LOCK_MS;
        });

        // 7. Pull-Tab (язычок) Click
        $pullTab.on('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            isHidden = false;
            $floatingWrapper.removeClass('is-hidden');
            canHideAfter = Date.now() + PULL_TAB_LOCK_MS;
            downScrollAccumulator = 0;
            upScrollAccumulator = 0;
            startAutoHideTimer(AUTO_HIDE_DELAY_MS);
        });
    });
})(jQuery);
