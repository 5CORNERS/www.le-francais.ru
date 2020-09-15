(async function () {

    var url_string = window.location.href;
    var url = new URL(url_string);
    var $dictApp = $('#dict-app')
    const currentPacketID = $dictApp.data('lesson-number');
    const showNegativeDefault = $dictApp.data('show-negative')
    const translateInfinitivesDefault = $dictApp.data('translate-infinitives')

    const response = await fetch('/dictionary/verbs/' + currentPacketID);
    const data = await response.json();
    const LISTENING = 0;
    const CHECKING = 1;

    const CARD_TYPE_AFFIRMATIVE = 0
    const CARD_TYPE_NEGATIVE = 1

    var loadCards = async function (packetId, more_lessons=undefined){
        let verbs = []
        let r
        if (more_lessons !== undefined && typeof more_lessons === 'number') {
            r = await fetch(`/dictionary/verbs/${packetId}/${more_lessons}`);
        }else{
            r = await fetch(`/dictionary/verbs/${packetId}/`)
        }
        let d = await r.json();
        d.verbs.forEach(function (form){
            verbs = verbs.concat(form)
            verbs = verbs.concat(form.forms)
        });

        return verbs.map((form) => {
            return {...form, flipped: false}
        });
    }

    const getAudionDuration = (url) => {
        return new Promise((resolve, reject) => {
            const audio = new Audio(url);
            audio.onloadedmetadata = () => {
                resolve(audio.duration);
            }
        });
    }

    async function playSound(url) {
        audio = new Audio(url);
        audio.play();
        duration = await getAudionDuration(url);
        return duration;
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
            TYPE_LISTENING: LISTENING,
            TYPE_CHECKING: CHECKING,
            moreVerbsLoaded: false,
        },

        async mounted() {
            this.cards = await loadCards(currentPacketID);
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

            initRepeatCards: function () {
                this.cardsRepeat = this.cards.slice().map((i) => {
                    return {
                        ...i,
                        form: i.translation,
                        verb: i.translation,
                        translation: i.verb || i.form,
                        pollyUrl: i.trPollyUrl,
                        trPollyUrl: i.pollyUrl
                    }
                })
                this.shuffle(this.cardsRepeat)
            },

            loadMoreCards: async function () {
                if (!this.pause){
                    this.pause = true;
                }
                this.cards = await loadCards(currentPacketID, 5);
                this.init();
                this.startOver();
                this.moreVerbsLoaded = true;
            },

            startOver: function(){
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
                    if (this.type === CHECKING){
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

            playCards: function () {
                if (!this.pause) {
                    _this = this;

                    if (this.progress < 100) {
                        this.progress += this.progressStep;
                    }

                    if (!this.showNegative && this.card.type === CARD_TYPE_NEGATIVE) {
                        return this.playNextCard()
                    }

                    if (this.card.isShownOnDrill || this.type === CHECKING) {
                        var verb_timeout;
                        if (this.nextCardIsInfinitive() || this.isInfinitive()) {
                            // текущая или следующая карточка -- инфинитив
                            verb_timeout = this.timeoutInfinitive * 1000
                            console.log('infinitive')
                        } else {
                            // текущая и следующая карточка -- не инфинитив
                            console.log('not-infinitive')
                            if (this.type === LISTENING) {
                                verb_timeout = this.timeoutWordsListening * 1000;
                            } else {
                                verb_timeout = this.timeoutWordsChecking * 1000;
                            }
                        }
                        // карточка показывается в режиме прослушивания или режим проверки
                        playSound(this.card.pollyUrl).then(function (duration) {
                            duration *= 1000;
                            var translateTimeout;
                            if (this.card.isTranslation || this.type === CHECKING) {
                                // карточка подлежит переводу или режим проверки
                                translateTimeout = this.timeoutTranslation * 1000 + duration;
                            } else if (this.translateInfinitives && this.isInfinitive() && this.type === LISTENING) {
                                translateTimeout = this.timeoutInfinitiveTranslation * 1000 + duration;
                            } else if (this.type === LISTENING) {
                                // режим прослушивания и карточка не подлежит переводу
                                translateTimeout = 0;
                            }
                            console.log('translate timeout: ' + translateTimeout)
                            setTimeout(function () {

                                if ((_this.type === LISTENING && _this.card.isTranslation) || _this.type === CHECKING || (_this.translateInfinitives && _this.isInfinitive() && _this.type === LISTENING)) {
                                    // Карточка подлежит переводу и установлен режим прослушивания или режим проверки
                                    _this.card.flipped = !_this.card.flipped;
                                    playSound(_this.card.trPollyUrl).then(function (trDuration) {
                                        trDuration *= 1000;
                                        console.log('word timeout: ' + (Number(verb_timeout) + Number(trDuration)))
                                        setTimeout(function () {
                                            _this.playNextCard()
                                        }, Number(verb_timeout) + Number(trDuration));
                                    }.bind(_this));
                                } else {
                                    // Карточка не подлежит переводу и  установлен режим прослушивания
                                    console.log('word timeout: ' + (Number(verb_timeout) + Number(duration)))
                                    setTimeout(function () {
                                        _this.playNextCard()
                                    }, Number(verb_timeout) + Number(duration));
                                }
                            }, Number(translateTimeout));
                        }.bind(this));
                    } else {
                        // карточки не показывается в режиме прослушивания и режим прослушивания
                        _this.playNextCard()
                    }
                }
            }
        }
    });

})();
