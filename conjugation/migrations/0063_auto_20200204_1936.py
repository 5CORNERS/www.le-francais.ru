# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-02-04 16:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conjugation', '0062_auto_20191205_1433'),
    ]

    operations = [
        migrations.AlterField(
            model_name='translation',
            name='type',
            field=models.CharField(choices=[('translation', 'Перевод'), ('example', 'Пример использования'), ('collocation', 'Устойчивое выражение'), ('idiom', 'Идиоматическое выражение'), ('none', 'Не выбрано')], default=None, max_length=10, null=True),
        ),
    ]