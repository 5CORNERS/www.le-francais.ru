from django.contrib import admin
from django.conf.urls import url
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import format_html

from .models import User
from .forms import UserAddCupsForm


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
	# change_list_template = 'custom_user/admin/change_list.html'
	exclude = ['password']
	list_display = ['user_actions', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'must_pay', 'saw_message', '_cup_amount', '_cup_credit', '_low_price', 'is_active']
	readonly_fields = ['user_actions']
	list_filter = ['date_joined']
	search_fields = ['username', 'email', 'first_name', 'last_name']

	def get_urls(self):
		urls = super(CustomUserAdmin, self).get_urls()
		custom_urls = [
			url(
				r'^(?P<user_id>[0-9]+)/add_cups/$',
				self.admin_site.admin_view(self.add_cups),
				name='user_add_cups',
			),
		]
		return custom_urls + urls

	def user_actions(self, obj):
		return format_html(
			'<a class="button" href="{}">Add Cups</a>',
			reverse('admin:user_add_cups', args=[obj.pk])
		)

	user_actions.short_description = 'User Actions'
	user_actions.allow_tags = True

	# TODO: add request user to log this action
	def add_cups(self, request, user_id):
		if request.method == 'POST':
			form = UserAddCupsForm(request.POST)
			if not form.is_valid():
				self.message_user(request, 'Form is not valid')
				return redirect('admin:custom_user_user_changelist')
			user = User.objects.get(id=user_id)
			user.add_cups(form.cleaned_data['cups'])
			self.message_user(request, 'Cups was added')
			return redirect('admin:custom_user_user_changelist')
		form = UserAddCupsForm()
		context = dict(
			self.admin_site.each_context(request),
			form=form,
		)
		return render(request, 'custom_user/admin/add_cups_form.html', context)
