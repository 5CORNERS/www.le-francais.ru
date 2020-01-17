to_rename = [(1185,"un_arret_de_bus_synth_hom.mp3"),
(1360,"une_cause_synth_hom.mp3"),
(1519,"le_ski_alpin_synth_hom.mp3"),
(1520,"le_ski_de_fond_synth_hom.mp3"),
(1521,"le_fond_synth_hom.mp3"),
(1522,"la_luge_synth_hom.mp3"),
(1523,"le_surf_des_neiges_synth_hom.mp3"),
(1535,"les_oeufs_de_poisson_synth_hom.mp3"),
(47,"a_synth.mp3"),]

from le_francais_dictionary.models import Word

for pk, new_filename in to_rename:
	word = Word.objects.get(pk=pk)
	old_url = word._polly_url
	word._polly_url = old_url.rsplit('/', 1)[0] + '/' + new_filename
	word.save()
	print(word, old_url, '=>', word._polly_url)
