from pybb.permissions import DefaultPermissionHandler

class CustomPermissionHandler(DefaultPermissionHandler):
	def may_create_poll(self, user):
		if user.is_superuser or user.is_staff:
			return True
		return False