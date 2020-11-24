(async function () {

    var url_string = window.location.href;
    var url = new URL(url_string);
    var $dictApp = $('#dict-app')
    const currentLessonNumber = $dictApp.data('lesson-number')
    const currentPacketID = $dictApp.data('packet-id');
    const showNegativeDefault = $dictApp.data('show-negative')
    const translateInfinitivesDefault = $dictApp.data('translate-infinitives')

    const response = await fetch('/dictionary/verbs/' + currentPacketID);
    const data = await response.json();
    const LISTENING = 0;
    const CHECKING = 1;

    const CARD_TYPE_AFFIRMATIVE = 0
    const CARD_TYPE_NEGATIVE = 1

    const TENSE_INDICATIVE_PRESENT = 0
    const TENSE_PASSE_COMPOSE = 1
    const TENSE_IMPERATIVE = 2
    const TENSE_INDICATIVE_IMPARFAIT = 3
    const TENSE_INDICATIVE_FUTURE = 4
    const TENSE_AUDIO_URLS = {
        [TENSE_INDICATIVE_PRESENT]: "/static/dictionary/media/indicatif_present.mp3",
        [TENSE_PASSE_COMPOSE]: "/static/dictionary/media/passe_compose.mp3",
        [TENSE_IMPERATIVE]: "/static/dictionary/media/impératif_présent.mp3",
        [TENSE_INDICATIVE_IMPARFAIT]: "/static/dictionary/media/imparfait.mp3",
        [TENSE_INDICATIVE_FUTURE]: "/static/dictionary/media/futur_simple.mp3",
    }
    const TENSE_NAMES = {
        [TENSE_INDICATIVE_PRESENT]: "Indicatif Présent",
        [TENSE_PASSE_COMPOSE]: "Passé Composé",
        [TENSE_IMPERATIVE]: "Impératif Présent",
        [TENSE_INDICATIVE_IMPARFAIT]: "Imparfait",
        [TENSE_INDICATIVE_FUTURE]: "Futur Simple",
    }

    const SILENCE_URL = '/static/dictionary/media/silence.2b5bb705.mp3';
    const silence = new Howl({
      src: SILENCE_URL,
      loop: false,
    })

    const TENSE_SOUNDS = Object.keys(TENSE_AUDIO_URLS).map((key, url) => {
        return {
            [key]: new Howl({
                src: [url],
                preload: true,
                loop: false,
                buffer: true,
                html5: true,
                onload: () => resolve(howl),
                onloaderror: () => resolve(silence)
            })
        }
    })


    var createSound = async function(url) {
        return new Promise((resolve, reject) => {
            const howl = new Howl({
                src: [url],
                preload: true,
                loop: false,
                buffer: true,
                html5: true,
                onload: () => resolve(howl),
                onloaderror: () => resolve(silence)
            })
        })
    }

    var loadCards = async function (packetId, more_lessons = undefined) {
        let verbs = []
        let r
        if (more_lessons !== undefined && typeof more_lessons === 'number') {
            r = await fetch(`/dictionary/verbs/${packetId}/${more_lessons}`);
        } else {
            r = await fetch(`/dictionary/verbs/${packetId}/`)
        }
        let d = await r.json();
        d.verbs.forEach(function (form) {
            verbs = verbs.concat(form)
            verbs = verbs.concat(form.forms)
        });

        return [verbs.map((form) => {
            return {
                ...form,
                flipped: false,
                formSound: createSound(form.pollyUrl),
                translationSound: createSound(form.trPollyUrl)
            }
        }), d.packets];
    }

    const getAudionDuration = (audio) => {
        return new Promise((resolve, reject) => {
            audio.onloadedmetadata = () => {
                resolve(audio.duration);
            }
        });
    }

    async function playSound(sound) {
        if ((sound === undefined) || (sound === null)) {
            return 0;
        }
        return new Promise(resolve => {
            sound.then((howl) => {
                howl.once('end', () => {
                    resolve(howl.duration())
                })
                howl.play()
            })
        })
    }

    new Vue({

        el: '#flashcard-app',
        data: {
            cards: [],
            cardsRepeat: [],
            //cardsRepeat — тоже самое что и cards, но перевод и слово поменяны местами
            card: undefined,
            currentCard: 0,
            translation: undefined,
            progress: 0,
            progressStep: 0,
            timeoutWordsListening: 0.5, // время между словами в режиме прослушивания
            timeoutWordsChecking: 1, // время между словами в режиме проверки
            timeoutTranslation: 5, // время между переводом
            timeoutInfinitive: 1.2, // время до и после инфинитива
            type: LISTENING,
            pause: true,
            error: false,
            showNegative: showNegativeDefault,
            translateInfinitives: translateInfinitivesDefault,
            timeoutInfinitiveTranslation: 0.5,
            timeoutTense: 1,
            TYPE_LISTENING: LISTENING,
            TYPE_CHECKING: CHECKING,
            moreVerbsLoaded: false,
            lessonNumber: currentLessonNumber,
            packets: [],
            loadMoreOptions: [],
        },

        async mounted() {
            let values = await loadCards(currentPacketID);
            this.cards = values[0];
            this.packets = values[1];
            this.init();
        },

        methods: {

            init: function () {
                this.progress = 0
                this.progressStep = 100 / (this.cards.length - 1);
                this.initRepeatCards();
                this.card = this.cards[0]
                this.translation = this.cards[0]['translation']
                console.log(this.cards);
            },

            getVerbsCountById: function (packetId) {
                let packet = this.packets.find(packet => packet.id === packetId);
                if (packet) {
                    return packet.verbsCount
                } else {
                    return null
                }
            },

            getVerbsCountByLesson: function (lessonNumber) {
                let packet = this.packets.find(packet => packet.lessonNumber === lessonNumber);
                if (packet) {
                    return packet.verbsCount
                } else {
                    return null
                }
            },

            lessonsAbove: function () {
                let dif = this.lessonNumber - 5
                let la
                if (dif < 0) {
                    la = 5 + dif
                } else {
                    return 'пяти'
                }
                if (la === 4) {
                    return 'четырёх'
                } else if (la === 3) {
                    return 'трёх'
                } else if (la === 2) {
                    return 'двух'
                } else if (la === 1) {
                    return 'одного'
                }
            },

            initRepeatCards: function () {
                this.cardsRepeat = this.cards.slice().map((i) => {
                    return {
                        ...i,
                        form: i.translation,
                        verb: i.translation,
                        translation: i.verb || i.form,
                        pollyUrl: i.trPollyUrl,
                        trPollyUrl: i.pollyUrl,
                        formSound: i.translationSound,
                        translationSound: i.formSound
                    }
                })
                this.shuffle(this.cardsRepeat)
            },

            loadInitCards: async function () {
                if (!this.pause) {
                    this.pause = true;
                }
                let values = await loadCards(currentPacketID);
                this.cards = values[0];
                this.packets = values[1];
                this.init();
                this.startOver();
                this.moreVerbsLoaded = false;
            },

            loadMoreCards: async function () {
                if (!this.pause) {
                    this.pause = true;
                }
                let values = await loadCards(currentPacketID, 5);
                this.cards = values[0];
                this.packets = values[1];
                this.init();
                this.startOver();
                this.moreVerbsLoaded = true;
            },

            startOver: function () {
                this.progress = 0;
                this.currentCard = 0;
            },

            getNextCard: function () {
                if (this.type === LISTENING) {
                    let nextCard = this.cards.slice(this.currentCard + 1).find(card => card.isShownOnDrill)
                    if (nextCard === undefined) {
                        return this.cards[0]
                    }
                    return nextCard
                } else {
                    if (this.currentCard === (this.cards.length - 1)) {
                        return this.cards[0]
                    }
                    return this.cards[this.currentCard + 1]
                }
            },
            isInfinitive: function () {
                return 'forms' in this.card
            },
            nextCardIsInfinitive: function () {
                return 'forms' in this.getNextCard()
            },


            togglePause: function () {
                this.pause = !this.pause;
                if (this.pause === false) {
                    if (this.type === LISTENING) {
                        this.playCards(this.cards);
                    } else {
                        this.playCards(this.cardsRepeat);
                    }
                }
            },

            toggleType: function () {

                if (this.type === LISTENING) {
                    this.type = CHECKING
                } else {
                    this.type = LISTENING
                }
                this.progress = 0;
                this.currentCard = 0;
                this.pause = true;

                if (this.type === LISTENING) {
                    this.progressStep = 100 / (verbs.length - 1);
                    this.card = this.cards[0];
                } else {
                    this.progressStep = 100 / verbs.length;
                    this.card = this.cardsRepeat[0];
                }
            },

            shuffle: function (array) {
                array.sort(() => Math.random() - 0.5);
            },

            playNextCard: function () {
                this.currentCard++;
                if (this.currentCard === (this.cards.length)) {
                    this.currentCard = 0
                    this.progress = 0
                    if (this.type === CHECKING) {
                        this.shuffle(this.cardsRepeat)
                    }
                }
                if (this.type === LISTENING) {
                    this.card = this.cards[this.currentCard];
                } else {
                    this.card = this.cardsRepeat[this.currentCard];
                }
                this.playCards();
            },

            getTenseUrl: function () {
                let tense = this.card.tense
                return TENSE_AUDIO_URLS[tense]
            },

            getTenseSound: function () {
                return TENSE_SOUNDS[this.card.tense]
            },

            getLastCard: function() {
                if (this.currentCard === 0) {
                    return null;
                } else {
                    return this.cards[this.currentCard - 1]
                }
            },

            isSameTense: function () {
                let has_tenses = []
                this.cards.forEach(el => {
                        if (has_tenses.indexOf(el.tense)) {
                            has_tenses.push(el.tense)
                        }
                    }
                )
                return has_tenses.length === 1;

            },

            playCards: function () {
                if (!this.pause) {
                    let _this = this;

                    if (this.progress < 100) {
                        this.progress += this.progressStep;
                    }

                    if (!this.showNegative && this.card.type === CARD_TYPE_NEGATIVE) {
                        return this.playNextCard()
                    }

                    if (this.card.isShownOnDrill || this.type === CHECKING) {
                        let afterVerbTimeout;
                        if (this.nextCardIsInfinitive() || this.isInfinitive()) {
                            // текущая или следующая карточка -- инфинитив
                            afterVerbTimeout = this.timeoutInfinitive * 1000
                            console.log('infinitive')
                        } else {
                            // текущая и следующая карточка -- не инфинитив
                            console.log('not-infinitive')
                            if (this.type === LISTENING) {
                                afterVerbTimeout = this.timeoutWordsListening * 1000;
                            } else {
                                afterVerbTimeout = this.timeoutWordsChecking * 1000;
                            }
                        }
                        // произносим время, если предыдузая карточка была другого времени
                        let tenseUrl = undefined
                        let tenseSound = undefined
                        let afterTenseTimeout = 0
                        if (
                            this.type === LISTENING && (
                                (this.currentCard === 0 && !(this.isSameTense() && this.card.tense === TENSE_INDICATIVE_PRESENT)) || (
                                    this.getLastCard() !== null && this.getLastCard().tense !== this.card.tense
                                )
                            )
                        ) {
                            tenseUrl = this.getTenseUrl()
                            tenseSound = this.getTenseSound()
                            afterTenseTimeout = this.timeoutTense * 1000
                        }
                        playSound(tenseSound).then(function (tenseDuration) {
                            tenseDuration = 0
                            console.log('tense timeout: ' + (tenseDuration + afterTenseTimeout))
                            setTimeout(function () {
                                playSound(_this.card.formSound).then(function (verbDuration) {
                                    verbDuration = 0;
                                    var beforeTranslationTimeout;
                                    if (_this.card.isTranslation || _this.type === CHECKING) {
                                        // карточка подлежит переводу или режим проверки
                                        beforeTranslationTimeout = this.timeoutTranslation * 1000 + verbDuration;
                                    } else if (_this.translateInfinitives && _this.isInfinitive() && _this.type === LISTENING) {
                                        beforeTranslationTimeout = this.timeoutInfinitiveTranslation * 1000 + verbDuration;
                                    } else if (_this.type === LISTENING) {
                                        // режим прослушивания и карточка не подлежит переводу
                                        beforeTranslationTimeout = 0;
                                    }
                                    console.log('translation timeout: ' + (beforeTranslationTimeout + verbDuration))
                                    setTimeout(function () {
                                        let translationUrl = undefined;
                                        let translationSound = undefined;
                                        if ((_this.type === LISTENING && _this.card.isTranslation) || _this.type === CHECKING || (_this.translateInfinitives && _this.isInfinitive() && _this.type === LISTENING)) {
                                            translationUrl = _this.card.trPollyUrl;
                                            translationSound = _this.card.translationSound
                                            _this.card.flipped = !_this.card.flipped;
                                        }
                                        playSound(translationSound).then(function (translationDuration) {
                                            translationDuration = 0;
                                            let timeout = 0;
                                            if (_this.isInfinitive()) {}
                                            setTimeout(function () {
                                                console.log('word timeout: ' + (afterVerbTimeout + translationDuration))
                                                setTimeout(function () {
                                                    _this.playNextCard()
                                                }, afterVerbTimeout + translationDuration);
                                            }.bind(_this), translationDuration)
                                        }.bind(_this))
                                    }, beforeTranslationTimeout + verbDuration);
                                }.bind(_this));
                            }, tenseDuration + afterTenseTimeout)
                        }.bind(_this))
                    }else{
                        return this.playNextCard()
                    }
                }
            }
        }
    });

})();
