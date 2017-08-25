from django.core.management import BaseCommand

import re
from home.models import LessonPage, PageWithSidebar
from ._private import set_block


class Command(BaseCommand):
	def handle(self, *args, **options):
		# self.replace('''<td style="border-top-width:0pt;border-right-width:0pt;border-bottom-width:0pt;border-left-width:0pt;vertical-align:top;padding-top:4pt;padding-right:4pt;padding-bottom:4pt;padding-left:4pt;width:174px;height:20px">
         #      <p style="margin:0in;font-family:Verdana;font-size:10.0pt;text-align:center">
         #       Masculin
         #      </p>
         #     </td>
         #     <td style="border-top-width:0pt;border-right-width:0pt;border-bottom-width:0pt;border-left-width:0pt;vertical-align:top;padding-top:4pt;padding-right:4pt;padding-bottom:4pt;padding-left:4pt;width:178px;height:20px">
         #      <p style="margin:0in;font-family:Verdana;font-size:10.0pt;text-align:center">
         #       <span lang="ru">
         #        F
         #       </span>
         #       <span lang="en-US">
         #        éminin
         #       </span>
         #      </p>
         #     </td>''')
		self.span_fix(LessonPage)
		self.span_fix(PageWithSidebar)

	def span_fix(self, PageModel):
		for page in PageModel.objects.all():
			if page.lesson_number < 135:
				print('Lesson_number ' + str(page.lesson_number))
				for i in range(len(page.body.stream_data)):
					block = page.body.__getitem__(i)
					if block.block_type == 'html':
						new_value = self.replace(block.value)
						block.value = new_value
						set_block(i, block, page.body)
				page.save()

	def replace(self, new_value):
		# new_value = re.sub(r'\n(\s{0,})<span', '<span', value)
		# new_value = re.sub(r'\n(\s{0,})<\/span>', '</span>', new_value)
		# new_value = re.sub(r'\n(\s{0,})<a', '<a', new_value)
		# new_value = re.sub(r'\n(\s{0,})<\/a>', '</a>', new_value)
		# new_value = re.sub(r'\n(\s{0,})<p', '<p', new_value)
		# new_value = re.sub(r'\n(\s{0,})<\/p>', '</p>', new_value)
		# new_value = re.sub(r'\n(\s{0,})<\/b>', '</b>', new_value)
		# new_value = re.sub(r'\n(\s{0,})<\/i>', '</i>', new_value)
		new_value = re.sub(r'<b>\s{0,}\n\s{0,}', '<b>', new_value)
		new_value = re.sub(r'<i>\s{0,}\n\s{0,}', '<i>', new_value)

		# list = re.findall(r'<span[^>]{0,}>\s{0,}\n\s{0,}', new_value)
		# trim_list = []
		# for span in list:
		# 	new_span = re.sub(r'\s{0,}\n\s{0,}', '', span)
		# 	trim_list.append(new_span)
		# 	new_value = new_value.replace(span, new_span)
		# list = re.findall(r'<span[^>]{0,}>\s{0,}', new_value)
		# trim_list = []
		# for span in list:
		# 	new_span = span.strip()
		# 	trim_list.append(new_span)
		# 	new_value = new_value.replace(span, new_span)
		return new_value