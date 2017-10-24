with open("C:\\Users\\ilia.dumov\\PycharmProjects\\www.le-francais.ru\\home\\static\\css\\pybb.css", 'r') as f:
	for line in f:
		if line[0] == '@':
			a=0
		if not line[0] == '\n' and line[-2] == '{' and not line[0] == '@' and not (line == '    from {\n' or line == '    to {\n'):
			rules = line.split(',')
			new_line = '.block-pybb ' + rules[0].lstrip('    ')
			if line[0:4] == '    ':
				new_line = '    ' + new_line
			if len(rules) > 1:
				for num in range(1, len(rules)):
					new_rule = '.block-pybb' + rules[num]
					new_line = new_line + ', ' + new_rule
			print(new_line, end='')
		else:
			new_line = line
			print(new_line, end='')
