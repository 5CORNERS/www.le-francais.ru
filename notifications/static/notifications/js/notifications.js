var notificationsUpdateDatetime = 0;

function ifHasNewNotification(func) {
    $.ajax(Urls['notifications:has_new_notifications'](), {
        type: 'POST',
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        data: JSON.stringify({
            'datetime': notificationsUpdateDatetime
        }),
        success: function (r) {
            if (r.hasNewNotifications) {
                func.call()
            } else if (!r.hasNewNotifications) {
                $('#notify-badge-nav').html('0').hide()
            }
        }
    })
}


function updateBadge() {
    $.ajax({
        url: Urls['notifications:get_new_count'](),
        success: function (r) {
            if (r > 0) {
                $('#notify-badge-nav').html(r).show();
                notificationsUpdateDatetime = Date.now()
            } else {
                $('#notify-badge-nav').html(r).hide();
            }
        }
    });
}


$(document).ready(function () {
    $('.notify-dropdown .nav-link').on('click', get_drop_content);
    var badgeUpdater = setIntervalRun(60000, ifHasNewNotification, updateBadge);
    var notificationsUpdateDatetime = 0;
    document.addEventListener('visibilitychange', function () {
        if (document.visibilityState === 'visible') {
            badgeUpdater.start();
        } else {
            badgeUpdater.stop();
        }
    })
});


function check_notifications(pks) {
    if (pks.length > 0) {
        $('#notify-badge-nav').hide().html('0');
        $.ajax(Urls['notifications:check_list'](), {
            type: 'POST',
            data: {'pks': pks.toString()}
        })
    }
}


function get_drop_content() {
    $('.notify-drop > .drop-content').replaceWith($("<div class=\"drop-content\"><img src='/static/images/loading_icon.gif'></div>"));
    $.ajax(Urls['notifications:get_drop_content_html'](), {
        data: {
            path: window.location.pathname,
        },
        success: function (r) {
            $('.notify-drop > .drop-content').replaceWith(r);
            $('.dropdown-menu .notify').click(function (e) {
                if (!$(e.target).is('a')) {
                    window.location.href = this.getAttribute('data-url')
                }
            });
            var new_notifications_pks = [];
            $("*[data-check_datetime='None']").each(function () {
                new_notifications_pks.push(this.dataset.pk)
            });
            check_notifications(new_notifications_pks)
        }
    })
}

