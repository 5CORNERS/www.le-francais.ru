from django.db import models
from django.contrib.postgres.fields import JSONField


# Create your models here.
class Template(models.Model):
    name = models.CharField(max_length=200)
    infinitive = JSONField()
    indicative = JSONField()
    conditional = JSONField()
    subjunctive = JSONField()
    imperative = JSONField()
    participle = JSONField()

    def __str__(self):
        return self.name

class Verb(models.Model):
    infinitive = models.CharField(max_length=100)
    template = models.ForeignKey(Template)
    aspirate_h = models.BooleanField(default=False)
    
    def __str__(self):
        return self.infinitive