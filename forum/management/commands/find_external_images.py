import re
import urllib.request
from pathlib import Path

from django.core.management import BaseCommand
from django.db.models.signals import post_save

from pybb.models import Post, Topic

from pandas import read_csv


class Command(BaseCommand):
	help = "First run: store images. Second run: replace links."
	def handle(self, *args, **options):
		s = ''
		s += "Post ID,Image Link,Filename\n"
		table = read_csv('forum/dat/images/list.txt')
		from pybb.signals import topic_saved
		# FIXME: we should have specific signals to send notifications to topic/forum subscribers
		# but for now, we must connect / disconnect the callback
		post_save.disconnect(topic_saved, sender=Topic)
		for i in range(len(table)):
			post_id = int(table['Post ID'][i])
			old_link = table['Image Link'][i]
			filename = table['Filename'][i]
			new_link = 'https://files.le-francais.ru/images/forum/' + filename
			post = Post.objects.get(id=post_id)
			post.body = post.body.replace(old_link, new_link)
			post.save()
		post_save.connect(topic_saved, sender=Topic)

		for post in Post.objects.all():
			for link in re.findall('\((((http://)|(https://))(.+?\.(png|jpeg|gif)))', post.body):
				file_name = link[0].split('//')[1]
				file_name = re.sub('/', '+', file_name)
				if link[0].startswith('https://files.le-francais.ru'):
					continue
				s += str(post.id) + ',' + link[0] + ',' + file_name[:] + '\n'
				image_string = 'https://www.le-francais.ru' + str(post.get_absolute_url()) + '\t' + link[0]
				file = Path('forum/dat/images/' + file_name[:])
				if not file.is_file():
					try:
						opener= urllib.request.build_opener()
						opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
						urllib.request.install_opener(opener)
						urllib.request.urlretrieve(link[0], 'forum/dat/images/' + file_name[:])
						print(image_string)
					except:
						print(image_string + ' UrlRetrieve Error')
				else:
					print(image_string + ' File already exist')
		open('forum/dat/images/list.txt', 'w').write(s)

