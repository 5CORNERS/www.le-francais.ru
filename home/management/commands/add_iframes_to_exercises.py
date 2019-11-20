import re
from pathlib import Path

from django.core.management import BaseCommand
from typing import Dict

from .mail_archive import html_to_block
import math
import pandas
import urllib.request
from home.blocks.LearningAppsBlock import LearningAppsBlock


def rewrite_additional_exercises(table):
    pass


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--additional',
            action='store_true',
            default=False,
            dest='additional'
        )
        parser.add_argument(
            '--jsons',
            action='store_true',
            default=False,
            dest='jsons'
        )
        parser.add_argument(
            '--lesson',
            dest='lessons',
            action='append'
        )

    def handle(self, *args, **options):
        table = get_table_dict('home/data/devoirs.csv' if not options[
            'additional'] else 'home/data/devoirs_additional.csv')
        if options['additional']:
            rewrite_excercises(table, additional=True, options=options)
        else:
            rewrite_excercises(table, additional=False, options=options)
        if options['jsons']:
            retrieve_jsons(table)


def get_table_dict(p):
    table = pandas.read_csv(p, sep=',').sort_values(['Lesson', 'N'],
                                                    ascending=[True, True])
    table_dict = table.to_dict()
    return table_dict


def rewrite_excercises(table_dict, additional, options):
    from home.models import LessonPage
    pages_dict: Dict[int, LessonPage] = {}
    for n in range(len(table_dict['Lesson'])):
        lesson_number = list(table_dict['Lesson'].values())[n]
        if options['lessons']:
            if lesson_number not in options['lessons']:
                continue
        if list(table_dict['Lesson'].values())[n] not in pages_dict.keys():
            pages_dict[lesson_number] = LessonPage.objects.get(
                lesson_number=lesson_number)
            if additional:
                pages_dict[lesson_number].additional_exercise.stream_data = []
            else:
                pages_dict[lesson_number].exercise.stream_data = []
        # FIXME make this readable
        url = list(table_dict['HTML'].values())[n]
        app_id = re.search(r'v=(.+?)[\'"]', url).group(1)
        app_number = list(table_dict['N'].values())[n]
        title = list(table_dict['TITLE'].values())[n]
        height = re.search(r'(?:height:(.+?))(?:[;"\'])', url).group(1)
        width = re.search(r'(?:width:(.+?))(?:[;"\'])', url).group(1)
        iframe_block = dict(
            value=dict(
                app_id=app_id,
                number=app_number,
                title=title if not isinstance(title, float) else '',
                height=height,
                width=width,
                show_lesson_number=1 if not additional else 0
            ),
            type='learning_apps',
        )
        if additional:
            pages_dict[lesson_number].additional_exercise.stream_data.append(
                iframe_block)
        else:
            pages_dict[lesson_number].exercise.stream_data.append(iframe_block)
    if not additional:
        instruction = html_to_block(
            '<div class="alert alert-success"><p>Прочтите советы о том, как делать <a href="/lecons/bibliotheque/comment_faire_les_devoirs/">упражнения из домашки</a>.</p></div>')
        for n, page in pages_dict.items():
            page.exercise.stream_data.insert(0, instruction)
    for n, page in pages_dict.items():
        print("Saving draft {0}".format(page.lesson_number))
        page.save_revision()
    for n, page in pages_dict.items():
        print("Publish {0}".format(page.lesson_number))
        page.get_latest_revision().publish()
    return


def retrieve_jsons(table_dict):
    iframes = []
    for n in range(len(table_dict['Lesson'])):
        iframes.append(table_dict['HTML'][n])
    for iframe in iframes:
        get_json(get_id(iframe))


def get_id(iframe):
    return iframe.split('?v=')[1].split('\"')[0]


def get_json(id):
    file = Path('home/data/exercises/' + id + '.json')
    if not file.is_file():
        url = 'https://learningapps.org/data?jsonp=1&id={0}&version=38'.format(
            id)
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(url, 'home/data/exercises/' + id + '.json')
        print(id + ' Success')
