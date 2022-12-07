import os.path
import uuid

import dateutil.parser
import requests
import shortuuid
from PIL import Image
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField, JSONField
from django.core.exceptions import ValidationError
from django.db import models
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone

from .consts import LOG_TYPE_CHOICES

User = get_user_model()

DEFAULT_PLACEMENTS_CHOICES = [
    ('conjugations_table_sidebar', 'Conjugations Table Sidebar'),
    ('test_placement', 'Test Placement')
]


class Placement(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


def calculate_times(times, now=None):
    if now is None:
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
    return in_day, in_week, in_month


class LineItem(models.Model):
    name = models.CharField(max_length=255, unique=True)
    label = models.CharField(max_length=256, null=True, blank=True,
                             default=None)
    priority = models.PositiveIntegerField(default=0)
    placements = models.ManyToManyField(
        Placement, blank=True
    )
    placements_inverted = models.BooleanField(default=False, verbose_name="Invert Placements")
    ad_units = ArrayField(base_field=models.CharField(
        max_length=255,
    ), help_text='List of AdUnit names.', default=list, blank=True)

    do_not_show_to = ArrayField(base_field=models.CharField(
        max_length=255,
    ),
        help_text='Список slug\'ов страниц через запятую',
        verbose_name='Don\'t display if user visited following pages',
        default=list,
        blank=True
    )
    less_than_n_days_ago = models.BooleanField(
        default=False, verbose_name="Не показывать пользователям, видевших следующие страницы менее чем N дней назад")
    less_than_n_days_ago_value = models.IntegerField(blank=True, null=True, verbose_name="Значение в днях")

    do_not_show_if_was_on_conjugations = models.BooleanField(
        default=False, verbose_name='Don\'t display if user visited conjugations pages')

    views = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)

    capping_day = models.IntegerField(blank=True, null=True, default=None)
    capping_week = models.IntegerField(blank=True, null=True, default=None)
    capping_month = models.IntegerField(blank=True, null=True, default=None)

    do_not_display_to_registered_users = models.BooleanField(default=False)
    do_not_display_to_anonymous_users = models.BooleanField(default=False)

    labels = ArrayField(models.CharField(max_length=256), blank=True,
                        default=list)

    targeting_country = models.CharField(max_length=256, null=True, blank=True)
    targeting_city = models.CharField(max_length=256, null=True, blank=True)
    targeting_invert = models.BooleanField(default=False, verbose_name='Invert Geo Targeting')

    disable = models.BooleanField(default=False, blank=True)

    utm_campaign = models.CharField(max_length=256, null=True, blank=True)
    utm_medium = models.CharField(max_length=256, null=True, blank=True)

    do_not_display_to_donating_users = models.BooleanField(
        default=False, blank=True,
        verbose_name="Do not display to users who ever donate"
    )
    do_not_display_to_donating_users_days_ago = models.IntegerField(
        null=True, blank=True,
        verbose_name="Do not display to users, who donate less than N days age"
    )

    def __str__(self):
        return self.name

    def check_cappings(self, times) -> bool:
        if not (self.capping_day and self.capping_week and self.capping_month):
            return True

        parsed_times = []
        for time in times:
            parsed_times.append(dateutil.parser.isoparse(time) if isinstance(time, str) else time)
        in_day, in_week, in_month = calculate_times(parsed_times)
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

def creative_image_file_update(instance, filename):
    path = "YWR2ZXJ0aXNlbWVudA"
    ext = filename.split('.')[-1]
    new_name = f'{shortuuid.random()}.{ext}'
    return f"{path}/{new_name}"

class Creative(models.Model):
    name = models.CharField(max_length=256, blank=False)
    utm_campaign = models.CharField(max_length=256, blank=True, null=True, help_text="Will override line item values")
    utm_medium = models.CharField(max_length=256, blank=True, null=True, help_text="Will override line item values")
    # utm_source = models.CharField(max_length=256, blank=True, null=True, help_text="Will override ad unit value")

    image_click_through_url = models.URLField(blank=True)
    image = models.ImageField(blank=True, upload_to=creative_image_file_update) # TODO: changing filename
    image_url = models.URLField(blank=True, help_text='Одно из полей image или image_url должно быть заполнено')

    html = models.TextField(blank=True, default=None, null=True)

    line_item = models.ForeignKey(
        LineItem, related_name='creatives',
        related_query_name='creative', on_delete=models.SET_NULL, null=True, blank=True
    )
    disable = models.BooleanField(default=False)

    _width = models.IntegerField(editable=False, blank=True, null=True)
    _height = models.IntegerField(editable=False, blank=True, null=True)

    views = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)

    labels = ArrayField(models.CharField(max_length=256), blank=True, default=list)
    fluid = models.BooleanField(default=False, blank=True)

    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unique_class = shortuuid.uuid()

    @property
    def width(self):
        if (self.html or self.fluid) and self._width is None:
            return 1
        elif self._width is None:
            self.save()
        return self._width

    @property
    def height(self):
        if self._height is None:
            self.save()
        return self._height

    @property
    def line_item_name(self):
        if self.line_item:
            return self.line_item.name
        else:
            return None

    def __str__(self):
        return f'{self.name}:{self.line_item_name}'

    def get_image_url(self):
        if self.image_url:
            return self.image_url
        elif self.image:
            return self.image.url
        else:
            return ''

    def get_click_through_url(self, utm_source=None, log_id=None):
        # if utm_source is None:
            return reverse('ads:creative-click-through_wo_utm', kwargs={
                'uuid': self.uuid, 'log_id': log_id
            })
        # else:
        #     return reverse('ads:creative-click-through', kwargs={
        #         'uuid': self.uuid, 'utm_source': utm_source, 'log_id': log_id
        #     })

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
        elif self.fluid or (self.html and self._width is None or self.height is None):
            self._width = None
            self._height = None

    def serve_body(self, request: HttpRequest, utm_source=None, log_id=None):
        # if self.utm_source is not None:
        #     utm_source = self.utm_source
        click_url = self.get_click_through_url(utm_source, log_id)
        return render_to_string(
            'ads/creative_body.html',
            {'self': self, 'utm_source': utm_source,
             'click_url':click_url},
            request,
        )

    def serve_head(self, request: HttpRequest, sizes):
        if sizes:
            max_width = max([s['width'] for s in sizes if not s['fluid']])
            min_width = min([s['width'] for s in sizes if not s['fluid']])
            max_height = max([s['height'] for s in sizes if not s['fluid']])
            min_height = min([s['height'] for s in sizes if not s['fluid']])
        else:
            max_width = None
            min_width = None
            max_height = None
            min_height = None
        return render_to_string(
            'ads/creative_head.html',
            dict(
                self=self,
                max_width=max_width,
                min_width=min_width,
                max_height=max_height,
                min_height=min_height,
                width=self.width,
                height=self.height,
                fluid=self.fluid
            ),
            request,
        )

def set_default_utm():
    return dict(
        utm_campaign=None,
        utm_medium=None,
        utm_source=None
    )
class Log(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    ip = models.GenericIPAddressField()
    country = models.CharField(null=True, max_length=128)
    city = models.CharField(null=True, max_length=128)
    datetime = models.DateTimeField(auto_now_add=True)
    line_item = models.ForeignKey(LineItem, on_delete=models.SET_NULL, null=True)
    creative = models.ForeignKey(Creative, on_delete=models.SET_NULL, null=True)
    log_type = models.CharField(choices=LOG_TYPE_CHOICES, max_length=10)
    ad_unit_name = models.CharField(max_length=128, null=True, blank=True)
    ad_unit_placements = ArrayField(base_field=models.CharField(max_length=256), default=list)
    clicked = models.BooleanField(default=False)
    click_datetime = models.DateTimeField(default=None, null=True, blank=True)
    utm_data = JSONField(default=set_default_utm)

    def serve_body(self, request: HttpRequest):
        return render_to_string(
            'ads/creative_body.html',
            {'self': self},
            request,
        )

    def serve_head(self, request: HttpRequest):
        return render_to_string(
            'ads/creative_head.html',
            {'self': self},
            request,
        )

    def __str__(self):
        return f"Log Object:{self.pk}"
