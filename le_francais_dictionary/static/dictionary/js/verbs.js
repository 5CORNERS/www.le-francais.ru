(async function () {

    var url_string = window.location.href;
    var url = new URL(url_string);
    const lesson = $('#dict-app').data('lesson-number');

    const response = await fetch('/dictionary/verbs/' + lesson);
    const data = await response.json();
    const LISTENING = 0;
    const CHECKING = 1;

    var verbs = [];
    data.verbs.forEach(function (form) {
        verbs = verbs.concat(form)
        verbs = verbs.concat(form.forms)
    });

//const cards = verbs.map((form) => {return {...form, verb: form.form, flipped: false }});
    const cards = verbs.map((form) => {
        return {...form, flipped: false}
    });

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
            cards: cards,
            cardsRepeat: cards.slice().map((i) => {
                return {
                    ...i,
                    form: i.translation,
                    verb: i.translation,
                    translation: i.verb || i.form,
                    pollyUrl: i.trPollyUrl,
                    trPollyUrl: i.pollyUrl
                }
            }),
            //cardsRepeat — тоже самое что и cards, но перевод и слово поменяны местами
            card: cards[0],
            currentCard: 0,
            translation: cards[0]['translation'],
            progress: 0,
            progressStep: 0,
            timeoutDefault: 1000, // время между словами
            timeoutTranslation: 2000, // время между переводом
            timeoutInfinitive: 2000, // время до и после инфинитива
            type: LISTENING,
            pause: true,
            error: false,
        },

        mounted() {
            this.progressStep = 100 / (verbs.length - 1);
            this.shuffle(this.cardsRepeat);
            console.log(this.cards);
        },

        methods: {

            getNextCard: function () {
                if (this.type === LISTENING) {
                    let nextCard = this.cards.slice(this.currentCard+1).find(card => card.isShownOnDrill)
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
                if (this.pause == false) {
                    if (this.type == LISTENING) {
                        this.playCards(this.cards);
                    } else {
                        this.playCards(this.cardsRepeat);
                    }
                }
            },

            toggleType: function () {

                this.type = !this.type;
                this.progress = 0;
                this.currentCard = 0;
                this.pause = true;

                if (this.type == LISTENING) {
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
                }
                if (this.type === LISTENING){
                    this.card = this.cards[this.currentCard];
                }else{
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

                    if (this.card.isShownOnDrill || this.type == CHECKING) {
                        var verb_timeout;
                        if (this.nextCardIsInfinitive() || this.isInfinitive()) {
                            // текущая или следующая карточка -- инфинитив
                            verb_timeout = this.timeoutInfinitive
                            console.log('infinitive')
                        } else {
                            // текущая и следующая карточка -- не инфинитив
                            console.log('not-infinitive')
                            verb_timeout = this.timeoutDefault
                        }
                        // карточка показывается в режиме прослушивания или режим проверки
                        playSound(this.card.pollyUrl).then(function (duration) {
                            duration *= 1000;
                            var translateTimeout;
                            if (this.card.isTranslation || this.type == CHECKING) {
                                // карточка подлежит переводу или режим проверки
                                translateTimeout = Number(this.timeoutTranslation) + duration;
                            } else if (this.type == LISTENING) {
                                // режим прослушивания и карточка не подлежит переводу
                                translateTimeout = 0;
                            }
                            console.log('translate timeout: ' + Number(translateTimeout))
                            setTimeout(function () {

                                if ((_this.type == LISTENING && _this.card.isTranslation) || _this.type == CHECKING) {
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
