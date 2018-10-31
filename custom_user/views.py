from django.views import View
from django.shortcuts import HttpResponse


class SawMessageView(View):
	def post(self, request):
		user = request.user
		if request.POST['saw_message'] == 'true':
			user.saw_message = True
			user.save()
			return HttpResponse(b'OK', status=200)
