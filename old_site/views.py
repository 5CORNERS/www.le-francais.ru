from django.shortcuts import render


def get_page_template(request, page):
	return render(request, page)

def open_old_site_iframe(request):
	return render(request, 'old_site.html')