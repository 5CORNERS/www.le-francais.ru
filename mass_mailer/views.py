from django.shortcuts import render
from django.http.response import HttpResponseNotFound, HttpResponse
from mass_mailer.models import Profile


def unsubscribe(request, key):
	try:
		profile = Profile.objects.get(key=key)
		profile.subscribed = False
		profile.save()
		return HttpResponse(f'Ваш адрес {profile.user.email} был отписан от всех рассылок.', status=200, content_type='text/plain')
	except Profile.DoesNotExist:
		return HttpResponseNotFound
