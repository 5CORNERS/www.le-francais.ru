import datetime
from dateutil.parser import parse
from dateutil import tz

class OldForum():
    def __init__(self):
        self.topics = []
        self.users = []

    def add_topic(self, topic):
        self.topics.append(topic)

    def add_user(self, user):
        if not self.user_exists(user):
            self.users.append(user)

    def user_exists(self, user_):
        for user in self.users:
            if user_.mail == user.mail:
                return user
        return False


class OldUser():
    def __init__(self, username, mail):
        self.username = username
        self.mail = mail
        self.registration_date = datetime.datetime(2017,6,1,tzinfo=tz.tzoffset(None,7200))
        self.last_visit_date = datetime.datetime(2010,2,10,tzinfo=tz.tzoffset(None,0000))

        from xkcdpass import xkcd_password as xp

        wordfile = xp.locate_wordfile()
        mywords = xp.generate_wordlist(wordfile=wordfile, min_length=5, max_length=8)

        self.password = xp.generate_xkcdpassword(mywords,1)

    def set_dates(self, date):
        if date < self.registration_date :
            self.registration_date = date
        if date > self.last_visit_date:
            self.last_visit_date = date


class OldTopic():
    def __init__(self):
        self.name = str()
        self.posts = []
        self.category = str()
        self.id = str()

    def add_post(self, post):
        self.posts.append(post)


class OldPost():
    def __init__(self, user, date, subject, body):
        self.user = user
        self.date = date
        self.subject = subject
        self.body = body
        self.id = str()
