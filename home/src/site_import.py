import csv
import io
import json
from io import StringIO
from typing import Dict
from typing import List
from urllib.parse import parse_qs
from urllib.parse import urlparse

import urllib3
import xmltodict
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from wagtail.core.models import Page, Site

from home.models import DefaultPage, LessonPage, PageWithSidebar


def import_content(http):
    if Page.objects.count() > 100:
        return
    drive_service = build('drive', 'v3', http=http)
    request = drive_service.files().export_media(fileId='1KhbjJr4cD2J6-9vzaC9NgQfReQJa5hL4dDb4v0-2Ttk',
                                                 mimeType='text/csv')
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    table_reader = csv.reader(StringIO(fh.getvalue().decode('utf-8')))
    lessons = {}
    for row in table_reader:
        try:
            lesson_information = LessonInformation(row, drive_service)
            lessons[lesson_information.number] = lesson_information
        except:
            pass
    load_old_site_pages(lessons)
    for lesson in lessons.values():
        if lesson.content_type == 'Пустой таб' or lesson.content is not None:
            add_new_lesson(lesson)


def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""


class LessonInformation:
    def __init__(self, row: List[str], drive_service):
        self.number = int(row[0])
        content_url = urlparse(row[1])
        summary_url = urlparse(row[4])
        repetition_material = urlparse(row[7])

        if len(summary_url.scheme) > 0:
            self.summary_url = summary_url.geturl()
        else:
            self.summary_url = None

        if len(repetition_material.scheme) > 0:
            self.repetition_material = repetition_material.geturl()
        else:
            self.repetition_material = None

        if len(content_url.scheme) > 0:
            file_id = content_url.path.split('/')[-1]
            if file_id == 'open':
                file_id = parse_qs(content_url.query)['id']

            request = drive_service.files().export_media(fileId=file_id,
                                                         mimeType='text/plain')
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            self.content = fh.getvalue().decode('utf-8')
            self.content_type = None
        else:
            self.content = None
            self.content_type = row[1]


class OldSitePage:
    def __init__(self, text):
        document = BeautifulSoup(text, 'html.parser')
        self.content_element = document.select('#sites-canvas')[0]
        self.title = document.find('title').get_text().rsplit(u'- Самоучитель французского языка', 1)[0].strip()
        self.is_lesson_page = self.title.startswith(u'Урок ')
        if self.is_lesson_page:
            if "(" in self.title:
                self.number = int(find_between(self.title, '(', ')'))
            else:
                self.number = int(self.title.rsplit(u'Урок', 1)[1].strip())


def load_old_site_pages(lessons_information: Dict[int, LessonInformation]):
    http = urllib3.PoolManager()
    url = "http://www.le-francais.ru/system/feeds/sitemap"
    sitemap_request = http.request('GET', url)
    sitemap = xmltodict.parse(sitemap_request.data)

    Page.objects.get(slug='home').delete()

    for url in sitemap['urlset']['url']:
        location = url['loc']
        parsed_location = urlparse(location)
        page_request = http.request('GET', location)
        old_site_page = OldSitePage(page_request.data)
        audio_files = []
        for iframe in old_site_page.content_element.find_all('iframe'):
            src_url = urlparse(iframe['src'])
            params = parse_qs(src_url.query)
            if 'up_MP3' in params:
                file_url = params['up_MP3'][0]
            elif 'up_FILE' in params:
                file_url = params['up_FILE'][0]
            else:
                continue
            # iframe.parent.text = '%splitter%'
            # element['class'] = 'player'
            # element['data-file-url'] = file_url
            audio_files.append(file_url)
            element_to_replace = iframe
            while len(element_to_replace.parent.contents) <= 1:
                element_to_replace = element_to_replace.parent
            element_to_replace.replaceWith('%splitter%')
        body = []
        html_parts = old_site_page.content_element.prettify().split('%splitter%')
        for i in range(0, len(html_parts)):
            body.append({'type': 'html', 'value': html_parts[i]})
            if i < len(audio_files):
                body.append({'type': 'audio', 'value': {'url': audio_files[i]}})

        parent_path = '/' if parsed_location.path == '/' else '/home' + parsed_location.path.rsplit('/', 1)[0] + '/'
        slug = 'home' if parsed_location.path == '/' else parsed_location.path.rsplit('/', 1)[1]
        parent = Page.objects.get(url_path=parent_path)
        if parsed_location.path == '/':
            parent.add_child(
                instance=DefaultPage(title=old_site_page.title, slug=slug, show_in_menus=1, body=json.dumps(body)))
            continue

        if old_site_page.is_lesson_page:
            lesson = lessons_information[old_site_page.number]
            if lesson.content is not None:
                continue
            parent.add_child(
                instance=LessonPage(
                    title=old_site_page.title,
                    slug=slug,
                    show_in_menus=1,
                    repetition_material=lesson.repetition_material,
                    summary=lesson.summary_url,
                    body=json.dumps(body),
                    other_tabs=None
                )
            )
        else:
            parent.add_child(
                instance=PageWithSidebar(
                    title=old_site_page.title,
                    slug=slug,
                    show_in_menus=1,
                    body=json.dumps(body)
                )
            )
    Site.objects.create(hostname='localhost', port=80, is_default_site=True, root_page=Page.objects.get(slug='home'))


def add_new_lesson(lesson_information: LessonInformation):
    parent = Page.objects.get(url_path='/home/lecons/')
    if lesson_information.content is not None:
        body = [{
            'type': 'paragraph',
            'value': lesson_information.content
        }]
    elif lesson_information.content_type == 'Пустой таб':
        body = []
    else:
        return
    try:
        parent.add_child(
            instance=LessonPage(
                title='Урок ' + str(lesson_information.number),
                slug='lecon-' + str(lesson_information.number),
                show_in_menus=1,
                repetition_material=lesson_information.repetition_material,
                summary=lesson_information.summary_url,
                body=json.dumps(body),
                other_tabs=None
            )
        )
    except:
        pass
