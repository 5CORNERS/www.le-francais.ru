from django.test import RequestFactory

from custom_user.models import User
from home.models import LessonPage
from home.views import lesson_page_to_json

factory = RequestFactory()
request = factory.get('test')
request.user = User.objects.get(username='Anton Dumov')
for lesson in LessonPage.objects.all().order_by('lesson_number'):
	print(lesson.lesson_number, len([x for x in
	                                 lesson_page_to_json(lesson, True,
	                                                     User.objects.get(
		                                                     username='Anton Dumov'),
	                                                     request)['tabs'] if
	                                 x['value'] is not None]))

