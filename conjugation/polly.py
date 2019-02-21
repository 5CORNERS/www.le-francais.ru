import boto3
from django.conf import settings

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

# Russian voices
VOICE_ID_MAXIM = 'Maxim'
VOICE_ID_TATYANA = 'Tatyana'

VOICE_IDS = (
	(VOICE_ID_LEA, 'lea'),
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


class PollyAPI:
	_access_key_id = None
	_secret_access_key = None

	_output_s3_bucket_name = None,
	_output_s3_key_prefix = None,

	_client = None

	def __init__(self, access_key_id: str = None, secret_access_key: str = None, output_s3_bucket_name: str = None, output_s3_key_prefix: str = None):
		self._access_key_id = access_key_id
		self._secret_access_key = secret_access_key
		self._output_s3_bucket_name = output_s3_bucket_name
		self._output_s3_key_prefix = output_s3_key_prefix

	@property
	def access_key_id(self) -> str:
		if not self._access_key_id:
			self._access_key_id = settings.AWS_ACCESS_KEY_ID
		return self._access_key_id

	@property
	def secret_access_key(self) -> str:
		if not self._secret_access_key:
			self._secret_access_key = settings.AWS_SECRET_ACCESS_KEY
		return self._secret_access_key

	@property
	def output_s3_bucket_name(self) -> str:
		if not self._output_s3_bucket_name:
			self._output_s3_bucket_name = settings.POLLY_OUTPUT_S3_BUCKET_NAME
		return self._output_s3_bucket_name

	@property
	def output_s3_key_prefix(self) -> str:
		if not self._output_s3_key_prefix:
			self._output_s3_key_prefix = settings.POLLY_OUTPUT_S3_KEY_PREFIX
		return self._output_s3_key_prefix

	@property
	def client(self):
		if not self._client:
			self._client = boto3.Session(self.access_key_id, self.secret_access_key).client('polly', region_name=settings.AWS_S3_REGION_NAME)
		return self._client

	def start_task(self, polly_audio, wait=False, save=True):
		"""
		:param polly_audio: PollyAudio
		:param wait: wait while task is complited (or failed)
		:param save: save object before return
		:return: dict {'AudioStream': StreamingBody(),'ContentType': 'string','RequestCharacters': 123}
		"""
		data = polly_audio.to_dict()  # type: dict
		data['OutputS3BucketName'] = self.output_s3_bucket_name
		data['OutputS3KeyPrefix'] = self.output_s3_key_prefix
		response = self.client.start_speech_synthesis_task(**data)
		for response_key, field in RESPONSE_PARAMS.items():
			setattr(polly_audio, field, response['SynthesisTask'][response_key])
		while wait and polly_audio.task_status not in ('completed', 'failed'):
			polly_audio.task_status = self.client.get_speech_synthesis_task(TaskId=polly_audio.task_id)['SynthesisTask']['TaskStatus']
		if save:
			polly_audio.save()
		return polly_audio

	def bulk_start_task(self, audio_list: list):
		scheduled_audio = []
		for c, polly_audio in enumerate(audio_list):
			print('\rSending requests... {0} in {1}'.format(c+1, len(audio_list)), end='')
			new_task = self.start_task(polly_audio, wait=False, save=False)
			scheduled_audio.append(new_task)
		print()
		for c, polly_audio in enumerate(scheduled_audio):
			print('\rSaving urls... {0} in {1}'.format(c+1, len(scheduled_audio)), end='')
			polly_audio.save()
		print()

	def update_task(self, polly_audio):
		response = self.client.get_speech_synthesis_task(TaskId=polly_audio.task_id)
		for response_key, field in RESPONSE_PARAMS.items():
			setattr(polly_audio, field, response['SynthesisTask'][response_key])
		polly_audio.save()
