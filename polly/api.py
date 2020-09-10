import boto3
from django.conf import settings
from botocore.exceptions import ClientError
from .const import RESPONSE_PARAMS


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

	def get_audio_stream(self, polly_task):
		data = polly_task.to_dict()  # type: dict
		response = self.client.synthesize_speech(**data)
		return response['AudioStream']

	def start_task(self, polly_task, wait=False, save=True):
		"""
		:param polly_task: PollyAudio
		:param wait: wait while task is complited (or failed)
		:param save: save object before return
		:return: dict {'AudioStream': StreamingBody(),'ContentType': 'string','RequestCharacters': 123}
		"""
		data = polly_task.to_dict()  # type: dict
		data['OutputS3BucketName'] = self.output_s3_bucket_name
		data['OutputS3KeyPrefix'] = self.output_s3_key_prefix
		response = self.client.start_speech_synthesis_task(**data)
		polly_task.task_id, polly_task.task_status, polly_task.url = (
			response['SynthesisTask']['TaskId'],
			response['SynthesisTask']['TaskStatus'],
			response['SynthesisTask']['OutputUri'])
		while wait and polly_task.task_status not in ('completed', 'failed'):
			polly_task.task_status = self.client.get_speech_synthesis_task(TaskId=polly_task.task_id)['SynthesisTask']['TaskStatus']
		if save:
			polly_task.save()
		return polly_task

	def bulk_start_task(self, audio_list: list):
		scheduled_audio = []
		for c, polly_audio in enumerate(audio_list):
			print('\rSending request... {0} in {1}'.format(c+1, len(audio_list)), end='')
			new_task = self.start_task(polly_audio, wait=False, save=False)
			scheduled_audio.append(new_task)
		print()
		for c, polly_audio in enumerate(scheduled_audio):
			print('\rSaving url... {0} in {1}'.format(c+1, len(scheduled_audio)), end='')
			polly_audio.save()
		print()

	def update_task(self, polly_audio):
		try:
			response = self.client.get_speech_synthesis_task(TaskId=polly_audio.task_id)
		except ClientError as e:
			if e.response['Error']['Code'] == 'SynthesisTaskNotFoundException':
				self.start_task(polly_task=polly_audio, wait=False, save=True)
				return None
		for response_key, field in RESPONSE_PARAMS.items():
			setattr(polly_audio, field, response['SynthesisTask'][response_key])
		polly_audio.save()
