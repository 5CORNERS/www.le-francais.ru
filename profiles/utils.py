def check_user(user, post):
    if user.days_since_joined():
	    return True
    if user.posts.filter(on_moderation=False).count() > 1:
	    return True
    if user.is_superuser:
        return True
    return False
