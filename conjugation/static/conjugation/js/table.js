let polly = {};
let audio = undefined;

let ua = window.navigator.userAgent;
let iOS = !!ua.match(/iPad/i) || !!ua.match(/iPhone/i);
let is_webkit = !!ua.match(/WebKit/i);
let iOSSafari = iOS && is_webkit && !ua.match(/CriOS/i);

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
	if (!IS_REFLEXIVE && icon.attributes['data-mood'].value === 'indicative' && icon.attributes['data-tense'].value === 'present' && AUDIO_URL !== 'None') {
		polly[key] = AUDIO_URL
	}
	if (polly[key] === undefined) {
		changeClassTo(icon, LOADING_CLASS);
		$.ajax({
				url: CONJ_POLLY_URL,
				type: 'POST',
				async: !iOSSafari,
				datatype: 'json',
				data: {csrfmiddlewaretoken: CSRF_TOKEN, key: key,},
				success: function (r) {
					polly[key] = r[key].url;
					pollyListen(icon, key);
				},
				error: function (r) {
					changeClassTo(icon, ERROR_CLASS);
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

function see_less() {
	$.each($(".in_short_list"), function (i, v) {
		v.style.display = "none";
	});
	$("#more_tab").removeClass("active");
	$("#less_tab").addClass("active");
	$("#more_tab>a").html('Полная').removeClass("active");
	$("#less_tab>a").html('Сокращённая версия').addClass("active");
	window.localStorage.setItem('long_list', 'false');
}

function see_more() {
	$.each($(".in_short_list"), function (i, v) {
		v.style.display = "block";
	});
	$("#more_tab").addClass("active");
	$("#more_tab>a").html('Полная версия').addClass("active");
	$("#less_tab").removeClass("active");
	$("#less_tab>a").html('Сокращённая').removeClass("active");
	window.localStorage.setItem('long_list', 'true');
}

$(document).ready(function () {
	if (window.localStorage.getItem('long_list') === 'true') {
		see_more()
	}

	// TODO: change form on hashchange
	let url = location.href.replace(/\/$/, "");
	if(location.hash){
		const hash = url.split('#');
		$(`.verb-form-pill a[data-target=".${hash[1]}"]`).tab('show');
	}

	$('.verb-form-pill a[data-toggle="pill"]').on("click", function () {
		let newUrl;
		const hash = $(this).attr('data-target').replace(/\./, '#');
		if (hash === '#form0') {
			newUrl = url.split('#')[0]
		}else{
			newUrl = url.split('#')[0] + hash
		}
		history.replaceState(null, null, newUrl)
	});

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

	// Verb Switches script
	let $pronounCheckbox = $('#pronounCheckbox');
	let $pronounInput = $pronounCheckbox.find('input');
	let $voice_range = $(`#${VOICE_RANGE_ID}`);
	let last_val = $voice_range.val();
	let $switchesForm = $('#switchesForm')
	if (CAN_BE_PRONOUN && $voice_range.val() === '2') {
		$pronounCheckbox.show();
		if (MUST_BE_PRONOUN) {
			$pronounInput.prop('disabled', true)
		}
	}
	$voice_range.change(ev => {
		if ($voice_range.val() === '1' && !CAN_BE_PASSIVE && CAN_BE_REFLEXIVE) {
			if (last_val === '0') {
				$voice_range.val('2')
			} else {
				$voice_range.val('0')
			}
		} else if ($voice_range.val() === '2' && !CAN_BE_REFLEXIVE && CAN_BE_PASSIVE) {
			if (last_val === '3') {
				$voice_range.val('1')
			} else {
				$voice_range.val('3')
			}
		} else if (!CAN_BE_PASSIVE && !CAN_BE_REFLEXIVE && ($voice_range.val() === '2' || $voice_range.val() === '1')) {
			$voice_range.val('0')
		}
		if (CAN_BE_PRONOUN && $voice_range.val() === '2') {
			if (MUST_BE_PRONOUN) {
				$pronounInput.prop('checked', true)
				$pronounInput.prop('disabled', true)
			}
			$pronounCheckbox.show()
		} else {
			if (MUST_BE_PRONOUN) {
				$pronounInput.prop('checked', false)
				$pronounInput.prop('disabled', false)
			}
			$pronounCheckbox.hide()
		}
		last_val = $voice_range.val()
	})
	$switchesForm.submit(ev => {
		if ($pronounInput.prop('disabled')) {
			$pronounInput.prop('disabled', false)
		}
	})
});
