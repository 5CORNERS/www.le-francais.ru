$(document).ready(function () {
	$('.notify-dropdown').on('click', get_drop_content);
	setInterval(update_badge, 60000);
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

function update_badge() {
	$.ajax({
		url: Urls['notifications:get_new_count'](),
		success: function (r) {
			if (r > 0) {
				$('#notify-badge-nav').html(r).show();
			}else{
				$('#notify-badge-nav').html(r).hide();
			}
		}
	});
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

