import json
import threading

import httplib2
from django.http.response import HttpResponse
from django.shortcuts import redirect
from oauth2client.client import OAuth2WebServerFlow
from wagtail.wagtailcore.models import Page

from home.src.site_import import import_content

flow = OAuth2WebServerFlow(client_id='499129759772-bqrp9ha0vfibn6t76fdgdmd87khnn2e0.apps.googleusercontent.com',
                           client_secret='CRTqrmLi-116OMgpFOnYS6wH',
                           scope='https://www.googleapis.com/auth/drive',
                           redirect_uri='http://localhost:8000/import/authorized')


def authorize(request):
    return redirect(flow.step1_get_authorize_url())


def authorized(request):
    credentials = flow.step2_exchange(request.GET['code'])
    http = credentials.authorize(httplib2.Http())
    t = threading.Thread(target=import_content,
                         args=(http,))
    t.setDaemon(True)
    t.start()
    return HttpResponse('')


def get_navigation_object_from_page(page: Page, current_page_id: int) -> dict:
    page_object = {
        "text": page.title,
        "nodes": [],
        "href": page.get_url()
    }
    if page.id == current_page_id:
        page_object["state"] = {
            "selected": True
        }
        page_object["selectable"] = False
    for child in page.get_children():
        if child.show_in_menus:
            page_object["nodes"].append(get_navigation_object_from_page(child, current_page_id))
    if len(page_object["nodes"]) == 0:
        page_object.pop('nodes', None)
    return page_object


def get_nav_data(request):
    if "rootId" not in request.GET:
        return HttpResponse(status=400, content="Root page id not provided")
    root_id = request.GET['rootId']
    page_id = int(request.GET['pageId'])
    nav_items = get_navigation_object_from_page(Page.objects.get(id=root_id), page_id)["nodes"]
    return HttpResponse(content=json.dumps(nav_items))
