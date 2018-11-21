from django.views import View
from django.shortcuts import HttpResponse
import json


class SawMessageView(View):
	def dispatch(self, request, *args, **kwargs):
		return super(SawMessageView, self).dispatch(request, *args, **kwargs)

	def post(self, request):
		user = request.user
		if request.POST['action'] == 'make_true':
			user.saw_message = True
			user.save()
			return HttpResponse(b'OK', status=200)
		elif request.POST['action'] == 'get_state':
			return HttpResponse(json.dumps(user.saw_message), content_type='application/json', status=200)
		else:
			return HttpResponse(status=400)
