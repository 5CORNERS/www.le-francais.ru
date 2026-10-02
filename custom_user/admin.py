from django.contrib import admin
from django.conf.urls import url
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import format_html

from .models import User
from .forms import UserAddCupsForm


class EmailStatusFilter(admin.SimpleListFilter):
	title = 'Email Verification / Auth'
	parameter_name = 'email_status'

	def lookups(self, request, model_admin):
		return (
			('oauth', 'OAuth Registered'),
			('verified', 'Email Verified'),
			('unverified', 'Unverified'),
		)

	def queryset(self, request, queryset):
		if self.value() == 'oauth':
			return queryset.filter(social_auth__isnull=False).distinct()
		if self.value() == 'verified':
			return queryset.filter(emailaddress__verified=True, social_auth__isnull=True).distinct()
		if self.value() == 'unverified':
			return queryset.exclude(emailaddress__verified=True).exclude(social_auth__isnull=False).distinct()
		return queryset


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
	# change_list_template = 'custom_user/admin/change_list.html'
	exclude = ['password']
	list_display = ['user_actions', 'username', 'email', 'email_status', 'first_name', 'last_name', 'date_joined', '_cup_amount', 'saw_message', 'country_name', 'city', '_low_price', 'is_active', 'must_pay', '_cup_credit']
	list_display_links = ['username']
	readonly_fields = ['user_actions']
	list_filter = ['date_joined', EmailStatusFilter]
	search_fields = ['username', 'email', 'first_name', 'last_name']

	def get_queryset(self, request):
		return super(CustomUserAdmin, self).get_queryset(request).prefetch_related('emailaddress_set', 'social_auth')

	def email_status(self, obj):
		social_accounts = list(obj.social_auth.all())
		if social_accounts:
			providers = ', '.join(sa.provider for sa in social_accounts)
			return format_html('<span style="color: #2e7d32; font-weight: bold;">&#10004; OAuth ({})</span>', providers)

		is_verified = any(ea.verified for ea in obj.emailaddress_set.all())
		if is_verified:
			return format_html('<span style="color: #2e7d32; font-weight: bold;">&#10004; Verified</span>')

		return format_html('<span style="color: #c62828;">&#10008; Unverified</span>')

	email_status.short_description = 'Email Status'
	email_status.admin_order_field = 'emailaddress__verified'

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
