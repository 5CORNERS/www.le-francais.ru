def check_user(user, post):
    if user.is_superuser:
        return True
    if user.days_since_joined():
	    return True
    return False
