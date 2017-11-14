from django.core.management import BaseCommand
from home.models import IndexReviews
import pandas as pd

FILE = 'forum/dat/testimonials.csv'

class Command(BaseCommand)
	def handle(self, *args, **options):
		with open(FILE) as f:
			df = pd.read_csv(f)
			table= df.to_dict()
		new_dict = []
		for i in range(len(table['Text'])):
			new_dict = {"text":table['Text'][i], "signature":table["Signature"][i], "url":table["Url"][i]}
		for review in new_dict:
			print(new_dict )



