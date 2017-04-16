# -*- coding: utf-8 -*-

import json
from urllib.parse import urlparse, parse_qs

import urllib3
import xmltodict
from django.core.management import BaseCommand
from wagtail.wagtailcore.models import Page, Site
from bs4 import BeautifulSoup

from home.models import DefaultPage, PageWithSidebar


class Command(BaseCommand):
    def handle(self, *args, **options):
        http = urllib3.PoolManager()
        url = "http://www.le-francais.ru/system/feeds/sitemap"
        sitemap_request = http.request('GET', url)
        sitemap = xmltodict.parse(sitemap_request.data)

        Page.objects.get(slug='home').delete()

        for url in sitemap['urlset']['url']:
            location = url['loc']
            parsed_location = urlparse(location)
            page_request = http.request('GET', location)
            document = BeautifulSoup(page_request.data, 'html.parser')
            content_element = document.select('#sites-canvas')[0]
            audio_files = []
            for iframe in content_element.find_all('iframe'):
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
            html_parts = content_element.prettify().split('%splitter%')
            for i in range(0, len(html_parts)):
                body.append({'type': 'html', 'value': html_parts[i]})
                if i < len(audio_files):
                    body.append({'type': 'audio', 'value': {'url': audio_files[i]}})

            parent_path = '/' if parsed_location.path == '/' else '/home' + parsed_location.path.rsplit('/', 1)[0] + '/'
            slug = 'home' if parsed_location.path == '/' else parsed_location.path.rsplit('/', 1)[1]
            title = document.find('title').get_text().rsplit(u'- Самоучитель французского языка', 1)[0].strip()
            parent = Page.objects.get(url_path=parent_path)
            if parsed_location.path == '/':
                parent.add_child(instance=DefaultPage(title=title, slug=slug, show_in_menus=1, body=json.dumps(body)))
            else:
                parent.add_child(instance=PageWithSidebar(title=title, slug=slug, show_in_menus=1, body=json.dumps(body)))
        Site.objects.create(hostname='localhost', port=80, is_default_site=True, root_page=Page.objects.get(id=3))
