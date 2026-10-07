(function ($) {
    'use strict';

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = $.trim(cookies[i]);
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function escapeHtml(string) {
        if (!string) return '';
        return String(string)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    var BERET_SVG = '<svg class="reaction-beret-icon" viewBox="0 0 467.32 329.23" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Vive le-francais.ru !"><path fill="#ed1c24" d="M566.78,205.68c-28.78,28.37-59.1,56.19-65.55,102.06,16.31,4.46,33,7.44,48.48,13.58,39.3,15.61,80.3,28.86,116.14,50.49,21.53,13,38.76,37.83,50.53,61.09,16.25,32.09-2.29,71.48-37.2,71.75-111.08.85-223.27,33.09-333.22-7.5-18.51-6.83-37-15.17-53.39-26-42.46-28.06-48.95-70.82-19.34-112.53,20.9-29.45,48.15-50.16,84.39-53.34,34-3,68.42-2.71,102.56-1.44,14.63.55,21.44-2.64,24.65-17,4.93-22,11.1-43.8,17.36-65.5C513.24,183.09,529.68,178.45,566.78,205.68Z" transform="translate(-255.01 -188.36)"/></svg>';

    var REACTION_METADATA = {
        heart: { label: 'Сердечко', icon: '<i class="fas fa-heart text-danger"></i>', emoji: '❤️' },
        like: { label: 'Нравится', icon: '👍', emoji: '👍' },
        pray: { label: 'Спасибо', icon: '🙏', emoji: '🙏' },
        idea: { label: 'Идея', icon: '💡', emoji: '💡' },
        pencil: { label: 'Взял на карандаш', icon: '✏️', emoji: '✏️' },
        wow: { label: 'Вау!', icon: '😮', emoji: '😮' },
        fire: { label: 'Огонь', icon: '🔥', emoji: '🔥' },
        beret: {
            label: 'Vive le-francais.ru !',
            icon: BERET_SVG,
            emoji: null
        }
    };

    var hoverTimer = null;
    var closeTimer = null;
    var activeWrapper = null;

    function openPopover($wrapper) {
        clearTimeout(closeTimer);
        $('.reaction-picker-popover.show').not($wrapper.find('.reaction-picker-popover')).removeClass('show');
        $wrapper.find('.reaction-picker-popover').addClass('show');
        activeWrapper = $wrapper;
    }

    function closePopover($wrapper) {
        if (!$wrapper) return;
        $wrapper.find('.reaction-picker-popover').removeClass('show');
        if (activeWrapper && activeWrapper.is($wrapper)) {
            activeWrapper = null;
        }
    }

    // Desktop hover management for reaction picker
    $(document).on('mouseenter', '.reactions-wrapper', function () {
        var $wrapper = $(this);
        clearTimeout(closeTimer);
        hoverTimer = setTimeout(function () {
            openPopover($wrapper);
        }, 180);
    });

    $(document).on('mouseleave', '.reactions-wrapper', function () {
        var $wrapper = $(this);
        clearTimeout(hoverTimer);
        closeTimer = setTimeout(function () {
            closePopover($wrapper);
        }, 320);
    });

    // Mobile / Touch support: long press to show picker
    var touchTimer = null;
    var touchMoved = false;

    $(document).on('touchstart', '.post-react-btn', function (e) {
        touchMoved = false;
        var $btn = $(this);
        var $wrapper = $btn.closest('.reactions-wrapper');
        touchTimer = setTimeout(function () {
            if (!touchMoved) {
                openPopover($wrapper);
            }
        }, 350);
    });

    $(document).on('touchmove', '.post-react-btn', function () {
        touchMoved = true;
        clearTimeout(touchTimer);
    });

    $(document).on('touchend', '.post-react-btn', function () {
        clearTimeout(touchTimer);
    });

    // Close picker popover on click outside
    $(document).on('click', function (e) {
        if (!$(e.target).closest('.reactions-wrapper').length) {
            $('.reaction-picker-popover.show').removeClass('show');
            activeWrapper = null;
        }
    });

    // Execute reaction AJAX request
    function sendReaction(postId, reactionCode, reactUrl, $postRow) {
        var csrftoken = getCookie('csrftoken') || $('input[name=csrfmiddlewaretoken]').val();

        $.ajax({
            url: reactUrl,
            type: 'POST',
            data: {
                reaction: reactionCode,
                csrfmiddlewaretoken: csrftoken
            },
            headers: {
                'X-CSRFToken': csrftoken
            },
            dataType: 'json',
            success: function (data) {
                if (data.status === 'ok') {
                    updatePostReactionsUI($postRow, postId, reactUrl, data);
                } else if (data.status === 'auth_required') {
                    window.location = '/accounts/login/';
                }
            },
            error: function (xhr) {
                if (xhr.status === 401) {
                    window.location = '/accounts/login/';
                }
            }
        });
    }

    // Update DOM after reaction change
    function updatePostReactionsUI($postRow, postId, reactUrl, data) {
        var $btn = $postRow.find('.post-react-btn[data-post-id="' + postId + '"]');
        var $popover = $postRow.find('#reaction-picker-' + postId);
        var $badgesContainer = $postRow.find('#reactions-badges-' + postId);
        var userReaction = data.user_reaction;

        // 1. Update reaction trigger button
        $btn.removeClass(function (index, className) {
            return (className.match(/(^|\s)user-reacted-\S+/g) || []).join(' ');
        });

        if (userReaction) {
            $btn.addClass('active user-reacted-' + userReaction);
            $btn.attr('data-current-reaction', userReaction);
            var meta = REACTION_METADATA[userReaction] || { label: userReaction, icon: '❤️' };
            $btn.find('.post-react-icon').html(meta.icon);
            $btn.find('.post-react-label').text(meta.label);
        } else {
            $btn.removeClass('active');
            $btn.attr('data-current-reaction', '');
            $btn.find('.post-react-icon').html('<i class="far fa-heart"></i>');
            $btn.find('.post-react-label').text('Мне нравится');
        }

        // 2. Update picker selected states
        $popover.find('.reaction-picker-btn').removeClass('is-selected');
        if (userReaction) {
            $popover.find('.reaction-picker-btn[data-reaction="' + userReaction + '"]').addClass('is-selected');
        }

        // 3. Update badges list using Anton's handcrafted tooltip structure
        var badgesHtml = '';
        if (data.summary && data.summary.length > 0) {
            $.each(data.summary, function (idx, item) {
                var isUser = item.is_user ? ' is-user-reacted' : '';
                var iconHtml = '';
                if (item.code === 'beret') {
                    iconHtml = BERET_SVG;
                } else if (item.emoji) {
                    iconHtml = '<span class="reaction-badge-emoji">' + item.emoji + '</span>';
                } else if (item.image) {
                    var imgSrc = item.image.indexOf('/') === 0 ? item.image : '/static/' + item.image;
                    iconHtml = '<img src="' + imgSrc + '" class="reaction-badge-img" alt="' + escapeHtml(item.label) + '">';
                }

                var users = item.users || [];
                var showChevrones = users.length > 5 ? ' show-chevrones' : '';
                var usersHtml = '';
                for (var uIdx = 0; uIdx < users.length; uIdx++) {
                    var u = users[uIdx];
                    var avatarSrc = u.avatar_url || '/static/pybb/img/default_avatar.jpg';
                    usersHtml += '<a href="' + (u.url || '#') + '" class="tooltip-like-entry" title="' + escapeHtml(u.username) + '" data-toggle="tooltip">' +
                        '<div class="avatar">' +
                        '<img src="' + avatarSrc + '" alt="' + escapeHtml(u.username) + '">' +
                        '</div></a>';
                }

                var tooltipHtml = '<div class="tooltip-who-liked' + showChevrones + '">' +
                    '<div class="tooltip-who-liked-container' + showChevrones + '">' +
                    '<span class="fas fa-chevron-left"></span>' +
                    usersHtml +
                    '<span class="fas fa-chevron-right"></span>' +
                    '</div></div>';

                badgesHtml += '<div class="reaction-badge' + isUser + '" role="button" tabindex="0" ' +
                    'data-post-id="' + postId + '" data-reaction="' + item.code + '" data-react-url="' + reactUrl + '" ' +
                    'aria-label="' + escapeHtml(item.label) + '">' +
                    iconHtml +
                    '<span class="reaction-badge-count">' + item.count + '</span>' +
                    tooltipHtml +
                    '</div>';
            });
        }
        $badgesContainer.html(badgesHtml);

        // Initialize tooltips on avatars
        $badgesContainer.find('[data-toggle="tooltip"]').tooltip();

        // 4. Update schema user interaction count
        $postRow.find('[itemprop="userInteractionCount"]').attr('content', data.total_count);

        // Animate button bounce
        $btn.addClass('animated pulse').one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function () {
            $(this).removeClass('animated pulse');
        });
    }

    // Click on reaction trigger button
    $(document).on('click', '.post-react-btn', function (e) {
        e.preventDefault();
        var $btn = $(this);
        var loginUrl = $btn.data('login-url');
        if (loginUrl) {
            window.location = loginUrl;
            return;
        }

        var postId = $btn.data('post-id');
        var reactUrl = $btn.data('react-url');
        var currentReaction = $btn.attr('data-current-reaction') || '';
        var $postRow = $btn.closest('.post-card');

        // If user already reacted, clicking the button toggles that reaction off.
        // If not reacted, default to 'heart'.
        var reactionToSend = currentReaction ? currentReaction : 'heart';
        closePopover($btn.closest('.reactions-wrapper'));
        sendReaction(postId, reactionToSend, reactUrl, $postRow);
    });

    // Click on emoji in reaction picker popover
    $(document).on('click', '.reaction-picker-btn', function (e) {
        e.preventDefault();
        e.stopPropagation();
        var $pickerBtn = $(this);
        var $wrapper = $pickerBtn.closest('.reactions-wrapper');
        var $reactBtn = $wrapper.find('.post-react-btn');
        var loginUrl = $reactBtn.data('login-url');
        if (loginUrl) {
            window.location = loginUrl;
            return;
        }

        var postId = $reactBtn.data('post-id');
        var reactUrl = $reactBtn.data('react-url');
        var reactionCode = $pickerBtn.data('reaction');
        var $postRow = $wrapper.closest('.post-card');

        closePopover($wrapper);
        sendReaction(postId, reactionCode, reactUrl, $postRow);
    });

    // Click on an existing reaction badge
    $(document).on('click', '.reaction-badge', function (e) {
        if ($(e.target).closest('.tooltip-who-liked').length) {
            return;
        }
        e.preventDefault();
        var $badge = $(this);
        var postId = $badge.data('post-id');
        var reactionCode = $badge.data('reaction');
        var reactUrl = $badge.data('react-url');
        var $postRow = $badge.closest('.post-card');
        var $reactBtn = $postRow.find('.post-react-btn');

        var loginUrl = $reactBtn.data('login-url');
        if (loginUrl) {
            window.location = loginUrl;
            return;
        }

        sendReaction(postId, reactionCode, reactUrl, $postRow);
    });

    // Keyboard support for reaction badges
    $(document).on('keydown', '.reaction-badge', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
            if (!$(e.target).closest('.tooltip-who-liked').length) {
                e.preventDefault();
                $(this).trigger('click');
            }
        }
    });

    // Scrolling chevrons inside Anton's who-liked tooltip
    $(document).on('click', '.tooltip-who-liked-container .fa-chevron-right, .tooltip-who-liked-container [class*="fa-chevron-right"]', function (e) {
        e.stopPropagation();
        e.preventDefault();
        var $container = $(this).closest('.tooltip-who-liked-container');
        $container.animate({ scrollLeft: $container.scrollLeft() + 100 }, 150);
    });

    $(document).on('click', '.tooltip-who-liked-container .fa-chevron-left, .tooltip-who-liked-container [class*="fa-chevron-left"]', function (e) {
        e.stopPropagation();
        e.preventDefault();
        var $container = $(this).closest('.tooltip-who-liked-container');
        $container.animate({ scrollLeft: $container.scrollLeft() - 100 }, 150);
    });

    $(document).on('click', '.tooltip-like-entry', function (e) {
        e.stopPropagation();
    });

    // Hover timers for reaction badges to show Anton's who-liked tooltip
    var badgeShowTimer = null;

    function hideAllBadgeTooltips() {
        clearTimeout(badgeShowTimer);
        $('.reaction-badge.show-tooltip').removeClass('show-tooltip');
    }

    $(document).on('mouseenter', '.reaction-badge', function () {
        var $badge = $(this);
        // Immediately close any other badge's tooltip when moving to a neighbor badge
        $('.reaction-badge').not($badge).removeClass('show-tooltip');
        clearTimeout(badgeShowTimer);

        var $tooltip = $badge.find('.tooltip-who-liked');
        if (!$tooltip.length || !$tooltip.find('.tooltip-like-entry').length) {
            return;
        }

        badgeShowTimer = setTimeout(function () {
            // Ensure no other badges are shown
            $('.reaction-badge').not($badge).removeClass('show-tooltip');
            $badge.addClass('show-tooltip');
        }, 150);
    });

    $(document).on('mouseleave', '.reaction-badge', function () {
        var $badge = $(this);
        clearTimeout(badgeShowTimer);
        $badge.removeClass('show-tooltip');
    });

    // Close tooltips on click outside or Esc
    $(document).on('click', function (e) {
        if (!$(e.target).closest('.reaction-badge').length) {
            hideAllBadgeTooltips();
        }
    });

    $(document).on('keydown', function (e) {
        if (e.key === 'Escape' || e.keyCode === 27) {
            hideAllBadgeTooltips();
        }
    });

})(jQuery);
