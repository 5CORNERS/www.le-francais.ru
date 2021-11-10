from datetime import timedelta

import dateutil.parser
import requests
from PIL import Image
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone

DEFAULT_PLACEMENTS_CHOICES = [
    ('conjugations_table_sidebar', 'Conjugations Table Sidebar'),
    ('test_placement', 'Test Placement')
]


class Placement(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class LineItem(models.Model):
    name = models.CharField(max_length=255)
    priority = models.PositiveIntegerField(default=0)
    placements = models.ManyToManyField(
        Placement, blank=True
    )
    ad_units = ArrayField(base_field=models.CharField(
        max_length=255,
    ), help_text='List of AdUnit names.', default=list, blank=True)

    do_not_show_to = ArrayField(base_field=models.CharField(
        max_length=255,
    ),
        help_text='Список slug\'ов страниц через запятую',
        verbose_name='Do not show if user was on following pages',
        default=list,
        blank=True
    )
    do_not_show_if_was_on_conjugations = models.BooleanField(default=False)

    views = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)

    capping_day = models.IntegerField(blank=True, null=True, default=None)
    capping_week = models.IntegerField(blank=True, null=True, default=None)
    capping_month = models.IntegerField(blank=True, null=True, default=None)

    def __str__(self):
        return self.name

    def check_cappings(self, times):
        if not (self.capping_day and self.capping_week and self.capping_month):
            return True

        times = [dateutil.parser.isoparse(time) for time in times]
        now = timezone.now()

        in_day = 0
        in_week = 0
        in_month = 0
        for time in times:
            delta = now - time
            if delta.days < 30:
                in_month += 1
            if delta.days < 7:
                in_week += 1
            if delta.days < 1:
                in_day += 1
        if self.capping_day is not None and in_day > self.capping_day:
            return False
        elif self.capping_week is not None and in_month > self.capping_week:
            return False
        elif self.capping_month is not None and in_month > self.capping_month:
            return False
        else:
            return True


def creative_image_validator():
    ...


class Creative(models.Model):
    name = models.CharField(max_length=256)
    utm_campaign = models.CharField(max_length=256, blank=True, null=True)
    utm_medium = models.CharField(max_length=256, blank=True, null=True)
    click_through_url = models.URLField(blank=False)
    image = models.ImageField(blank=True)
    image_url = models.URLField(blank=True, help_text='Одно из полей image или image_url должно быть заполнено')
    line_item = models.ForeignKey(
        LineItem, related_name='creatives',
        related_query_name='creative', on_delete=models.SET_NULL, null=True, blank=True
    )
    disable = models.BooleanField(default=False)

    _width = models.IntegerField(editable=False, blank=True, null=True)
    _height = models.IntegerField(editable=False, blank=True, null=True)

    views = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)

    @property
    def width(self):
        if self._width is None:
            self.save()
        return self._width

    @property
    def height(self):
        if self._height is None:
            self.save()
        return self._height

    def __str__(self):
        return self.name

    def get_image_url(self):
        if self.image_url:
            return self.image_url
        elif self.image:
            return self.image.url
        else:
            return ''

    def get_click_through_url(self, line_item, utm_source):
        return reverse('ads:ad-counter-redirect', args=(line_item.pk, self.pk, utm_source))

    def save(self, *args, **kwargs):
        self.set_dimensions()
        return super(Creative, self).save(*args, **kwargs)

    def set_dimensions(self):
        if self.image:
            self._width = self.image.width
            self._height = self.image.height
        elif self.image_url:
            response = requests.get(self.image_url)
            img:Image.Image = Image.open(response.raw)
            self._width = img.width
            self._height = img.height
