from django.db import models
from django.contrib.postgres.fields import JSONField
from unidecode import unidecode


# Create your models here.
class Template(models.Model):
    name = models.CharField(max_length=200)
    data = JSONField(default={})
    new_data = JSONField(default={})
    no_red_end = models.BooleanField(default=False)

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
    only_reflexive = models.BooleanField(default=False)
    reflexive = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.infinitive

    def main_part(self):
        return self.infinitive.rstrip(self.template.infinitive_ending())

    def get_infinitive_no_accents(self):
        return unidecode(self.infinitive)
