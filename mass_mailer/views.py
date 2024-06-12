from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http.response import HttpResponseNotFound, HttpResponse
from django.urls import reverse

from mass_mailer.models import Profile



def unsubscribe(request, key):
	# TODO: add form with template
	try:
		profile = Profile.objects.get(key=key)
		profile.subscribed = False
		profile.save()
		return HttpResponse(f'Ваш адрес {profile.user.email} был отписан от всех рассылок. Чтобы подписаться обратно, перейдите по адресу {request.build_absolute_uri(reverse("mass_mailer:subscribe", kwargs={"key":key}))}', status=200, content_type='text/plain; charset=UTF-8')
	except Profile.DoesNotExist:
		return HttpResponseNotFound()

def subscribe(request, key):
	try:
		profile = Profile.objects.get(key=key)
		profile.subscribed = True
		profile.save()
		return HttpResponse(f'Ваш адрес {profile.user.email} был подписан на рассылки.', status=200, content_type='text/plain; charset=UTF-8')
	except Profile.DoesNotExist:
		return HttpResponseNotFound()

@login_required
def subscribe_user(request):
	profile = Profile.objects.get(user=request.user)
	profile.subscribed = True
	profile.save()
	return redirect(request.GET.get('next', '/'))