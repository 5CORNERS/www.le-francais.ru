function reloadPage(lesson_number, tabID=0) {
			$.ajax({
				type: 'GET',
				url: Urls['api:get_lesson_content'](lesson_number, 1, tabID),
				beforeSend: function() {
					if (tabID) {
						$(`#lazy-${tabID}`).html('Подождите, идёт загрузка...')
					}
				},
				success: function (r) {
					if (tabID) {
						$(`#lazy-${tabID}`).hide()
					}
					r.tabs.forEach(function (tab, i) {
						if (tab.value != null) {
						  let navLink = $(`a.nav-link[href="#${tab.href}"]`);
							navLink.html(tab.title);
							if (tab.transition){
							  $(document).on('hidden.bs.modal', function () {
							    navLink.parent().fadeIn(500);
								  navLink.css({"background-color":"#90ee90", "color":"#003e73", "transition":"background-color 0.5s ease"});
							    setTimeout(function(){
							    navLink.css({"background-color":"#ffffff", "color":"", "transition":"background-color 10s ease"});
							  },500)
                })
							}
							$(`div.tab-pane#${tab.href}`).html(tab.value);
						}
					});
					$('[data-toggle="popover"]').popover()
				}
			});
		}


$(document).ready(function () {
    $('a#tab-flash-cards').one('show.bs.tab', function () {
        reloadPage(LESSON_NUMBER, 'flash-cards');
    });
});

