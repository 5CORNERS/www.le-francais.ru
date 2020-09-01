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
                return this.cards[this.currentCard + 1]
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

            playCards: function (array) {
                if (!this.pause) {
                    _this = this;

                    this.progress += this.progressStep;

                    var verb_timeout;
                    if (this.nextCardIsInfinitive() || this.isInfinitive()){
                        verb_timeout = this.timeoutInfinitive
                        console.log('infinitive')
                    }else{
                        console.log('not-infinitive')
                        verb_timeout = this.timeoutDefault
                    }

                    if (this.card.isShownOnDrill || this.type == CHECKING) {
                        playSound(this.card.pollyUrl).then(function (duration) {
                            duration *= 1000;
                            var translateTimeout;
                            if (this.card.isTranslation || this.type == CHECKING) {
                                translateTimeout = this.timeoutTranslation;
                            } else if (this.type == LISTENING) {
                                translateTimeout = 0;
                            }
                            console.log('translate timeout: '+Number(translateTimeout))
                            setTimeout(function () {

                                if ((_this.type == LISTENING && _this.card.isTranslation) || _this.type == CHECKING) {
                                    _this.card.flipped = !_this.card.flipped;
                                    playSound(_this.card.trPollyUrl).then(function (trDuration) {
                                        trDuration *= 1000;
                                        console.log('word timeout: '+ (Number(_this.timeoutDefault) + Number(verb_timeout) + Number(trDuration)))
                                        setTimeout(function () {
                                            _this.currentCard++;
                                            _this.card = array[_this.currentCard];
                                            _this.playCards(array);
                                        }, Number(_this.timeoutDefault) + Number(verb_timeout) + Number(trDuration));
                                    }.bind(_this));
                                } else {
                                    console.log('word timeout: '+ (Number(_this.timeoutDefault) + Number(verb_timeout) + Number(duration)))
                                    setTimeout(function () {
                                        _this.currentCard++;
                                        _this.card = array[_this.currentCard];
                                        _this.playCards(array);
                                    }, Number(_this.timeoutDefault) + Number(verb_timeout) + Number(duration));
                                }
                            }, Number(translateTimeout));
                        }.bind(this));
                    } else {
                        _this.currentCard++;
                        _this.card = array[_this.currentCard];
                        _this.playCards(array);
                    }
                }
            }
        }
    });

})();
