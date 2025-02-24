def is_posting_permitted(user, post):
    if user.recaptcha3_score < 0.3:
        return False
    return (
            user.days_since_joined() > 1
            or user.posts.filter(on_moderation=False).count() > 1
            or user.is_superuser
    )
