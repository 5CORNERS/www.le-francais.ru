from django.db import models
from django.contrib.postgres.fields import JSONField
from unidecode import unidecode
from django.urls import reverse

VOWELS_LIST = ['a','ê','é','h','e','â','i','o','ô','u','w','y','œ',]



# Create your models here.
class Template(models.Model):
    name = models.CharField(max_length=200)
    data = JSONField(default={})
    new_data = JSONField(default={})
    second_form = models.BooleanField(default=False)
    no_red_end = models.BooleanField(default=False)
    forms_count = models.IntegerField(default=1)

    def infinitive_ending(self):
        return self.name.split(':')[1]

    def __str__(self):
        return self.name

class Verb(models.Model):
    infinitive = models.CharField(max_length=100)
    infinitive_no_accents = models.CharField(max_length=100, default='')
    template = models.ForeignKey(Template)
    aspirate_h = models.BooleanField(default=False)
    maison = models.BooleanField(default=False)
    reflexive_only = models.BooleanField(default=False)
    reflexive = models.CharField(max_length=100, default='')

    masculin_only = models.BooleanField(default=False)
    has_passive = models.BooleanField(default=False)
    has_second_form = models.BooleanField(default=False)
    has_reflexive = models.BooleanField(default=False)
    has_s_en = models.BooleanField(default=False)


    def __str__(self):
        return self.infinitive

    def main_part(self):
        return self.infinitive.rsplit(self.template.infinitive_ending(),1)[0]

    def get_infinitive_no_accents(self):
        return unidecode(self.infinitive)

    def url(self):
        return reverse('conjugation:verb', kwargs=dict(femenin=None, verb=self.infinitive_no_accents, se=None))

    def feminin_url(self):
        return reverse('conjugation:verb', kwargs=dict(femenin='feminin_',verb=self.infinitive_no_accents,se=None))

    def se_url(self):
        return reverse('conjugation:verb', kwargs=dict(femenin=None, verb=self.infinitive_no_accents, se='se_'))

    def feminin_se_url(self):
        return reverse('conjugation:verb', kwargs=dict(femenin='feminin_', verb=self.infinitive_no_accents, se='se_'))

    def infnitive_first_letter_is_vowel(self):
        return True if self.infinitive[0] in VOWELS_LIST else False

    def construct_conjugations(self):
        self.conjugations = {}
        for mood in self.template.new_data.keys():
            self.conjugations[mood] = {}
            for tense in self.template.new_data[mood].keys():
                self.conjugations[mood][tense] = [None]*6
                for person, i in enumerate(self.template.new_data[mood][tense]['p']):
                    endings = self.template.new_data[mood][tense]['p'][person]['i']
                    if endings == None:
                        pass
                    elif isinstance(endings, list):
                        forms = []
                        for ending in endings:
                            forms.append(self.main_part()+ending)
                        self.conjugations[mood][tense][person] = forms
                    else:
                        self.conjugations[mood][tense][person] =self.main_part() + endings

