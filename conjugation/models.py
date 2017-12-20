from django.db import models
from django.contrib.postgres.fields import HStoreField

# Create your models here.
class Template(models.Model):
    name = models.CharField(max_length=100)
    infinitive = HStoreField()
    indicative = HStoreField()
    conditional = HStoreField()
    subjunctive = HStoreField()
    imperative = HStoreField()
    participle = HStoreField()

class Verb(models.Model):
    infinitive = models.CharField(max_length=100)
    template = models.ForeignKey(Template)
    aspirate_h = models.BooleanField(default=False)