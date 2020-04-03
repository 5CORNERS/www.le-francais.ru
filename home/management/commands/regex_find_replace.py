import re

from django.core.management import BaseCommand

from home.management.commands._private import set_block, query_yes_no
from home.models import LessonPage


class Command(BaseCommand):
	def add_arguments(self, parser):
		parser.add_argument(
			'-p',
			dest='pattern',
			type=str,
			required=True,
		)
		parser.add_argument(
			'-r',
			dest='replace',
			required=True,
		)
		parser.add_argument(
			'-f', '--fields',
			nargs='*',
			dest='fields',
			default=['body'],
		)

	def handle(self, *args, **options):
		pattern = re.compile(options['pattern'], flags=re.DOTALL)
		replace_to = options['replace']
		update_pages = []
		for page in LessonPage.objects.all():
			page_was_changed = False
			found_strings = []
			for field_name in options['fields']:
				field = getattr(page, field_name)
				for i in range(len(field.stream_data)):
					block = field.__getitem__(i)
					if block.block_type != 'html':
						continue
					new_block_value, replaced_count = re.subn(
						pattern=pattern,
						repl=replace_to,
						string=block.value,
					)
					if replaced_count > 0:
						for match in re.finditer(pattern, block.value):
							found_strings.append({
								'field': field_name,
								'block': i,
								'to_replace': f"...{block.value[match.start()-10:match.start()]}||{match.group(0)}||{block.value[match.end():match.end()+10]}...",
								'new_value': re.sub(match.re, replace_to, f"...{block.value[match.start()-10:match.start()]}||{match.group(0)}||{block.value[match.end():match.end()+10]}...")
							})
						block.value = new_block_value
						set_block(i, block, field)
						setattr(page, field_name, field)
						page_was_changed = True
			if page_was_changed:
				print(f"{page}")
				for found_str in found_strings:
					print(f"\tField: {found_str['field']}\n"
					      f"\tFound: {found_str['to_replace']}\n"
					      f"\tReplaceTo: {found_str['new_value']}\n")
				update_pages.append(page)
		if query_yes_no("Save revisions of updated pages?", default='no'):
			for page in update_pages:
				print(f'Saving draft {page}')
				page.save_revision()
			if query_yes_no("Publish new revisions?", default='yes'):
				for page in update_pages:
					print(f'Publishing {page}')
					page.get_latest_revision().publish()
			else:
				for page in update_pages:
					revision = page.get_latest_revision()
					print(f'Deleting revision {revision}')
					revision.delete()

