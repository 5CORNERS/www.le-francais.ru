from django.contrib.auth.models import AbstractUser, UserManager
from django.core.mail import send_mail
from django.db import models
from django.utils.translation import ugettext_lazy as _


class CustomUserManager(UserManager):
	def _create_user(self, username, email, password, **extra_fields):
		"""
		Creates and saves a User with the given username, email and password.
		"""
		if not email:
			raise ValueError('Email is required')
		if not username:
			raise ValueError('The given username must be set')
		email = self.normalize_email(email)
		username = self.model.normalize_username(username)
		user = self.model(username=username, email=email, **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_user(self, username, email, password=None, **extra_fields):
		extra_fields.setdefault('is_staff', False)
		extra_fields.setdefault('is_superuser', False)
		return self._create_user(username, email, password, **extra_fields)


class User(AbstractUser):
	email = models.EmailField(
		verbose_name='email address',
		max_length=255,
		unique=True,
		error_messages={
			'unique': _("A user with that email already exists."),
		},
	)
	username = models.CharField(
		max_length=32,
		verbose_name='nickname',
		help_text='Your forum nickname (can be changed later)',
		unique=True,
		error_messages={
			'unique': _("Пользователь с таким именем уже зарегестрирован."),
		},
	)

	from django.core.serializers.json import DjangoJSONEncoder
	from django.contrib.postgres.fields import JSONField

	used_usernames = JSONField(encoder=DjangoJSONEncoder, default=list)

	objects = CustomUserManager()
	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username']

	def __str__(self):
		return self.username

	def email_user(self, subject, message, from_email=None, **kwargs):
		"""
		Sends an email to this User.
		"""
		send_mail(subject, message, from_email, [self.email], **kwargs)

	def nick_name(self):
		return self.username

	def get_username(self):
		return self.username


from django.db import models


class UsedUsernames(models.Model):
	user = models.ForeignKey('User', on_delete=models.CASCADE)
	used_username = models.CharField(max_length=32)
	change_datetime = models.DateTimeField()