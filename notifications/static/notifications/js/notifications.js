function updateBadge() {
    $.ajax({
      url: Urls['notifications:get_new_count'](),
      success: function (r) {
        if (r > 0) {
          $('#notify-badge-nav').html(r).show();
        } else {
          $('#notify-badge-nav').html(r).hide();
        }
      }
    });
}


window.setBadgeUpdater = function (timing) {
  let badgeUpdaterInternal = {
    interval: timing,
    stopTime: undefined,
    callback: updateBadge,
    stopped: false,
    runLoop: function () {
      if (badgeUpdaterInternal.stopped) return;
      var result = badgeUpdaterInternal.callback.call(this);
      if (typeof result == 'number') {
        if (result === 0) return;
        badgeUpdaterInternal.interval = result;
      }
      badgeUpdaterInternal.loop()
    },
    stop: function () {
      if (!this.stopped) {
        this.stopped = true;
        window.clearTimeout(this.timeout);
        this.stopTime = Date.now();
      }
    },
    start: function () {
      this.stopped = false;
      if (Date.now() - this.stopTime > this.interval) {
        this.callback.call(this)
      }
      return this.loop();
    },
    loop: function () {
      this.timeout = window.setTimeout(this.runLoop, this.interval);
      return this;
    }
  };
  return badgeUpdaterInternal.start()
};

$(document).ready(function () {
  $('.notify-dropdown').on('click', get_drop_content);
  var badgeUpdater = setBadgeUpdater(60000);
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

