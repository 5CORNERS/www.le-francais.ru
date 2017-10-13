# from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from django.core.exceptions import ValidationError
# from django.utils.translation import ugettext_lazy as _
# from registration import validators
# from registration.forms import RegistrationForm
#
# from .models import User
#
#
# class MyCustomUserForm(RegistrationForm):
# 	"""
# 	Form for registering a new user account.
#
# 	Validates that the requested username is not already in use, and
# 	requires the password to be entered twice to catch typos.
#
# 	Subclasses should feel free to add any additional validation they
# 	need, but should take care when overriding ``save()`` to respect
# 	the ``commit=False`` argument, as several registration workflows
# 	will make use of it to create inactive user accounts.
#
# 	"""
# 	# Explicitly declared here because Django's default
# 	# UserCreationForm, which we subclass, does not require this field
# 	# but workflows in django-registration which involve explicit
# 	# activation step do require it. If you need an optional email
# 	# field, simply subclass and declare the field not required.
# 	email = forms.EmailField(
# 		help_text=_(u'email address'),
# 		required=True
# 	)
# 	username = forms.CharField(required=True )
#
# 	class Meta(UserCreationForm.Meta):
# 		model = User
# 		fields = [
# 			User.USERNAME_FIELD,
# 			'username',
# 			'password1',
# 			'password2'
# 		]
# 		required_css_class = 'required'
#
# 	def clean(self):
# 		"""
# 		Apply the reserved-name validator to the username.
#
# 		"""
# 		# This is done in clean() because Django does not currently
# 		# have a non-ugly way to just add a validator to an existing
# 		# field on a form when subclassing; the standard approach is
# 		# to re-declare the entire field in order to specify the
# 		# validator. That's not an option here because we're dealing
# 		# with the user model and we don't know -- given custom users
# 		# -- how to declare the username field.
# 		#
# 		# So defining clean() and attaching the error message (if
# 		# there is one) to the username field is the least-ugly
# 		# solution.
# 		username_value = self.cleaned_data.get(User.USERNAME_FIELD)
# 		if username_value is not None:
# 			try:
# 				if hasattr(self, 'reserved_names'):
# 					reserved_names = self.reserved_names
# 				else:
# 					reserved_names = validators.DEFAULT_RESERVED_NAMES
# 				validator = validators.ReservedNameValidator(
# 					reserved_names=reserved_names
# 				)
# 				validator(username_value)
# 			except ValidationError as v:
# 				self.add_error(User.USERNAME_FIELD, v)
# 		super(RegistrationForm, self).clean()
