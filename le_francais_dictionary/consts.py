from django.utils.translation import ugettext_lazy as _

GRAMMATICAL_NUMBER_SINGULAR = 's'
GRAMMATICAL_NUMBER_PLURAL = 'pl'
GRAMMATICAL_NUMBER_SINGULAR_PLURAL = 's/pl'
GRAMMATICAL_NUMBER_COLLECTIVE = 'col'
GRAMMATICAL_NUMBER_CHOICES = [
    (GRAMMATICAL_NUMBER_SINGULAR, 'Singular'),
    (GRAMMATICAL_NUMBER_PLURAL, 'Plural'),
    (GRAMMATICAL_NUMBER_SINGULAR_PLURAL, 'Singular + Plural'),
    (GRAMMATICAL_NUMBER_COLLECTIVE, 'Collective')
]
GRAMMATICAL_NUMBER_LIST = [
    GRAMMATICAL_NUMBER_SINGULAR,
    GRAMMATICAL_NUMBER_PLURAL,
    GRAMMATICAL_NUMBER_SINGULAR_PLURAL,
    GRAMMATICAL_NUMBER_COLLECTIVE,
]

GENRE_FEMININE = 'f'
GENRE_MASCULINE = 'm'
GENRE_EPICENE = 'm/f'
GENRE_BOTH = 'm(f)'
GENRE_CHOICES = [
    (GENRE_FEMININE, 'Feminine'),
    (GENRE_MASCULINE, 'Masculine'),
    (GENRE_EPICENE, 'Epicene'),
    (GENRE_BOTH, 'Both in one')
]
PARTOFSPEECH_NOUN = 'nom'
PARTOFSPEECH_PRONOUN = 'pron'
PARTOFSPEECH_ADJECTIVE = 'adj'
PARTOFSPEECH_ADVERB = 'adv'
PARTOFSPEECH_CONJUNCTION = 'conj'
PARTOFSPEECH_VERB = 'verb'
PARTOFSPEECH_PREPOSITION = 'prep'
PARTOFSPEECH_INTERJECTION = 'interj'
PARTOFSPEECH_LOCUTION = 'loc'
PARTOFSPEECH_PHRASE = 'phrase'
PARTOFSPEECH_PARTICLE = 'partic'
PARTOFSPEECH_CHOICES = [
    (PARTOFSPEECH_NOUN, 'Noun'),
    (PARTOFSPEECH_PRONOUN, 'Pronoun'),
    (PARTOFSPEECH_ADJECTIVE, 'Adjective'),
    (PARTOFSPEECH_ADVERB, 'Adverb'),
    (PARTOFSPEECH_CONJUNCTION, 'Conjunction'),
    (PARTOFSPEECH_VERB, 'Verb'),
    (PARTOFSPEECH_PREPOSITION, 'Preposition'),
    (PARTOFSPEECH_INTERJECTION, 'Interjection'),
    (PARTOFSPEECH_LOCUTION, 'Locution'),
    (PARTOFSPEECH_PHRASE, 'Phrase'),
    (PARTOFSPEECH_PARTICLE, 'Particle'),
]

USER_IS_NOT_AUTHENTICATED_CODE = 10
PACKET_DOES_NOT_EXIST_CODE = 20
PACKET_IS_NOT_ADDED_CODE = 30
LESSON_IS_NOT_ACTIVATED_CODE = 40
WORD_DOES_NOT_EXIST_CODE = 50
TOO_EARLY_CODE = 60
NO_REPETITION_WORDS_CODE = 70
ALL_WORDS_ARE_IGNORED_CODE = 71
UNKNOWN_ERROR_CODE = 0

USER_IS_NOT_AUTHENTICATED_MESSAGE = _('User is not authenticated')
USER_IS_NOT_AUTHENTICATED_REPETITIONS_MESSAGE = 'Незарегистрированные пользователи не могут использовать метод интервальных повторений'
PACKET_DOES_NOT_EXIST_MESSAGE = _('Packet does not exist')
PACKET_IS_NOT_ADDED_MESSAGE = _('Packet is not added')
LESSON_IS_NOT_ACTIVATED_MESSAGE = _('Lesson is not activated')
WORD_DOES_NOT_EXIST_MESSAGE = _('Word does not exist')
TOO_EARLY_MESSAGE = _(
    'You trying to repeat word, which repetition date has not come yet')
NO_CUPS_MESSAGE = _('There are no cups left')
NO_REPETITION_WORDS_MESSAGE = 'На сегодня нет слов на повторение, но вы не расслабляйтесь :)'
ALL_WORDS_ARE_IGNORED_MESSAGE = 'В этом наборе карточек не осталось слов — они все исключены.'
TENSE_INDICATIVE_PRESENT = 0
TENSE_PASSE_COMPOSE = 1
TENSE_IMPERATIVE = 2
TENSE_INDICATIVE_IMPARFAIT = 3
TENSE_INDICATIVE_FUTURE = 4
TENSE_PARTICIPE_PASSE = 5
TENSE_CHOICES = [
	(TENSE_INDICATIVE_PRESENT, 'Indicatif Présent'),
	(TENSE_PASSE_COMPOSE, 'Passé Composé'),
	(TENSE_IMPERATIVE, 'Impératif Présent'),
	(TENSE_INDICATIVE_IMPARFAIT, 'Imparfait'),
	(TENSE_INDICATIVE_FUTURE, 'Futur Simple'),
	(TENSE_INDICATIVE_FUTURE, 'Futur simple'),
    (TENSE_PARTICIPE_PASSE, 'Participe Passé')
]
TYPE_AFFIRMATIVE = 0
TYPE_NEGATIVE = 1
TYPE_CHOICES = [
	(TYPE_AFFIRMATIVE, 'affirmative'),
	(TYPE_NEGATIVE, 'negative')
]
STAR_CHOICES = [
    ('None', 'Непройденные'),
    ('0@0',
     '<i class="far fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="far fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="far fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="far fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="far fa-star" aria-hidden="true" style="color: #ffc107;"></i>'),
    ('0@5',
     '<i class="fas fa-star-half-alt" aria-hidden="true" style="color: #ffc107;"></i><i class="far fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="far fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="far fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="far fa-star" aria-hidden="true" style="color: #ffc107;"></i>'),
    ('1@0',
     '<i class="fas fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="far fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="far fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="far fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="far fa-star" aria-hidden="true" style="color: #ffc107;"></i>'),
    ('1@5',
     '<i class="fas fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="fas fa-star-half-alt" aria-hidden="true" style="color: #ffc107;"></i><i class="far fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="far fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="far fa-star" aria-hidden="true" style="color: #ffc107;"></i>'),
    ('2@0',
     '<i class="fas fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="fas fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="far fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="far fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="far fa-star" aria-hidden="true" style="color: #ffc107;"></i>'),
    ('2@5',
     '<i class="fas fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="fas fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="fas fa-star-half-alt" aria-hidden="true" style="color: #ffc107;"></i><i class="far fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="far fa-star" aria-hidden="true" style="color: #ffc107;"></i>'),
    ('3@0',
     '<i class="fas fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="fas fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="fas fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="far fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="far fa-star" aria-hidden="true" style="color: #ffc107;"></i>'),
    ('3@5',
     '<i class="fas fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="fas fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="fas fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="fas fa-star-half-alt" aria-hidden="true" style="color: #ffc107;"></i><i class="far fa-star" aria-hidden="true" style="color: #ffc107;"></i>'),
    ('4@0',
     '<i class="fas fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="fas fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="fas fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="fas fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="far fa-star" aria-hidden="true" style="color: #ffc107;"></i>'),
    ('4@5',
     '<i class="fas fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="fas fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="fas fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="fas fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="fas fa-star-half-alt" aria-hidden="true" style="color: #ffc107;"></i>'),
    ('5@0',
     '<i class="fas fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="fas fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="fas fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="fas fa-star" aria-hidden="true" style="color: #ffc107;"></i><i class="fas fa-star" aria-hidden="true" style="color: #ffc107;"></i>'),
]
