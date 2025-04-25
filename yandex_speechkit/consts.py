PARAMS = {
    'text': 'text',
    'ssml': 'ssml',
    'lang': 'lang',
    'voice': 'voice',
    'speed': 'speed',
    'emotion': 'emotion',
    'format': 'format',
    'sample_rate': 'sampleRateHertz',
}

LANGUAGE_RU = 'ru-RU'

LANGUAGE_CHOICES = [
    (LANGUAGE_RU, 'Russian')
]

VOICE_ALENA = 'alena'
VOICE_FILIPP = 'filipp'

VOICES_CHOICES = [
    (VOICE_ALENA, 'alena'),
    (VOICE_FILIPP, 'filipp')
]

EMOTION_NEUTRAL = 'neutral'
EMOTION_WHISPER = 'whisper'
EMOTION_FRIENDLY = 'friendly'
EMOTION_GOOD = 'good'
EMOTION_STRICT = 'strict'
EMOTION_EVIL = 'evil'

EMOTION_CHOICES = [
    (EMOTION_NEUTRAL, 'neutral',),
    (EMOTION_WHISPER, 'whisper',),
    (EMOTION_FRIENDLY, 'friendly',),
    (EMOTION_GOOD, 'good',),
    (EMOTION_STRICT, 'strict',),
    (EMOTION_EVIL, 'evil'),
]

FORMAT_MP3 = 'mp3'
FORMAT_LPCM = 'lpcm'
FORMAT_OGGOPUS = 'oggopus'

FORMAT_CHOICES = [
    (FORMAT_LPCM, 'lpcm',),
    (FORMAT_OGGOPUS, 'oggopus',),
    (FORMAT_MP3, 'mp3',),
]

DEFAULT_VOICE_FEMALE = VOICE_ALENA
DEFAULT_EMOTION_FEMALE = EMOTION_NEUTRAL
DEFAULT_VOICE_MALE = VOICE_FILIPP
DEFAULT_EMOTION_MALE = EMOTION_NEUTRAL
DEFAULT_FORMAT = FORMAT_LPCM

FILE_EXTENSION = {
    FORMAT_MP3: 'mp3',
    FORMAT_LPCM: 'wav',
    FORMAT_OGGOPUS: 'ogg',
}

SAMPLE_RATE_8000 = '8000'
SAMPLE_RATE_16000 = '16000'
SAMPLE_RATE_48000 = '48000'

SAMPLE_RATE_CHOICES = [
    (SAMPLE_RATE_8000, '8000',),
    (SAMPLE_RATE_16000, '16000',),
    (SAMPLE_RATE_48000, '48000',),
]

FILES_LE_FRANCAIS_PATH = 'dictionary/speechkit/'
