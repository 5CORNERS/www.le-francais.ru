let reloadedTabs = []
const lazyTabs = [
    {elementID: 'tab-flash-cards', tabID: 'flash-cards'},
    {elementID: 'tab-verbs', tabID: 'verbs'},
    {elementID: 'tab-my-words', tabID: 'my-words'}
]
let clickedTabs = []

function reloadPage(lesson_number, tabID = 0) {
    $.ajax({
        type: 'GET',
        url: Urls['api:get_lesson_content'](lesson_number, 1, tabID),
        beforeSend: function () {
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
                    if (tab.transition) {
                        $(document).on('hidden.bs.modal', function () {
                            navLink.parent().fadeIn(500);
                            navLink.css({
                                "background-color": "#90ee90",
                                "color": "#003e73",
                                "transition": "background-color 0.5s ease"
                            });
                            setTimeout(function () {
                                navLink.css({
                                    "background-color": "#ffffff",
                                    "color": "",
                                    "transition": "background-color 10s ease"
                                });
                            }, 500)
                        })
                    }
                    $(`div.tab-pane#${tab.href}`).html(tab.value);
                    reloadedTabs.push({
                        elementID: navLink.attr('id'), tabID: tab.href
                    })
                }
            });
            $('[data-toggle="popover"]').popover()

        }
    });
}

function reloadLessonUrl() {
    $.ajax({
        type: 'POST',
        url: '/api/get_lesson_url/',
        data: {
            'csrfmiddlewaretoken': CSRF_TOKEN,
            'lesson_number': LESSON_NUMBER
        },
        datatype: 'json',
        success: function (r) {
            if (r.status === 200) {
                let audio = $('#lesson-audio')[0];
                let audioTime = audio.currentTime;
                audio.src(r.lesson_url);
                audio.load();
                audio.currentTime = audioTime;
                audio.play();
            } else {
            }
        }
    })
}

function errHandle(a) {
    console.log("Error " + a.error.code + "; details: " + a.error.message);
}


$(document).ready(function () {
    lazyTabs.forEach(function (value, index) {
        $(`a#${value.elementID}`).one('show.bs.tab', function () {
            clickTab(value.tabID)
        })
    })

    let ua = window.navigator.userAgent;
    let iOS = !!ua.match(/iPad/i) || !!ua.match(/iPhone/i);
    let is_webkit = !!ua.match(/WebKit/i);
    var iOSSafari = iOS && is_webkit && !ua.match(/CriOS/i);

    if (NEED_PAYMENT) {
        function sawProceed() {
            activateLesson('saw');
            setTimeout(activateLesson('proceed'), 1000);
        }

        $('[data-saw-proceed]').on('click', sawProceed);

        function showMinusCups() {
            $('#activated-dismiss-button').hide();
            $('#activated-unsofficiant-cups-button').hide();
            $('.minus-cups').show();
        }

        function showUnsMinusCups() {
            $('#activated-dismiss-button').hide();
            $('#activated-unsofficiant-cups-button').hide();
            $('.unsofficiant-cups-credit').show();
        }

        activateSounds = ['composter-01.mp3', 'composter-02.mp3', 'composter-03.mp3', 'composter-04.mp3'];

        function playActivateSound() {
            let index = Math.floor(Math.random() * 1000) % 4;
            console.log(index);
            let src = ('https://files.le-francais.ru/sound/' + activateSounds[index]);
            let audio = $('<audio class="sound-player" autoplay="autoplay" style="display:none;">'
                + '<source src="' + src + '" />'
                + '<embed src="' + src + '" hidden="true" autostart="true" loop="false"/>'
                + '</audio>'
            ).appendTo('body');
            audio[0].play();
        }

        function activate() {
            $('.success-message').hide();
            $('.fail-message').hide();
            $('.minus-cups').hide();
            $('.unsofficiant-cups-credit').hide();
            $('.waiting-message').show();
            $('#lesson-activated-modal').modal('show');
            $.ajax({
                type: 'POST',
                url: Urls['activate:activate_lesson'](),
                data: {
                    'csrfmiddlewaretoken': CSRF_TOKEN,
                    'lesson_number': LESSON_NUMBER
                },
                datatype: 'json',
                cache: false,
                headers: {"cache-control": "no-cache"},
                async: !iOSSafari,
                success: function (r) {
                    if (r.result === 'SUCCESS') {
                        playActivateSound();
                        window.location.href = window.location.pathname + "?" + $.param({'modal_open': 'lesson-activated-modal'});
                    } else if (r.result === 'ZERO_CUPS') {
                        $('.waiting-message').hide();
                        $('.unsofficiant-cups').show();
                        if ((cups_amount < 0) && (cups_credit === 0)) {
                            showUnsMinusCups()
                        }
                    } else if (r.result === 'ALREADY') {
                        $('.waiting-message').hide();
                        $('.already-activated').show();

                    } else if (r.result === 'NOT_AUTH') {
                        $('.waiting-message').hide();
                        $('.login-need').show();
                    }
                }
            });
        }

        function disableActivButton() {
            let button = $('#activate-button');
            button.removeClass('btn-primary').addClass('btn-success');
            button.disabled = true;
        }

        function activateLesson(state) {
            switch (state) {
                case 'tab':
                case 'download':
                case 'ended':
                    let audio = $('#lesson-audio')[0];
                    localStorage['lecon-{{ self.lesson_number }}'] = audio.duration - 5;
                    if (!IS_AUTHENTICATED) {
                        $('#listen-login-required-modal').modal('show');
                    } else {
                        if (saw_message) {
                            $('#lesson-not-activated-simple-modal').modal('show');
                        } else {
                            $('#lesson-not-activated-details-continue-modal').modal('show');
                        }
                    }
                    break;
                case 'button':
                    if (saw_message) {
                        activateLesson('proceed')
                    } else {
                        $('#lesson-not-activated-details-activate-modal').modal('show')
                    }
                    break;
                case 'saw':
                    sawMessage('make_true');
                    break;
                case 'proceed':
                    if (!userlesson) {
                        activate();
                    }
                    break;
            }
        }

        if (!userlesson && must_pay || NEED_PAYMENT && !IS_AUTHENTICATED) {
            window.addEventListener('lessonPlayerReady', function () {
                let downloadButton = $('.audioplayer-download-button')[0];
                downloadButton.addEventListener('click', function () {
                    activateLesson('download');
                });
                let lessonAudio = $('#lesson-audio')[0];
                lessonAudio.addEventListener('ended', function () {
                    activateLesson('ended')
                });
            });
            $('[data-activate-lesson]').click(function () {
                activateLesson($(this).data('activate-lesson'))
            });
            $('#tab-flash-cards').removeAttr('data-toggle');
            $('#tab-exercises-de-lesson').removeAttr('data-toggle');
            $('#tab-exercise').removeAttr('data-toggle');
            $('#tab-my-words').removeAttr('data-toggle');
            $('#tab-verbs').removeAttr('data-toggle');
            $('#tab-resume-populaire').removeAttr('data-toggle');
            $('#tab-flash-cards').click(function (e) {
                e.preventDefault();
                activateLesson('tab')
            });
            $('#tab-exercises-de-lesson').click(function (e) {
                e.preventDefault();
                activateLesson('tab')
            });
            $('#tab-exercise').click(function (e) {
                e.preventDefault();
                activateLesson('tab')
            });
            $('#tab-my-words').click(function (e) {
                e.preventDefault();
                activateLesson('tab')
            });
            $('#tab-verbs').click(function (e) {
                e.preventDefault();
                activateLesson('tab')
            });
            $('#tab-resume-populaire').click(function (e) {
                e.preventDefault();
                activateLesson('tab')
            });
        }
    } else {
        if (!IS_AUTHENTICATED && LESSON_NUMBER > 5) {
            $(window).one('lessonPlayerReady', function () {
                $('.audioplayer-download-button').on('click', function (e) {
                    e.preventDefault();
                    $.ajax({
                        url: Urls['modal:download_login_required'](),
                        type: 'GET',
                        data: {
                            redirect_url: window.location.pathname
                        },
                        datatype: 'html',
                        success: function (data) {
                            let modal = $(data);
                            modal.modal('show');
                        }
                    })
                })
            })
        }
    }

    function getSuccessButton() {
        let new_button = $(
            "<button" +
            " class='coffee-button btn btn-success btn-xs'" +
            " disabled='disabled'" +
            " id='coffee-button'" +
            ">" +
            "<img" +
            " id='coffee-button-image'" +
            " class='coffee-button-image'" +
            ` src='${BY_ME_A_COFFEE_SVG}'` +
            "<div" +
            " id='coffee-button-text'" +
            " class='coffee-button-text'>" +
            "Вы уже угощали меня<br>за этот урок :)" +
            "</div>" +
            "</button>");
        $("#coffee-button").replaceWith(new_button);
        $("#coffeeButtonHelp").hide()
    }

    function playCoffeeSound() {
        let coffeeAudio = new Audio(COFFEE_SOUND_URL);
        coffeeAudio.play();
    }

    function showActivateMessage() {
        if (sawMessage()) {
            $('#lesson-not-activated-subsequent-modal').show()
        } else {
            $('#lesson-not-activated-first-modal').show()
        }
    }

    function sawMessage(val) {
        switch (val) {
            case 'get_state': {
                $.ajax({
                    type: "POST",
                    url: Urls['custom_user:saw_message'](),
                    data: {
                        'csrfmiddlewaretoken': CSRF_TOKEN,
                        'action': 'get_state'
                    },
                    success: function (r) {
                        if (r.status === 200) {
                            return true
                        }
                    }
                });
                break
            }
            case 'make_true': {
                saw_message = true;
                $.ajax({
                    type: "POST",
                    async: false,
                    url: Urls['custom_user:saw_message'](),
                    data: {
                        'csrfmiddlewaretoken': CSRF_TOKEN,
                        'action': 'make_true'
                    },
                    success: function (r) {
                        if (r.status === 200) {
                            return true
                        }
                    }
                })
            }
        }
    }


    function giveMeCoffee() {
        $('.modal').modal('hide');
        $.ajax({
            type: "POST",
            url: Urls['coffee:give_me_a_coffee'](),
            data: {
                'lesson_number': LESSON_NUMBER,
                'csrfmiddlewaretoken': CSRF_TOKEN
            },
            async: !iOSSafari,
            datatype: "json",
            cache: false,
            headers: {"cache-control": "no-cache"},
            success: function (response) {
                if (response.result === 'SUCCESS') {
                    playCoffeeSound();
                    $('#give-me-a-coffee-success-message').html(response.description);
                    $('#give-me-a-coffee-complete-modal').modal('show');
                    getSuccessButton();
                    let $lessonAudioBlock = $('#lessonAudioBlock')
                    $lessonAudioBlock.find('.audioplayer-download-button').attr('href', LESSON_LISTEN_URL).off('.strict');
                    userlesson = true;
                    reloadPage(LESSON_NUMBER);
                } else if (response.result === 'ALREADY') {
                    $('#give-me-a-coffee-fail-message').html(response.description);
                    $('#give-me-a-coffee-fail-modal').modal('show');
                    getSuccessButton();
                    reloadPage(LESSON_NUMBER)
                } else {
                    $('#give-me-a-coffee-fail-message').html(response.description);
                    $('#give-me-a-coffee-fail-modal').modal('show');
                }
            },
            error: function (response, error) {
                $('#give-me-a-coffee-fail-message').html(error);
                $('#give-me-a-coffee-fail-modal').modal('show');
            }
        });
    }

    $('.coffee-proceed').on('click', giveMeCoffee);


    addEventListener('strictDownload', function (e) {
        if (!NEED_PAYMENT === true && must_pay === true && !userlesson) {
            $('#strictDownloadModal').modal('show');
        }
    });


    addEventListener('unhiddenWasPlaying', function (e) {
        $('#hiddenWasListeningModal').modal('show');
    });

    $('#unhiddenWasPlaying').click(function (e) {
        let $playPause = $('#lessonAudioBlock').find('#playpause')
        $playPause.click()
    })
    $('#strictDownloadModelWhyThis').popover({
        content: `<p>Мы поддерживаем и улучшаем проект своими силами. Чтобы продолжать
    работу над сайтом, нам важна Ваша поддержка.</p>

<p>Благодарность за уроки идет на техническое обеспечение сайта <a
        id="serversMapImageLink" tabindex="0"
        class="fas fa-info-circle text-primary"
        style="position: relative;top: 1px;"></a> и вознаграждение
    тем, <a href="${WHO_DO_YOU_THINK_WE_ARE}" title="кто эти люди?"
            target="_blank"> кто над ним трудится <i
            class="fas fa-external-link-alt"></i></a>.</p>

<p class="mb-0"><b>Однако, сейчас развитие проекта под угрозой.</b>
    Поэтому мы будем рады, если Вы поддержите нас в этот период.</p>`,
        html: true,
        placement: 'top',
        trigger: 'click',
        template: '<div class="popover" role="tooltip"><div class="arrow"></div><span class="pop-close close">×</span><div class="popover-body"></div></div>'
    }).on('shown.bs.popover', function () {
        $('.pop-close').on('click', function () {
            $('#strictDownloadModelWhyThis').popover('hide')
        })
        $('#serversMapImageLink').on('click', function () {
            $('#strictPopoverModalWhyThis').popover('hide')
            $('#serversMapImageModal').modal('show').one('hide.bs.modal', function () {
                $('#strictDownloadModal').modal('show')
            })
            $('#strictDownloadModal').modal('hide');
        })
    })
    $('#StrictDownloadModelCoffeeButton').on('click', function () {
        $('#strictDownloadModal').modal('hide');
    })

    $('#hiddenWasListeningModalWhyThis').popover({
        content: `<p>Мы поддерживаем и улучшаем проект своими силами. Чтобы продолжать
    работу над сайтом, нам важна Ваша поддержка.</p>

<p>Благодарность за уроки идет на техническое обеспечение сайта <a
        id="serversMapImageLink" tabindex="0"
        class="fas fa-info-circle text-primary"
        style="position: relative;top: 1px;"></a> и вознаграждение
    тем, <a href="${WHO_DO_YOU_THINK_WE_ARE}" title="кто эти люди?"
            target="_blank"> кто над ним трудится <i
            class="fas fa-external-link-alt"></i></a>.</p>

<p class="mb-0"><b>Однако, сейчас развитие проекта под угрозой.</b>
    Поэтому мы будем рады, если Вы поддержите нас в этот период.</p>`,
        html: true,
        placement: 'top',
        trigger: 'click',
        template: '<div class="popover" role="tooltip"><div class="arrow"></div><span class="pop-close close">×</span><div class="popover-body"></div></div>'
    }).on('shown.bs.popover', function () {
        $('.pop-close').on('click', function () {
            $('#hiddenWasListeningModalWhyThis').popover('hide')
        })
        $('#serversMapImageLink').on('click', function () {
            $('#strictPopoverModalWhyThis').popover('hide')
            $('#serversMapImageModal').modal('show').one('hide.bs.modal', function () {
                $('#hiddenWasListeningModal').modal('show')
            })
            $('#hiddenWasListeningModal').modal('hide');
        })
    })
    $('#hiddenWasListeningModalCoffeeButton').on('click', function () {
        $('#hiddenWasListeningModal').modal('hide');
    })
});

