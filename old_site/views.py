from django.shortcuts import render


def get_page_template(request, page):
	return render(request, page)