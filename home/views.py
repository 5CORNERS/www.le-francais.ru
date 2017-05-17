import csv
from io import StringIO
from typing import List
from urllib.parse import urlparse

import httplib2
import io

from django.http.response import HttpResponse
from django.shortcuts import redirect
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from oauth2client.client import OAuth2WebServerFlow

from home.src.site_import import load_old_site_pages, LessonInformation, add_new_lesson

flow = OAuth2WebServerFlow(client_id='499129759772-bqrp9ha0vfibn6t76fdgdmd87khnn2e0.apps.googleusercontent.com',
                           client_secret='CRTqrmLi-116OMgpFOnYS6wH',
                           scope='https://www.googleapis.com/auth/drive')


def authorize(request):
    flow.redirect_uri = 'http://' + request.get_host() + '/import/authorized'
    return redirect(flow.step1_get_authorize_url())


def authorized(request):
    credentials = flow.step2_exchange(request.GET['code'])
    http = credentials.authorize(httplib2.Http())
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
    return HttpResponse('')
