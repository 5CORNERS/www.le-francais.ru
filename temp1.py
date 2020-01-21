from notifications.models import Notification

for n in Notification.objects.filter(category="IR"):
	if not 'all' in n.data.keys():
		n.data['all'] = ''
		n.save()
		print(n)
