function vueIsLoaded() {
    if (typeof Vue != 'undefined') {
        let url_string = window.location.href;
        let url = new URL(url_string);
        let $dictApp = $('#dict-app')
        let playingInstance = 0
        const currentLessonNumber = $dictApp.data('lesson-number')
        const currentPacketID = $dictApp.data('packet-id');
        const showNegativeDefault = $dictApp.data('show-negative')
        const translateInfinitivesDefault = $dictApp.data('translate-infinitives')
        const safeMode = $('#verbsScript').data('safe-mode')

        const LISTENING = 0;
        const CHECKING = 1;

        const CARD_TYPE_AFFIRMATIVE = 0
        const CARD_TYPE_NEGATIVE = 1

        const TENSE_INDICATIVE_PRESENT = 0
        const TENSE_PASSE_COMPOSE = 1
        const TENSE_IMPERATIVE = 2
        const TENSE_INDICATIVE_IMPARFAIT = 3
        const TENSE_INDICATIVE_FUTURE = 4
        const TENSE_PARTICIPE_PASSE = 5
        const TENSE_AUDIO_URLS = {
            [TENSE_INDICATIVE_PRESENT]: "/static/dictionary/media/indicatif_present.mp3",
            [TENSE_PASSE_COMPOSE]: "/static/dictionary/media/passe_compose.mp3",
            [TENSE_IMPERATIVE]: "/static/dictionary/media/impératif_présent.mp3",
            [TENSE_INDICATIVE_IMPARFAIT]: "/static/dictionary/media/imparfait.mp3",
            [TENSE_INDICATIVE_FUTURE]: "/static/dictionary/media/futur_simple.mp3",
            [TENSE_PARTICIPE_PASSE]: "/static/dictionary/media/silence.mp3"
        }
        const TENSE_NAMES = {
            [TENSE_INDICATIVE_PRESENT]: "Indicatif Présent",
            [TENSE_PASSE_COMPOSE]: "Passé Composé",
            [TENSE_IMPERATIVE]: "Impératif Présent",
            [TENSE_INDICATIVE_IMPARFAIT]: "Imparfait",
            [TENSE_INDICATIVE_FUTURE]: "Futur Simple",
            [TENSE_PARTICIPE_PASSE]: "Participe Passé"
        }

        const SILENCE_URL = '/static/dictionary/media/silence.mp3';
        const silence = new Promise((resolve, reject) => {
            const howl = new Howl({
                src: [SILENCE_URL],
                preload: true,
                loop: false,
                buffer: true,
                html5: true,
                onload: () => resolve(howl)
            })
        })

        const TENSE_SOUNDS = Object.assign({},
            ...Object.keys(TENSE_AUDIO_URLS).map(tense_key => (
                {
                    [tense_key]: new Promise((resolve, reject) => {
                        const howl = new Howl({
                            src: [TENSE_AUDIO_URLS[tense_key]],
                            preload: true,
                            loop: false,
                            buffer: false,
                            html5: true,
                            onload: () => resolve(howl),
                            onloaderror: () => resolve(silence)
                        })
                    })
                }
            ))
        )

        const getAudionDuration = (audio) => {
            return new Promise((resolve, reject) => {
                audio.onloadedmetadata = () => {
                    resolve(audio.duration);
                }
            });
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

                participeTimeoutInfinitive: 0.5,
                participeTimeoutWordsListening: 0.5,
                participeTimeoutWordsChecking: 1,
                participeTimeoutTranslation: 0,
                participeTimeoutInfinitiveTranslation: 0,

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
                loadMoreValue: [],
                loadMoreOptions: [],
                showParticipe: false,
                hasParticipe: false,
                selectedLoadMoreOptions: [],
                playing: false,
                playingSound: undefined,
                verbListHTML: '',
                loadingProgress: 0,
                loadingProgressMax: 0,
                safeMode: false
            },

            async mounted() {
                let safeModeLocalStorage = localStorage.getItem('verbsSafeModeEnabled')
                if (safeModeLocalStorage === 'true') {
                    this.safeMode = true;
                } else {
                    this.safeMode = safeMode;
                }
                let values = await this.loadCards(currentPacketID);
                this.cards = values[0];
                this.packets = values[1];
                // this.verbListHTML = values[2]
                this.loadMoreOptions = this.getLoadMoreOptions();
                this.loadMoreValue = 0;
                this.init();
            },

            watch: {
                safeMode: function () {
                    localStorage.setItem('verbsSafeModeEnabled', this.safeMode)
                }
            },

            methods: {

                init: function () {
                    this.progress = 0
                    this.progressStep = 100 / (this.cards.length - 1);
                    this.initRepeatCards();
                    this.card = this.cards[0]
                    this.translation = this.cards[0]['translation']
                    console.log(this.cards);
                    this.hasParticipe = this.cards.filter(card => card.tense === TENSE_PARTICIPE_PASSE).length > 0
                },

                loadCards: async function (packetId, more_lessons = undefined) {
                    let verbs = []
                    let d
                    if (typeof verbs_data === 'undefined') {
                        let r
                        if (more_lessons !== undefined && typeof more_lessons === 'number') {
                            r = await fetch(`/dictionary/verbs/${packetId}/${more_lessons}`);
                        } else {
                            r = await fetch(`/dictionary/verbs/${packetId}/`)
                        }
                        d = await r.json();
                    } else {
                        d = verbs_data
                    }
                    d.verbs.forEach(function (form) {
                        verbs = verbs.concat(form)
                        verbs = verbs.concat(form.forms)
                    });

                    return [verbs.map((form) => {
                        return {
                            ...form,
                            _this: this,
                            flipped: false,
                            _formSound: undefined,
                            _translationSound: undefined,
                            get formSound() {
                                if (this._formSound === undefined) {
                                    this._formSound = this._this.createSound(form.pollyUrl);
                                }
                                this._formSound.then((howl) => {
                                    if (howl.state() === 'unloaded' && (this._this.loadingProgress >= this._this.loadingProgressMax || !this.safeMode)) {
                                        howl.load()
                                    }
                                })
                                return this._formSound
                            },
                            get translationSound() {
                                if (this._translationSound === undefined) {
                                    this._translationSound = this._this.createSound(form.trPollyUrl)
                                }
                                this._translationSound.then((howl) => {
                                    if (howl.state() === 'unloaded' && (this._this.loadingProgress >= this._this.loadingProgressMax || !this.safeMode)) {
                                        howl.load()
                                    }
                                })
                                return this._translationSound
                            }
                        }
                    }), d.packets, d.verbListHTML];
                },

                createSound: async function (url) {
                    this.loadingProgressMax = this.loadingProgressMax + 1
                    return new Promise((resolve, reject) => {
                        const howl = new Howl({
                            src: [url],
                            preload: true,
                            loop: false,
                            buffer: false,
                            html5: false,
                            onload: () => {
                                this.loadingProgress = this.loadingProgress + 1;
                                resolve(howl)
                            },
                            onloaderror: () => resolve(silence)
                        })
                    })
                },

                playSound: async function (soundPromise) {
                    if ((soundPromise === undefined) || (soundPromise === null)) {
                        return 0;
                    }
                    return new Promise((resolve, reject) => {
                        soundPromise.then((howl) => {
                            if (howl.state() === 'unloaded') {
                                howl.load()
                            }
                            this.playingSound = howl;
                            howl.once('end', () => {
                                console.log(`getting duration of a sound: ${howl}`);
                                resolve(howl.duration());
                                if (this.safeMode) {
                                    howl.unload()
                                }
                                soundPromise = undefined
                            })
                            console.log(`playing a sound: ${howl}`);
                            window.howl_to_play = howl;
                            howl.play()
                        })
                    })
                },

                getCurrentParticipeCard: function () {
                    if (this.type === this.TYPE_LISTENING) {
                        return this.cards.findIndex(card => card.tense === TENSE_PARTICIPE_PASSE)
                    } else {
                        return this.cardsRepeat.findIndex(card => card.tense === TENSE_PARTICIPE_PASSE)
                    }
                },

                getCurrentCard: function () {
                    if (this.type === LISTENING) {
                        return this.cards[this.currentCard]
                    } else {
                        return this.cardsRepeat[this.currentCard]
                    }
                },

                getCardTimeouts: function (i, cardList) {
                    let afterVerbTimeout, afterTenseTimeout,
                        beforeTranslationTimeout

                    if (!this.showParticipe
                        && (this.isCardInfinitive(cardList[i], cardList) || this.isCardInfinitive(this.getNextCard(i)))
                    ) {
                        afterVerbTimeout = this.timeoutInfinitive
                    } else if (!this.showParticipe) {
                        if (this.type === LISTENING) {
                            afterVerbTimeout = this.timeoutWordsListening
                        } else {
                            afterVerbTimeout = this.timeoutWordsChecking
                        }
                    } else {
                        if (this.type === LISTENING) {
                            afterVerbTimeout = this.participeTimeoutWordsListening;
                        } else {
                            afterVerbTimeout = this.participeTimeoutWordsChecking;
                        }
                    }
                    afterVerbTimeout *= 1000

                    afterTenseTimeout = this.timeoutTense * 1000

                    if (!this.showParticipe
                        && (cardList[i].isTranslation || this.type === CHECKING)
                    ) {
                        beforeTranslationTimeout = this.timeoutTranslation
                    } else if (!this.showParticipe && this.isCardInfinitive(cardList[i]) && this.type === LISTENING && this.translateInfinitives) {
                        beforeTranslationTimeout = this.timeoutInfinitiveTranslation
                    } else if (!this.showParticipe && this.type === LISTENING) {
                        beforeTranslationTimeout = 0
                    } else if (this.showParticipe && this.type === LISTENING) {
                        beforeTranslationTimeout = this.participeTimeoutTranslation
                    } else if (this.showParticipe && this.type === CHECKING) {
                        beforeTranslationTimeout = this.timeoutTranslation
                    }
                    beforeTranslationTimeout *= 1000
                    console.log(`After Verb: ${afterVerbTimeout / 1000}\nBefore Translation: ${beforeTranslationTimeout / 1000}`)
                    return [afterVerbTimeout, beforeTranslationTimeout]
                },

                showCurrentCard: function () {
                    this.card = this.getCurrentCard()
                },

                loadParticipeCards: function () {
                    this.pause = true
                    this.flipAllCards()
                    if (!this.showParticipe) {
                        this.showParticipe = true;
                        this.currentCard = this.getCurrentParticipeCard()
                        this.progress = this.currentCard * this.progressStep
                    } else {
                        this.showParticipe = false;
                        this.currentCard = 0;
                        this.progress = 0;
                    }
                    this.showCurrentCard()
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

                getParticipesCountByLesson: function (lessonNumber) {
                    let packet = this.packets.find(packet => packet.lessonNumber === lessonNumber);
                    if (packet) {
                        return packet.participesCount
                    } else {
                        return null
                    }
                },

                flipAllCards: function () {
                    this.cards.forEach(card => card.flipped = false);
                    this.cardsRepeat.forEach(card => card.flipped = false);
                },

                numWord: function (n, words) {
                    let value = Math.abs(n) % 100;
                    let num = value % 10;
                    if (value > 10 && value < 20) return words[2];
                    if (num > 1 && num < 5) return words[1];
                    if (num === 1) return words[0];
                    return words[2];
                },

                getVerbOrForm: function () {
                    return this.card.verb ? this.card.verb : this.card.form;
                },

                message: function (n) {
                    if (n >= 5) {
                        return 'пяти'
                    } else if (n === 4) {
                        return 'четырёх'
                    } else if (n === 3) {
                        return 'трёх'
                    } else if (n === 2) {
                        return 'двух'
                    } else if (n === 1) {
                        return 'одного'
                    }
                },

                lessonsAbove: function (lessons) {
                    if (lessons === undefined) lessons = 5
                    let fromLessonNumber = this.lessonNumber - lessons
                    let dif = this.lessonNumber - fromLessonNumber
                    return `${this.message(lessons + dif)} уроков`
                },

                loadMoreName: function (nLessons, verbsCount, participesCount) {
                    return `${this.message(nLessons)} ${this.numWord(nLessons, ['урока', 'уроков', 'уроков'])}
                 (+${verbsCount} ${this.numWord(verbsCount, ['глагол', 'глагола', 'глаголов'])} 
                 ${participesCount > 0 ? `а так же ${participesCount} ${this.numWord(participesCount, ['причастие', 'причастия', 'причастий'])}` : ""})`
                    //`(+${participesCount} ${this.numWord(participesCount, ['причастие', 'причастия', 'причастий'])})`
                },

                verbsList: function () {

                },

                isLoadMoreSelected: function () {
                    return this.loadMoreValue !== 0
                },

                getLoadMoreOptions: function () {
                    let options = []
                    let lessons = 0
                    let verbsCount = 0
                    let participesCount = 0
                    while (lessons < 5) {
                        lessons += 1
                        let currentLessonVerbsCount = this.getVerbsCountByLesson(this.lessonNumber - lessons)
                        let currentLessonParticipesCount = this.getParticipesCountByLesson(this.lessonNumber - lessons)
                        if (!currentLessonVerbsCount) {
                            continue
                        }
                        participesCount += currentLessonParticipesCount
                        verbsCount += currentLessonVerbsCount
                        options.push({
                            loadMore: lessons,
                            name: this.loadMoreName(lessons, verbsCount, participesCount)
                        })
                    }
                    return options
                },

                initRepeatCards: function () {
                    this.cardsRepeat = this.cards.slice().map((i) => {
                        return {
                            ...i,
                            _this: this,
                            form: i.translation,
                            verb: i.translation,
                            translation: i.verb || i.form,
                            pollyUrl: i.trPollyUrl,
                            trPollyUrl: i.pollyUrl,
                            _formSound: undefined,
                            _translationSound: undefined,
                            get formSound() {
                                if (this._formSound === undefined) {
                                    this._formSound = this._this.createSound(this.pollyUrl)
                                }
                                this._formSound.then((howl) => {
                                    if (howl.state() === 'unloaded' && (this._this.loadingProgress >= this._this.loadingProgressMax || !this.safeMode)) {
                                        howl.load()
                                    }
                                })
                                return this._formSound
                            },
                            get translationSound() {
                                if (this._translationSound === undefined) {
                                    this._translationSound = this._this.createSound(this.trPollyUrl)
                                }
                                this._translationSound.then((howl) => {
                                    if (howl.state() === 'unloaded' && (this._this.loadingProgress >= this._this.loadingProgressMax || !this.safeMode)) {
                                        howl.load()
                                    }
                                })
                                return this._translationSound
                            }
                        }
                    })
                    this.shuffle(this.cardsRepeat)
                },

                loadInitCards: async function () {
                    if (!this.pause) {
                        this.pause = true;
                    }
                    let values = await this.loadCards(currentPacketID);
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
                    let moreLessons = this.loadMoreValue
                    if (moreLessons === null) {
                        moreLessons = undefined
                    }
                    let values = await this.loadCards(currentPacketID, moreLessons);
                    this.cards = values[0];
                    this.packets = values[1];
                    this.init();
                    this.startOver();
                    this.moreVerbsLoaded = true;
                },

                startOver: function () {
                    this.progress = 0;
                    this.currentCard = 0;
                    this.flipAllCards();
                },

                filterCard: function (card) {
                    return (this.type === CHECKING || card.isShownOnDrill)
                        && (!this.showParticipe || card.tense === TENSE_PARTICIPE_PASSE)
                        && (this.showNegative || card.type === CARD_TYPE_AFFIRMATIVE)

                },

                getNextCard: function (i = undefined, cardsList = undefined) {
                    if (i === undefined) {
                        i = this.currentCard
                    }
                    if (cardsList === undefined) {
                        cardsList = (this.type === this.TYPE_LISTENING) ? this.cards : this.cardsRepeat
                    }
                    let nextCard = cardsList.slice(i + 1).find(card => this.filterCard(card))
                    if (nextCard === undefined) {
                        nextCard = cardsList.find(card => this.filterCard(card))
                    }
                    return nextCard
                },

                isCardInfinitive: function (card) {
                    return 'forms' in card
                },

                isCurrentCardInfinitive: function () {
                    return this.isCardInfinitive(this.card)
                },

                nextCardAfterCurrentIsInfinitive: function () {
                    return 'forms' in this.getNextCard()
                },


                togglePause: function () {
                    if (this.loadingProgress < this.loadingProgressMax && this.safeMode) {
                        return
                    }
                    this.pause = !this.pause;
                    if (this.pause === false) {
                        if (this.type === LISTENING) {
                            this.playCards('togglePause');
                        } else {
                            this.playCards('togglePause');
                        }
                    } else {
                        if (this.playing) {
                            this.playing = false;
                            this.playingSound = undefined
                        }
                    }
                },

                toggleType: function () {

                    if (this.type === LISTENING) {
                        this.type = CHECKING
                    } else {
                        this.type = LISTENING
                    }
                    this.pause = true;
                    this.progress = 0;
                    this.currentCard = 0

                    if (this.showParticipe) {
                        this.currentCard = this.getCurrentParticipeCard()
                    }
                    this.showCurrentCard()

                    if (this.type === LISTENING) {
                        this.progressStep = 100 / (this.cards.length - 1);
                    } else {
                        this.progressStep = 100 / this.cards.length;
                    }
                },

                shuffle: function (array) {
                    array.sort(() => Math.random() - 0.5);
                },

                playNextCard: function () {
                    if (!this.pause && !this.playing) {
                        this.currentCard++;
                        if (this.currentCard === (this.cards.length)) {
                            this.currentCard = 0
                            this.progress = 0
                            this.flipAllCards()
                            if (this.type === CHECKING) {
                                this.shuffle(this.cardsRepeat)
                            }
                        }
                        if (!this.pause) {
                            console.log(`Playing next card: ${this.currentCard}`)
                            this.playCards('playNextCard');
                        }
                    }
                },

                getTenseUrl: function () {
                    let tense = this.card.tense
                    return TENSE_AUDIO_URLS[tense]
                },

                getTenseSound: function () {
                    return TENSE_SOUNDS[this.card.tense]
                },

                getLastCard: function (i = undefined, cardList = undefined) {
                    if (i === undefined) i = this.currentCard
                    if (cardList === undefined) cardList = this.type === LISTENING ? this.cards : this.cardsRepeat
                    let lastCard = cardList.slice(0, i).reverse().find(card => this.filterCard(card))
                    if (lastCard === undefined) lastCard = null
                    return lastCard
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

                play: async function (sound) {
                    if (!this.pause) {
                        return this.playSound(sound)
                    } else {
                        return 0
                    }
                },

                playCards: function (source = 'none') {
                    if (this.playing) {
                        return
                    }
                    if (this.progress < 100) {
                        this.progress += this.progressStep;
                    }

                    if (!this.showNegative && this.getCurrentCard().type === CARD_TYPE_NEGATIVE) {
                        console.log('Playing next card')
                        return this.playNextCard()
                    }
                    if (!this.showParticipe && this.getCurrentCard().tense === TENSE_PARTICIPE_PASSE) {
                        console.log('Playing next card')
                        return this.playNextCard()
                    } else if (this.showParticipe && this.getCurrentCard().tense !== TENSE_PARTICIPE_PASSE) {
                        console.log('Playing next card')
                        return this.playNextCard()
                    }
                    if (!this.pause) {
                        playingInstance = playingInstance + 1
                        console.log(`playing instance: ${playingInstance}, source: ${source}`)
                        this.getCurrentCard().flipped = false;
                        this.showCurrentCard()
                        if (this.card.isShownOnDrill || this.type === CHECKING) {
                            this.playing = true;
                            let _this = this;
                            let afterVerbTimeout;
                            let beforeTranslationTimeout;
                            [afterVerbTimeout, beforeTranslationTimeout] = this.getCardTimeouts(this.currentCard, this.type === LISTENING ? this.cards : this.cardsRepeat)
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
                            this.play(tenseSound).then(function (tenseDuration) {
                                if (_this.pause) {
                                    _this.playing = false;
                                    return
                                }
                                tenseDuration = 0
                                console.log('tense timeout: ' + (tenseDuration + afterTenseTimeout))
                                setTimeout(function () {
                                    _this.play(_this.card.formSound).then(function (verbDuration) {
                                        if (_this.pause) {
                                            _this.playing = false;
                                            return
                                        }
                                        verbDuration = 0;
                                        setTimeout(function () {
                                            let translationUrl = undefined;
                                            let translationSound = undefined;
                                            if (_this.card.tense === TENSE_PARTICIPE_PASSE
                                                || (_this.type === LISTENING && _this.card.isTranslation)
                                                || _this.type === CHECKING
                                                || (_this.translateInfinitives && _this.isCurrentCardInfinitive() && _this.type === LISTENING)
                                            ) {
                                                translationSound = _this.card.translationSound
                                                _this.card.flipped = true;
                                            }
                                            if (_this.pause) {
                                                _this.playing = false;
                                                _this.card.flipped = false
                                                return
                                            }
                                            _this.play(translationSound).then(function (translationDuration) {
                                                if (_this.pause) {
                                                    _this.playing = false;
                                                    _this.card.flipped = false
                                                    return
                                                }
                                                translationDuration = 0;
                                                let timeout = 0;
                                                if (_this.isCurrentCardInfinitive()) {
                                                }
                                                setTimeout(function () {
                                                    console.log('word timeout: ' + (afterVerbTimeout + translationDuration))
                                                    setTimeout(function () {
                                                        _this.playing = false;
                                                        if (!_this.pause) {
                                                            console.log('Playing next card')
                                                            return _this.playNextCard()
                                                        }
                                                    }, afterVerbTimeout + translationDuration);
                                                }.bind(_this), translationDuration)
                                            }.bind(_this))
                                        }, beforeTranslationTimeout + verbDuration);
                                    }.bind(_this));
                                }, tenseDuration + afterTenseTimeout)
                            }.bind(_this))
                        } else {
                            console.log('Playing next card')
                            return this.playNextCard()
                        }
                    }
                }
            }
        })
    } else {
        setTimeout(vueIsLoaded, 1000)
    }
}

(async function () {
    vueIsLoaded()
})();
