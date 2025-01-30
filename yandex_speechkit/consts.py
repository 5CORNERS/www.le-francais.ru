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

VOICES_CHOICES = [
    ('alena', 'alena'),
    ('filipp', 'filipp')
]

EMOTION_CHOICES = [
    ('neutral','neutral',),
    ('whisper','whisper',),
    ('friendly','friendly',),
    ('good','good',),
    ('strict','strict',),
    ('evil','evil'),
]

FORMAT_MP3 = 'mp3'

FORMAT_CHOICES = [
    ('lpcm', 'lpcm',),
    ('oggopus', 'oggopus',),
    (FORMAT_MP3, 'mp3',),
]

FILE_EXTENSION = {
    FORMAT_MP3: 'mp3',
    'lpcm': 'wav',
    'oggopus': 'ogg',
}

SAMPLE_RATE_CHOICES = [
    ('8000','8000',),
    ('16000','16000',),
    ('48000','48000',),
]

FILES_LE_FRANCAIS_PATH = '/speechkit/'