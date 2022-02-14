from django.shortcuts import render
from django.http.response import HttpResponseNotFound, HttpResponse
from mass_mailer.models import Profile



def unsubscribe(request, key):
	# TODO: add form with template
	try:
		profile = Profile.objects.get(key=key)
		profile.subscribed = False
		profile.save()
		return HttpResponse(f'Ваш адрес {profile.user.email} был отписан от всех рассылок.', status=200, content_type='text/plain; charset=UTF-8')
	except Profile.DoesNotExist:
		return HttpResponseNotFound()

def subscribe(request, key):
	try:
		profile = Profile.objects.get(key=key)
		profile.subscribed = True
		profile.save()
		return HttpResponse(f'Ваш адрес {profile.user.email} был подписан на рассылки', status=200, content_type='text/plain; charset=UTF-8')
	except Profile.DoesNotExist:
		return HttpResponseNotFound()
