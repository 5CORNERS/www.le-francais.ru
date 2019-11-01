from django.utils.translation import ugettext_lazy as _

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
PARTOFSPEECH_PARTIC = 'partic'
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
    (PARTOFSPEECH_PARTIC, 'Partic'),
]

INITIAL_E_FACTOR = 2.5
FIRST_REPETITION_DELTA = 1
SECOND_REPETITION_DELTA = 6

USER_IS_NOT_AUTHENTICATED_MESSAGE = _('User is not authenticated')
PACKET_DOES_NOT_EXIST_MESSAGE = _('Packet does not exist')
PACKET_IS_NOT_ADDED_MESSAGE = _('Packet is not added')
LESSON_IS_NOT_ACTIVATED_MESSAGE = _('Lesson is not activated')
WORD_DOES_NOT_EXIST_MESSAGE = _('Word does not exist')
TOO_EARLY_MESSAGE = _(
    'You trying to repeat word, which repetition date has not come yet')
NO_LEFT_CUPS_MESSAGE = _('There are no cups left')
