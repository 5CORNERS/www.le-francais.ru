from conjugation.models import Template

for template in Template.objects.all():
	ending = template.new_data['conditional']['present']['p'][4]['i']
	if ending is None:
		continue
	if isinstance(ending, list):
		is_list = True
	else:
		is_list = False
	ending = str(ending).replace('i<b>ez</b>', '<b>iez</b>')
	ending = eval(ending) if is_list else ending
	template.new_data['conditional']['present']['p'][4]['i'] = ending
	template.save()
	print(template.new_data['conditional']['present']['p'][4])
