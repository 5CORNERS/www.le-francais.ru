ENGINE_STANDARD = 'standard'
ENGINE_NEURAL = 'neural'
ENGINE_LONG_FORM = 'long-form'
ENGINE_GENERATIVE = 'generative'

DEFAULT_ENGINE = ENGINE_NEURAL

ENGINE_CHOICES = [
	(ENGINE_STANDARD, 'Standard'),
	(ENGINE_NEURAL, 'Neural'),
	(ENGINE_LONG_FORM, 'Long form'),
	(ENGINE_GENERATIVE, 'Generative'),
]

OUTPUT_FORMAT_JSON = 'json'
OUTPUT_FORMAT_MP3 = 'mp3'
OUTPUT_FORMAT_OGG = 'ogg_vorbis'
OUTPUT_FORMAT_PCM = 'pcm'

OUTPUT_FORMATS = (
	(OUTPUT_FORMAT_JSON, 'json'),
	(OUTPUT_FORMAT_MP3, 'mp3'),
	(OUTPUT_FORMAT_OGG, 'ogg_vorbis'),
	(OUTPUT_FORMAT_PCM, 'pcm'),
)

FILE_EXTENSION = {
	OUTPUT_FORMAT_MP3: 'mp3',
	OUTPUT_FORMAT_OGG: 'ogg',
	OUTPUT_FORMAT_PCM: 'wav',
}

SAMPLE_RATE_8000 = '8000'
SAMPLE_RATE_16000 = '16000'
SAMPLE_RATE_22050 = '22050'

SAMPLE_RATES = (
	(SAMPLE_RATE_8000, '8000'),
	(SAMPLE_RATE_16000, '16000'),
	(SAMPLE_RATE_22050, '22050'),
)

SPEECH_MARK_TYPE_SENTENCE = 'sentence'
SPEECH_MARK_TYPE_SSML = 'ssml'
SPEECH_MARK_TYPE_VISEME = 'viseme'
SPEECH_MARK_TYPE_WORD = 'word'

SPEECH_MARK_TYPES = (
	(SPEECH_MARK_TYPE_SENTENCE, 'sentence'),
	(SPEECH_MARK_TYPE_SSML, 'ssml'),
	(SPEECH_MARK_TYPE_VISEME, 'viseme'),
	(SPEECH_MARK_TYPE_WORD, 'word'),
)

TEXT_TYPE_SSML = 'ssml'
TEXT_TYPE_TEXT = 'text'

TEXT_TYPES = (
	(TEXT_TYPE_SSML, 'ssml'),
	(TEXT_TYPE_TEXT, 'text')
)

# French voices
VOICE_ID_LEA = 'Lea'
VOICE_ID_CELINE = 'Celine'
VOICE_ID_MATHIEU = 'Mathieu'
VOICE_ID_REMI = 'Remi'

# Russian voices
VOICE_ID_MAXIM = 'Maxim'
VOICE_ID_TATYANA = 'Tatyana'

VOICE_IDS = (
	(VOICE_ID_LEA, 'lea'),
	(VOICE_ID_REMI, 'remi'),
	(VOICE_ID_CELINE, 'celine'),
	(VOICE_ID_MATHIEU, 'matthieu'),
	(VOICE_ID_MAXIM, 'maxim'),
	(VOICE_ID_TATYANA, 'tatyana'),
)

LANGUAGE_CODE_FR = 'fr-FR'
LANGUAGE_CODE_RU = 'ru-RU'

LANGUAGE_CODES = (
	(LANGUAGE_CODE_FR, 'French'),
	(LANGUAGE_CODE_RU, 'Russian'),
)

SCHEDULED = "scheduled"
IN_PROGRESS = "inProgress"
COMPLETED = "completed"
FAILED = "failed"

TASK_STATUSES = (
	(SCHEDULED, "scheduled"),
	(IN_PROGRESS, "inProgress"),
	(COMPLETED, "completed"),
	(FAILED, "failed"),
)

REQUIRED = (
	'OutputFormat',
	'OutputS3BucketName',
	'Text',
	'VoiceId',
)

PARAMS = {
	'output_format': 'OutputFormat',
	'output_s3_bucket_name': 'OutputS3BucketName',
	'output_s3_key_prefix': 'OutputS3KeyPrefix',
	'text': 'Text',
	'voice_id': 'VoiceId',
	'lexicon_names': 'LexiconNames',
	'sample_rate': 'SampleRate',
	'speech_mark_types': 'SpeechMarkTypes',
	'text_type': 'TextType',
	'language_code': 'LanguageCode',
	'engine': 'Engine'
}

RESPONSE_PARAMS = {
	'TaskId': 'task_id',
	'TaskStatus': 'task_status',
	'OutputUri': 'url',
	'CreationTime': 'datetime_creation',
	'RequestCharacters': 'request_characters',
	'OutputFormat': 'output_format',
	'SampleRate': 'sample_rate',
	'TextType': 'text_type',
	'VoiceId': 'voice_id',
	'LanguageCode': 'language_code',
}
