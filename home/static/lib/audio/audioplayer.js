/*
	AUTHOR: Osvaldas Valutis, www.osvaldas.info
*/

;$(document).ready(function () {
	$('audio').audioPlayer();
	dispatchEvent(new Event('audioplayerReady'));
});


(function ($, window, document, undefined) {
	var isTouch = 'ontouchstart' in window,
		eStart = isTouch ? 'touchstart' : 'mousedown',
		eMove = isTouch ? 'touchmove' : 'mousemove',
		eEnd = isTouch ? 'touchend' : 'mouseup',
		eCancel = isTouch ? 'touchcancel' : 'mouseup',
		secondsToTime = function (secs) {
			var hours = Math.floor(secs / 3600), minutes = Math.floor(secs % 3600 / 60),
				seconds = Math.ceil(secs % 3600 % 60),
				hours_str, minutes_str, seconds_str;

			if (hours == 0) {
				hours_str = '';
			} else {
				hours_str = (hours.toString().length < 2) ? ('0' + hours) : hours;
			}

			minutes_str = (minutes.toString().length < 2) ? ('0' + minutes) : minutes;
			seconds_str = (seconds.toString().length < 2) ? ('0' + seconds) : seconds;

			return hours_str + ((hours == 0) ? '' : ':') + minutes_str + ':' + seconds_str;
		},
		canPlayType = function (file) {
			var audioElement = document.createElement('audio');
			return true;
			// return !!(audioElement.canPlayType &&
			// 	audioElement.canPlayType('audio/' + file.split('.')
			// 		.pop()
			// 		.toLowerCase() + ';')
			// 		.replace(/no/, '')
			// );
		};

	$.fn.audioPlayer = function (params) {
		var params = $.extend({
				classPrefix: 'audioplayer',
				strPlay: 'Play',
				strPause: 'Pause',
				strVolume: 'Volume'
			}, params),
			cssClass = {},
			cssClassSub =
				{
					playPause: 'playpause',
					playing: 'playing',
					time: 'time',
					timeCurrent: 'time-current',
					timeDuration: 'time-duration',
					bar: 'bar',
					barLoaded: 'bar-loaded',
					barPlayed: 'bar-played',
					volume: 'volume',
					volumeButton: 'volume-button',
					volumeAdjust: 'volume-adjust',
					noVolume: 'novolume',
					mute: 'mute',
					mini: 'mini',
					download: 'download',
					downloadButton: 'download-button',
					tenSecondsBack: 'ten-seconds-back',
					tenSecondsBackMask: 'ten-seconds-back-mask',
				},
		tenSecondsBackMaskSvg = $(`<svg class="${cssClassSub.tenSecondsBackMask}">
      <defs>
        <pattern id="pattern-stripe" width="3" height="2" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
          <rect width="1" height="3" transform="translate(0,0)" fill="white" data-darkreader-inline-fill="" style="--darkreader-inline-fill:#bdbdbd;"></rect>
        </pattern>
        <mask id="mask-stripe">
          <rect x="0" y="0" width="100%" height="100%" fill="url(#pattern-stripe)"></rect>
        </mask>      
      </defs>

      <!-- bar chart -->
      <rect class="hbar thing-2" x="0" y="0" width="32" height="32" style="
    mask: url(#mask-stripe);
    fill: #292b2c;
"></rect>
    
</svg>`);

		for (var subName in cssClassSub) {
			cssClass[subName] = params.classPrefix + '-' + cssClassSub[subName];
		}

		this.each(function () {
			if ($(this).prop('tagName').toLowerCase() != 'audio')
				return false;

			var $this = $(this),
				audioFile = $this.attr('src'),
				isAutoPlay = $this.get(0).getAttribute('autoplay'),
				isLoop = $this.get(0).getAttribute('loop'),
				isSupport = false,
				setTime = $this.get(0).getAttribute('set-time'),
				isStrict = $this.data('strict') === true;

			isAutoPlay = ((isAutoPlay === '') || (isAutoPlay === 'autoplay'))
			isLoop = ((isLoop === '') || (isLoop === 'loop'))

			if (typeof audioFile === 'undefined') {
				$this.find('source').each(function () {
					audioFile = $(this).attr('src');
					if ((typeof audioFile !== 'undefined') && canPlayType(audioFile)) {
						isSupport = true;

						return false;
					}
				});
			}
			else if (canPlayType(audioFile)) {
				isSupport = true;
			}

			var thePlayer = $('<div class="' + params.classPrefix + '">'
				+ ((isSupport) ?
						$('<div>').append($this.eq(0).clone()).html()
						: '<embed src="' + audioFile + '" width="0" height="0" volume="100" autostart="' + isAutoPlay.toString() + '" loop="' + isLoop.toString() + '" />'
				)
				+ '<div class="' + cssClass.playPause + '" title="' + params.strPlay + '"><a href="#">' + params.strPlay + '</a></div></div>'
				),
				theAudio = (isSupport) ? thePlayer.find('audio') : thePlayer.find('embed'),
				theAudio = theAudio.get(0);

			var lesson_number = $(theAudio).attr('number'), wasPlaying;

			if ((typeof lesson_number !== typeof undefined) && (lesson_number !== false)) {
				var $menuPlayer = thePlayer.clone();
			}

			if (isSupport) {
				thePlayer.find('audio').css({'width': 0, 'height': 0, 'visibility': 'hidden'});
				thePlayer.append('<div class="' + cssClass.time + ' ' + cssClass.timeCurrent + '"></div><div class="' + cssClass.bar + '"><div class="' + cssClass.barLoaded + '"></div><div class="' + cssClass.barPlayed + '"></div></div><div class="' + cssClass.time + ' ' + cssClass.timeDuration + '"></div><div class="' + cssClass.volume + '"><div class="' + cssClass.volumeButton + '" title="' + params.strVolume + '"><a href="#">' + params.strVolume + '</a></div><div class="' + cssClass.volumeAdjust + '"><div><div></div></div></div></div>');

				var downloadable = $(theAudio).data('downloadable');

				if (downloadable === true) {
					var source = $(theAudio).find('source').attr('src');
					if (!isStrict) {
						thePlayer.append('<div class="' + cssClass.download + '"><a download="true" href="' + source + '&download=true' + '" class="' + cssClass.downloadButton + ' fa fa-download"></a></div><div class="audioplayer-space"></div>');
					} else {
						thePlayer.append('<div class="' + cssClass.download + '"><a download="true" class="' + cssClass.downloadButton + ' fa fa-download"></a></div>');
					}
					$(theAudio).attr('id', 'lesson-audio');
					$(theAudio).attr('number', lesson_number);
				}
				window.dispatchEvent(new CustomEvent('downloadButtonReady'));

				var theBar = thePlayer.find('.' + cssClass.bar),
					barPlayed = thePlayer.find('.' + cssClass.barPlayed),
					barLoaded = thePlayer.find('.' + cssClass.barLoaded),
					timeCurrent = thePlayer.find('.' + cssClass.timeCurrent),
					timeDuration = thePlayer.find('.' + cssClass.timeDuration),
					volumeButton = thePlayer.find('.' + cssClass.volumeButton),
					volumeAdjuster = thePlayer.find('.' + cssClass.volumeAdjust + ' > div'),
					downloadButton = thePlayer.find('.' + cssClass.downloadButton),
					volumeDefault = 0,
					adjustCurrentTime = function (e) {
						theRealEvent = isTouch ? e.originalEvent.touches[0] : e;
						theAudio.currentTime = Math.round((theAudio.duration * (theRealEvent.pageX - theBar.offset().left)) / theBar.width());
					},
					adjustVolume = function (e) {
						theRealEvent = isTouch ? e.originalEvent.touches[0] : e;
						theAudio.volume = Math.abs((theRealEvent.pageY - (volumeAdjuster.offset().top + volumeAdjuster.height())) / volumeAdjuster.height());
					};

				var volumeTestDefault = theAudio.volume, volumeTestValue = theAudio.volume = 0.111;

				if (Math.round(theAudio.volume * 1000) / 1000 == volumeTestValue) {
					theAudio.volume = volumeTestDefault;
				} else {
					thePlayer.addClass(cssClass.noVolume);
				}

				timeDuration.html('&hellip;');
				timeCurrent.text(secondsToTime(0));

				theAudio.addEventListener('loadeddata', function () {
					if ((typeof lesson_number !== typeof undefined) && (lesson_number !== false)) {
						if (setTime) {
							theAudio.currentTime = setTime;
						}
						else if ((typeof localStorage['lecon-' + lesson_number] !== typeof undefined)
							&& localStorage['lecon-' + lesson_number] !== 'undefined'
						) {
							theAudio.currentTime = +localStorage['lecon-' + lesson_number];
						}
					}
					timeDuration.text(secondsToTime(theAudio.duration));
					volumeAdjuster.find('div').height(theAudio.volume * 100 + '%');
					volumeDefault = theAudio.volume;
					event = new CustomEvent('lessonPlayerReady');
					window.dispatchEvent(event)
				});

				theAudio.addEventListener('timeupdate', function () {
					timeCurrent.text(secondsToTime(theAudio.currentTime));
					barPlayed.width((theAudio.currentTime / theAudio.duration) * 100 + '%');

					var lesson_number = $(theAudio).attr('number');
					if ((typeof lesson_number !== typeof undefined) && (lesson_number !== false) && (theAudio.currentTime !== 0)) {
						localStorage['lecon-' + lesson_number] = theAudio.currentTime;
					}
				});

				theAudio.addEventListener('volumechange', function () {
					volumeAdjuster.find('div').height(theAudio.volume * 100 + '%');

					if (theAudio.volume > 0 && thePlayer.hasClass(cssClass.mute)) {
						thePlayer.removeClass(cssClass.mute);
					}

					if ((theAudio.volume <= 0) && !thePlayer.hasClass(cssClass.mute)) {
						thePlayer.addClass(cssClass.mute);
					}
				});

				theAudio.addEventListener('ended', function () {
					thePlayer.removeClass(cssClass.playing);

					var lesson_number = $(theAudio).attr('number');
					if ((typeof lesson_number !== typeof undefined) && (lesson_number !== false)) {
						localStorage.removeItem('lecon-' + lesson_number);
						$menuPlayer.removeClass(cssClass.playing);
					}
				});

				theBar.on(eStart, function (e) {
					adjustCurrentTime(e);
					theBar.on(eMove, function (e) {
						adjustCurrentTime(e);
					});
				}).on(eCancel, function () {
					theBar.off(eMove);
				});

				volumeButton.on('click', function () {
					if (thePlayer.hasClass(cssClass.mute)) {
						thePlayer.removeClass(cssClass.mute);
						theAudio.volume = volumeDefault;
					} else {
						thePlayer.addClass(cssClass.mute);
						volumeDefault = theAudio.volume;
						theAudio.volume = 0;
					}
					return false;
				});
				
				downloadButton.on('click', function (e) {
					if (isStrict) {
						e.preventDefault()
						dispatchEvent(new Event('strictDownload'))
					}
				})

				volumeAdjuster.on(eStart, function (e) {
					adjustVolume(e);
					volumeAdjuster.on(eMove, function (e) {
						adjustVolume(e);
					});
				}).on(eCancel, function () {
					volumeAdjuster.off(eMove);
				});
			} else {
				thePlayer.addClass(cssClass.mini);
			}

			if ((typeof lesson_number !== typeof undefined) && (lesson_number !== false)) {
				if ((typeof localStorage['lecon-' + lesson_number] !== typeof undefined)
					&& localStorage['lecon-' + lesson_number] !== 'undefined'
				) {
					theAudio.currentTime = +localStorage['lecon-' + lesson_number];
				}

				$menuPlayer.addClass(cssClass.mini).addClass('pull-right');
				$menuPlayer.attr('number', $menuPlayer.find('audio').attr('number'));
				$menuPlayer.find('audio').remove();
				$menuPlayer.prepend($(`<div class="${cssClass.tenSecondsBack}" title="Отмотать на 10 секунд"><a class="fas fa-undo-alt" href="#"></a></div>`));
				$menuPlayer.find('.' + cssClass.tenSecondsBack).prepend(tenSecondsBackMaskSvg);
				$('nav.navbar > .container > .d-flex.order-2 > .navbar-nav').prepend($menuPlayer);

				$menuPlayer.find('.' + cssClass.playPause).on('click', function (e) {
					e.preventDefault();
					return playerPlayPause(true);
				});
				$menuPlayer.find('.' + cssClass.tenSecondsBack).on('click', e => {
					e.preventDefault();
					return playerSeekBack(10);
				});

				let hidden, visibilityChange;
				if (typeof document.hidden !== 'undefined') {
					hidden = 'hidden';
					visibilityChange = 'visibilitychange';
				} else if (typeof document.msHidden !== 'undefined') {
					hidden = 'msHidden';
					visibilityChange = 'msvisibilitychange';
				} else if (typeof document.webkitHidden !== 'undefined') {
					hidden = 'webkitHidden';
					visibilityChange = 'webkitcisibilitychange'
				}

				if (typeof document.addEventListener === 'undefined' || hidden === undefined) {
					console.log("Audio player requires a browser, such as Google Chrome or Firefox," +
						" that supports the Page Visibility API");
				} else if (isStrict) {
					document.addEventListener(visibilityChange, handleVisibilityChange, false)
				}
			}

			if (isAutoPlay) {
				thePlayer.addClass(cssClass.playing);
			}

			thePlayer.find('.' + cssClass.playPause).on('click', function () {
				return playerPlayPause(false);
			});

			function playerPlayPause(is_menu) {
				if (thePlayer.hasClass(cssClass.playing)) {
					$(this).attr('title', params.strPlay).find('a').html(params.strPlay);

					if (typeof $menuPlayer !== typeof undefined) {
						if (is_menu) {
							thePlayer.find('.' + cssClass.playPause)
								.attr('title', params.strPlay).find('a').html(params.strPlay);
						} else {
							$menuPlayer.find('.' + cssClass.playPause)
								.attr('title', params.strPlay).find('a').html(params.strPlay);
						}

						$menuPlayer.removeClass(cssClass.playing);
					}

					thePlayer.removeClass(cssClass.playing);

					if (isSupport) {
						theAudio.pause();
					} else {
						theAudio.Stop();
					}
				} else {
                    if ((typeof lesson_number !== typeof undefined) && (lesson_number !== false) && document['hidden']){
                        return false;
					}

					$(this).attr('title', params.strPause).find('a').html(params.strPause);

					if (typeof $menuPlayer !== typeof undefined) {
						if (is_menu) {
							thePlayer.find('.' + cssClass.playPause)
								.attr('title', params.strPause).find('a').html(params.strPause);
						} else {
							$menuPlayer.find('.' + cssClass.playPause)
								.attr('title', params.strPlay).find('a').html(params.strPause);
						}

						$menuPlayer.addClass(cssClass.playing);
					}

					thePlayer.addClass(cssClass.playing);

					if (isSupport) {
						theAudio.play()
					} else {
						theAudio.Play();
					}
				}

				return false;
			}

			function playerSeekBack(s) {
				theAudio.currentTime -= s
			}

			function handleVisibilityChange() {
				if (isStrict) {
					console.log(`Visibility Changed. Playing: ${thePlayer.hasClass(cssClass.playing)}`)
					// 	if (document["hidden"] && thePlayer.hasClass(cssClass.playing)) {
					// 		playerStop()
					// 		wasPlaying = true
					// 	} else if (!document['hidden'] && !thePlayer.hasClass(cssClass.playing)) {
					// 		playerStart()
					// 		if (wasPlaying) {
					// 			dispatchEvent(new Event('unhiddenWasPlaying'))
					// 		}
					// 	}
				}
			}

			function playerStop() {
				playerPlayPause(false)
				setTime = theAudio.currentTime
				theAudio.src = ""
				theAudio.load()
			}

			function playerStart() {
				theAudio.src = audioFile
				theAudio.load()
				theAudio.currentTime = setTime
			}

			$this.replaceWith(thePlayer);
		});
		return this;
	};
})(jQuery, window, document);
