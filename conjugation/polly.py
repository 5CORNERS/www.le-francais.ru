import boto3
from django.conf import settings

OUTPUT_FORMAT_JSON = 'json'
OUTPUT_FORMAT_MP3 = 'mp3'
OUTPUT_FORMAT_OGG = 'ogg_vorbis'
OUTPUT_FORMAT_PCM = 'pcm'

SAMPLE_RATE_8000 = '8000'
SAMPLE_RATE_16000 = '16000'
SAMPLE_RATE_22050 = '22050'

SPEECH_MARK_TYPE_SENTENCE = 'sentence'
SPEECH_MARK_TYPE_SSML = 'ssml'
SPEECH_MARK_TYPE_VISEME = 'viseme'
SPEECH_MARK_TYPE_WORD = 'word'

TEXT_TYPE_SSML = 'ssml'
TEXT_TYPE_TEXT = 'text'

# French voices
VOICE_ID_LEA = 'Lea'
VOICE_ID_CELINE = 'Celine'
VOICE_ID_MATHIEU = 'Mathieu'

# Russian voices
VOICE_ID_MAXIM = 'Maxim'
VOICE_ID_TATYANA = 'Tatyana'

LANGUAGE_CODE_FR = 'fr-FR'
LANGUAGE_CODE_RU = 'ru-RU'


class PollySpeech:
	def __init__(self, ):
		pass


class PolllyAPI:
	_access_key_id = None
	_secret_access_key = None

	_output_s3_bucket_name = None,
	_output_s3_key_prefix = None,

	__client = None

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
		return self._output_s3_bucket_name

	@property
	def output_s3_key_prefix(self) -> str:
		return self._output_s3_key_prefix

	@property
	def client(self):
		if not self.__client:
			self.__client = boto3.Session(self.access_key_id, self.secret_access_key).client('Polly')
		return self.__client

	def start_task(self, polly_speech:PollySpeech,**kwargs) -> dict:
		"""
		:key !OutputFormat:    'json' | 'mp3' | 'ogg_vorbis' | 'pcm'
		:key !Text:            text itself
		:key !VoiceId:         'Lea' | 'Celine' | 'Mathieu' | 'Maxim' | 'Tatyana'
		:key LexiconNames:    ['string',]
		:key SampleRate:      '8000' | '16000' | '22050'
		:key SpeechMarkTypes: ['sentence' | 'ssml' | 'viseme' | 'word']
		:key TextType:        'ssml' | 'text'
		:key LeanguageCode:   'fr-FR' | 'ru-RU'
		:return: dict {'AudioStream': StreamingBody(),'ContentType': 'string','RequestCharacters': 123}
		"""
		return self.client.synthesize_speech(**kwargs)
