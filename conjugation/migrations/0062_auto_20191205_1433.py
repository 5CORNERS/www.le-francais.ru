# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2019-12-05 11:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('conjugation', '0061_auto_20191028_2014'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChildrenRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='FrTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RuTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=100)),
                ('word_normalise', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterModelOptions(
            name='translation',
            options={'ordering': ['order', 'verb']},
        ),
        migrations.AddField(
            model_name='translation',
            name='comment',
            field=models.CharField(max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='translation',
            name='fr_word',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='translation',
            name='order',
            field=models.IntegerField(blank=True, default=0, help_text='Поле для сортировки'),
        ),
        migrations.AddField(
            model_name='translation',
            name='ru_word',
            field=models.CharField(default=None, max_length=800, null=True),
        ),
        migrations.AddField(
            model_name='translation',
            name='status',
            field=models.CharField(choices=[('', ''), ('', ''), ('', '')], default=None, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='translation',
            name='type',
            field=models.CharField(choices=[('verb_translation', 'Перевод'), ('example', 'Пример использования'), ('collocation', 'Устойчивое выражение'), ('idiom', 'Идиоматическое выражение'), ('none', 'Не выбрано')], default=None, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='childrenrelation',
            name='child',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='child', to='conjugation.Translation'),
        ),
        migrations.AddField(
            model_name='childrenrelation',
            name='translation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parent', to='conjugation.Translation'),
        ),
        migrations.AddField(
            model_name='translation',
            name='children',
            field=models.ManyToManyField(through='conjugation.ChildrenRelation', to='conjugation.Translation'),
        ),
        migrations.AddField(
            model_name='translation',
            name='fr_tag',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='conjugation.FrTag'),
        ),
        migrations.AddField(
            model_name='translation',
            name='ru_tags',
            field=models.ManyToManyField(to='conjugation.RuTag'),
        ),
    ]
