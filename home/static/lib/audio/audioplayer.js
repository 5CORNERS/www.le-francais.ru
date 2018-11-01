/*
	AUTHOR: Osvaldas Valutis, www.osvaldas.info
*/

;$(document).ready(function () {
	$('audio').audioPlayer();
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
		return !!( audioElement.canPlayType &&
					audioElement.canPlayType('audio/' + file.split('.')
															.pop()
															.toLowerCase() + ';')
															.replace(/no/, '')
				);
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
				downloadButton: 'download-button'
			};

		for (var subName in cssClassSub)
		{
			cssClass[subName] = params.classPrefix + '-' + cssClassSub[subName];
		}

		this.each(function () {
			if ($(this).prop('tagName').toLowerCase() != 'audio')
			return false;

			var $this = $(this),
			audioFile = $this.attr('src'),
			isAutoPlay = $this.get(0).getAttribute('autoplay'),
			isAutoPlay = ((isAutoPlay === '') || (isAutoPlay === 'autoplay')) ? true : false,
			isLoop = $this.get(0).getAttribute('loop'),
			isLoop = ((isLoop === '') || (isLoop === 'loop')) ? true : false,
			isSupport = false,
			setTime = $this.get(0).getAttribute('set-time');

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
								+ ( (isSupport) ?
										$('<div>').append($this.eq(0).clone()).html()
										: '<embed src="' + audioFile + '" width="0" height="0" volume="100" autostart="' + isAutoPlay.toString() + '" loop="' + isLoop.toString() + '" />'
								)
								+ '<div class="' + cssClass.playPause + '" title="' + params.strPlay + '"><a href="#">' + params.strPlay + '</a></div></div>'
							),
				theAudio = (isSupport) ? thePlayer.find('audio') : thePlayer.find('embed'),
				theAudio = theAudio.get(0);

			var lesson_number = $(theAudio).attr('number');

			if ((typeof lesson_number !== typeof undefined) && (lesson_number !== false)) {
				var $menuPlayer = thePlayer.clone();
			}

			if (isSupport) {
				thePlayer.find('audio').css({'width': 0, 'height': 0, 'visibility': 'hidden'});
				thePlayer.append('<div class="' + cssClass.time + ' ' + cssClass.timeCurrent + '"></div><div class="' + cssClass.bar + '"><div class="' + cssClass.barLoaded + '"></div><div class="' + cssClass.barPlayed + '"></div></div><div class="' + cssClass.time + ' ' + cssClass.timeDuration + '"></div><div class="' + cssClass.volume + '"><div class="' + cssClass.volumeButton + '" title="' + params.strVolume + '"><a href="#">' + params.strVolume + '</a></div><div class="' + cssClass.volumeAdjust + '"><div><div></div></div></div></div>');

				var downloadable = $(theAudio).attr('data-downloadable');

				if ((typeof downloadable !== typeof undefined) && (downloadable !== false)) {
					var source = $(theAudio).find('source').attr('src');

					thePlayer.append('<div class="' + cssClass.download + '"><a download="true" href="' + source + '" class="' + cssClass.downloadButton + ' glyphicon glyphicon-download"></a></div>');
					$(theAudio).attr('id', 'lesson-audio');
					$(theAudio).attr('number', lesson_number);
				}

				var theBar = thePlayer.find('.' + cssClass.bar),
					barPlayed = thePlayer.find('.' + cssClass.barPlayed),
					barLoaded = thePlayer.find('.' + cssClass.barLoaded),
					timeCurrent = thePlayer.find('.' + cssClass.timeCurrent),
					timeDuration = thePlayer.find('.' + cssClass.timeDuration),
					volumeButton = thePlayer.find('.' + cssClass.volumeButton),
					volumeAdjuster = thePlayer.find('.' + cssClass.volumeAdjust + ' > div'),
					volumeDefault = 0,
					adjustCurrentTime = function (e) {
						theRealEvent = isTouch ? e.originalEvent.touches[0] : e;
						theAudio.currentTime = Math.round(( theAudio.duration * ( theRealEvent.pageX - theBar.offset().left ) ) / theBar.width());
					},
					adjustVolume = function (e) {
						theRealEvent = isTouch ? e.originalEvent.touches[0] : e;
						theAudio.volume = Math.abs(( theRealEvent.pageY - ( volumeAdjuster.offset().top + volumeAdjuster.height() ) ) / volumeAdjuster.height());
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
					timeDuration.text(secondsToTime(theAudio.duration));
					volumeAdjuster.find('div').height(theAudio.volume * 100 + '%');
					volumeDefault = theAudio.volume;
					theAudio.currentTime=setTime;
				});

				theAudio.addEventListener('timeupdate', function () {
					timeCurrent.text(secondsToTime(theAudio.currentTime));
					barPlayed.width(( theAudio.currentTime / theAudio.duration ) * 100 + '%');

					var lesson_number = $(theAudio).attr('number');
					if ((typeof lesson_number !== typeof undefined) && (lesson_number !== false)) {
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

				$menuPlayer.addClass(cssClass.mini);
				$menuPlayer.attr('number', $menuPlayer.find('audio').attr('number'));
				$menuPlayer.find('audio').remove();
				$('.navbar-header').prepend($menuPlayer);

				$menuPlayer.find('.' + cssClass.playPause).on('click', function(e) {
					e.preventDefault();
					return playerPlayPause(true);
				});
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
					$(this).attr('title', params.strPause).find('a').html(params.strPause);

					if (typeof $menuPlayer !== typeof undefined) {
						if (is_menu)
						{
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

			$this.replaceWith(thePlayer);
		});
		return this;
	};
})(jQuery, window, document);