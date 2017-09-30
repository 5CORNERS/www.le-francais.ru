import pickle
from datetime import datetime
from io import BytesIO

import pandas as pd
import pytz
from PIL import Image
from django.core.management import BaseCommand
from requests import get

from custom_user.models import User
from pybb.models import Category, Forum, Topic, Post


# import ggroups2pybbm.forum_classes


# from drupango.models import (Node as DrupalNode, Comments as DrupalComments, )
# from html2bbcode import HTML2BBCode

class Command(BaseCommand):
	help = 'Migration phpbb3 to pybbm'

	def handle(self, *args, **options):
		with open('forum/unique_nicknames.csv', 'rb') as file:
			df = pd.read_csv(file)
			table = df.to_dict()
			new_dict = {}
			for i in range(len(table['Email'])):
				new_dict[table['Email'][i]] = table['Nickname'][i]
			unique_nicknames = new_dict
		with open('forum/oldforum1.dat', 'rb') as file:
			old_forum = pickle.load(file)
			self.stdout.write(u'Import forum')
			self.arnaud_fix(old_forum.users)
		with open('forum/out-of-forum_emails_list.txt', 'r', encoding='utf-8') as f:
			list = []
			for line in f:
				list.append(line.rstrip('\n'))
			out_of_forum = list
		with open('forum/Forum_users_resolved—new_approach_fixed.csv', encoding='utf-8') as file:
			df = pd.read_csv(file)
			table = df.to_dict()
			new_dict = {}
			for i in range(len(table['Email'])):
				new_dict[table['Email'][i]] = table['Forumname or Gmail_name unique'][i]
			new_approach = new_dict
		# self.print_table(old_forum.users)
		# self.migrate_users(old_forum, unique_nicknames)
		self.fix_users(new_approach, old_forum.users)

	# self.get_picasaweb(old_forum.users)
	# self.get_picasaweb(out_of_forum)

	# self.migrate_forums()
	# self.migrate_topics(old_forum)

	def migrate_users(self, old_forum, unique_nicknames: dict):
		count = 0
		for user in old_forum.users:
			count += 1
			if user.username == None:
				try:
					user.username = unique_nicknames[user.mail]
				except:
					user.username = "user" + str(count)
			user.password = User.objects.make_random_password(length=8)
			try:
				new_user, created = User.objects.get_or_create(
					email=user.mail, username=user.username
				)
			except:
				try:
					new_user, created = User.objects.get_or_create(
						email=user.mail, username=unique_nicknames[user.mail]
					)
				except:
					new_user, created = User.objects.get_or_create(
						email=user.mail, username=user.username + '_'
					)
					old_forum.users[old_forum.users.index(user)].username += '_'
			if created:
				new_user.set_password(user.password)
				new_user.is_active = True
				new_user.date_joined = user.registration_date
				new_user.last_login = user.last_visit_date
				self.stdout.write(
					'New user:	' + str(user.mail) + '	' + str(user.username) + '	' + str(user.password))
				new_user.save()
			else:
				new_user.set_password(user.password)
				self.stdout.write('User already exist:	' + str(user.mail) + '	' + str(user.username) + '\t' + str(
					user.password))
				new_user.save()

	def fix_users(self, new_users: dict, old_users):
		count = 1
		for user in old_users:
			print('User ' + str(count) + ' of 654 ' + user.mail, end=' ')
			count += 1
			try:
				new_username = new_users[user.mail]
			except:
				print("\nERROR!!! Couldn't find approach user with this email: " + user.mail)
				continue
			try:
				django_user = User.objects.get(email=user.mail)
			except:
				print("\nERROR!!! Couldn't find django user with this email: " + user.mail)
				continue
			if django_user.username != new_username:
				print(django_user.username + ' changed to ' + new_username)
				django_user.username = new_username
				django_user.save()
			else:
				print("has the same username: " + django_user.username)

	def get_picasaweb(self, users):
		url = 'http://picasaweb.google.com/data/entry/api/user/'
		params = {'alt': 'json'}
		self.stdout.write('Email\tGoogle User Name\tImage ID')
		skip = True
		for user in users:
			try:
				json = get(url + user, params).json()
			except:
				self.stdout.write(user + '\t' + 'Unresolved' + '\t' + 'Unresolved')
				continue
			json_entry = json['entry']
			nickname = json_entry['author'][0]['name']['$t']
			image_id = json_entry['gphoto$user']['$t']
			image_url = json_entry['gphoto$thumbnail']['$t']
			self.stdout.write(user + '\t' + nickname + '\t' + image_id)
			image = Image.open(BytesIO(get(image_url).content)).convert('RGB')
			image.save('forum/avatars/' + image_id + '.jpg')

	def migrate_forums(self):
		to_create = [
			("О том, о сём", 'o_tom_o_sem'),
			("Не могу молчать!", 'ne_mogu_molchat')
		]
		for forum in to_create:
			new_forum, created = Forum.objects.get_or_create(
				name=forum[0],
				slug=forum[1],
				category=Category.objects.get(slug='old_forum'))
			if created:
				self.stdout.write(u'Created forum:  ' + forum[0])
			else:
				self.stdout.write(u'Forum already exist:  ' + forum[0])

	def migrate_topics(self, old_forum):
		for topic in old_forum.topics:
			if topic.name == "Города и веси":
				goroda_i_vesi(topic)
				continue
			new_topic, created = Topic.objects.get_or_create(
				forum=Forum.objects.get(name=topic.category),
				name=topic.name,
				user=User.objects.get(email=get_firs_post(topic.posts).user.mail),
				created=get_firs_post(topic.posts).date,
			)
			if created:
				self.stdout.write(u'Created topic:	' + topic.name + '	' + topic.id)
			else:
				self.stdout.write(u'Topic already exist:	' + topic.name + '	' + topic.id)
			self.migrate_posts(topic.posts, new_topic)

	def migrate_posts(self, posts, to_topic):
		for post in posts:
			new_post, created = Post.objects.get_or_create(
				topic=to_topic,
				user=User.objects.get(email=post.user.mail),
				created=post.date,
				body=post.body
			)
			if created:
				new_post.save()
				self.stdout.write(u'\tCreated post:	' + post.subject + '	' + post.id)
			else:
				self.stdout.write(u'\tPost already exist:	' + post.subject + '\t' + post.id)

	def arnaud_fix(self, users):
		for user in users:
			if user.mail == 'bidibulle25@gmail.com':
				i = users.index(user)
				users[i].mail = 'bidibulle025@gmail.com'

	def print_table(self, users):
		self.stdout.write('Email\tUsername\tRegistration\tLastVisit')
		for user in users:
			self.stdout.write(user.mail + '\t' + str(user.username) + '\t' + user.registration_date.strftime(
				'%Y/%m/%d') + '\t' + user.last_visit_date.strftime('%Y/%m/%d'))


def print_posts(old_forum):
	for topic in old_forum.topics:
		print("Topic:\t" + topic.name + '\t' + topic.category)
		for post in topic.posts:
			print("\tPost:\t" + post.subject)


def goroda_i_vesi(topic):
	try:
		new_topic = Topic.objects.get(name='Города и веси')
		print(u'Topic already exist:	' + topic.name + '	' + topic.id)
	except:
		new_topic = Topic.objects.create(
			forum=Forum.objects.get(name="О том, о сём"),
			name="Города и веси",
			user=User.objects.get(email=topic.posts[0].user.mail),
			created=get_firs_post(topic.posts).date
		)
		print(u'Created topic:	' + topic.name + '	' + topic.id)
	for post in topic.posts:
		new_post, created = Post.objects.get_or_create(
			topic=new_topic,
			user=User.objects.get(email=post.user.mail),
			created=post.date,
			body=post.body
		)
		if created:
			new_post.save()
			print(u'\tCreated post:	' + post.subject + '	' + post.id)
		else:
			print(u'\tPost already exist:	' + post.subject + '\t' + post.id)


def get_firs_post(posts):
	utc = pytz.UTC
	min = utc.localize(datetime.max)
	for post in posts:
		if post.date < min:
			min = post.date
			firs_post = post
		else:
			continue
	return firs_post
