$(document).ready(function () {
	$('.dropdown-menu .notify').click(function (e) {
		if (!$(e.target).is('a')) {
			window.location.href = this.getAttribute('data-url')
		}
	});
	$('.notify-dropdown').one('click', function (e) {
		if (NEW_NOTIFY_PKS.length > 0) {
			$('.notify-badge').hide();
			$.ajax(CHECK_URL, {
				type: 'POST',
				data: {'pks': NEW_NOTIFY_PKS.toString()}
			})
		}
	})
});
