let polly = {};
let audio = undefined;

const NORMAL_CLASS = 'fa-volume-down';
const LOADING_CLASS = 'fa-spinner fa-pulse';
const SPEAKING_CLASS = 'fa-volume-up';
const ERROR_CLASS = 'fa-exclamation-circle red';

const classes = [NORMAL_CLASS, LOADING_CLASS, SPEAKING_CLASS, ERROR_CLASS];

function changeClassTo(icon, c) {
	for (let i in classes) {
		$(icon).removeClass(classes[i])
	}
	$(icon).addClass(c)
}

function pollyListen(icon, key) {
	if (icon.attributes['data-mood'].value === 'indicative' && icon.attributes['data-tense'].value === 'present' && AUDIO_URL !== 'None') {
		polly[key] = AUDIO_URL
	}
	if (polly[key] === undefined) {
		changeClassTo(icon, LOADING_CLASS);
		$.ajax({
				url: CONJ_POLLY_URL,
				type: 'POST',
				async: true,
				datatype: 'json',
				data: {csrfmiddlewaretoken: CSRF_TOKEN, key: key,},
				success: function (r) {
					polly[key] = r[key].url;
					pollyListen(icon, key);
				},
				error: function (r) {
					changeClassTo(icon, ERROR_CLASS)
				}
			}
		)
	} else {
		audio = new Audio([polly[key]]);
		audio.attributes['data-key'] = key;
		audio.addEventListener('play', function () {
			changeClassTo(icon, SPEAKING_CLASS);
		});
		audio.addEventListener('pause', function () {
			changeClassTo(icon, NORMAL_CLASS);
		});
		audio.play();
	}
}

$(document).ready(function () {
	/*setTimeout(function () {
		let blue_arrow = $(".blue_arrow");
		blue_arrow.each(function () {
			this.style.display = "none";
		})
	}, 5000);*/
	$('.play-pause-icon').each(function () {
		$(this).addClass(NORMAL_CLASS);
		this.addEventListener('click', function () {
			if (audio !== undefined && !audio.paused) {
				audio.pause();
				audio.currentTime = 0;
				changeClassTo(this, NORMAL_CLASS);
				if (audio.attributes['data-key'] === this.attributes['data-key'].value) {
					return
				}
			}
			pollyListen(this, this.attributes['data-key'].value)
		})
	});
	$('.nav-pills > li > a').each(function () {
		this.addEventListener('click', function () {
			if(this.attributes['data-target'].value !== '.form0'){
				$('.play-pause-icon').hide()
			}else{
				$('.play-pause-icon').show()
			}
		})
	})
});
