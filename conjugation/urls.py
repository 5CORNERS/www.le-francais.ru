from django.conf.urls import url

from . import views

urlpatterns = [
	url(
		r'verbs_autocomplete/.{0,50}?/$',
		views.get_autocomplete_list,
		name='autocomplete'),
	url(
		r'fr_verb_autocomplete/$',
		views.FrVerbAutocomplete.as_view(),
		name='autocomplete_fr_verb'),
	url(
		r't_tag_autocomplete/$',
		views.TranslationTagAutocomplete.as_view(create_field='tag'),
		name='autocomplete_t_tag'),
	url(
		r'fr_tag_autocomplete/$',
		views.FrTagAutocomplete.as_view(create_field='tag'),
		name='autocomplete_fr_tag'),
	# url(
	# 	r'translations/$',
	# 	views.ListTranslationView.as_view(),
	# 	name='translation_list'),
	# url(
	# 	r'translations/(?P<pk>[0-9]+)/$',
	# 	views.TranslationDetailView.as_view(),
	# 	name='translation_detail'),
	url(
		r'translations/(?P<pk>[0-9]+)/edit/$',
		views.TranslationUpdateView.as_view(),
		name='translation_update'
	),
	url(
		r'search/$',
		views.search,
		name='search'),
    url(r"polly/$", views.get_polly_audio_link, name='polly'),
    url(r"(?P<feminin>feminin_)?(?P<se>se_|s_)?(?P<verb>[-'a-zÀ-ÿ]{1,30})(?P<homonym>_2)?/$", views.verb_page, name='verb'),
    url(r'^$', views.index, name='index'),
]
