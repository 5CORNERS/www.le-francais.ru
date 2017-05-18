import threading

import httplib2
from django.http.response import HttpResponse
from django.shortcuts import redirect
from oauth2client.client import OAuth2WebServerFlow

from home.src.site_import import import_content

flow = OAuth2WebServerFlow(client_id='499129759772-bqrp9ha0vfibn6t76fdgdmd87khnn2e0.apps.googleusercontent.com',
                           client_secret='CRTqrmLi-116OMgpFOnYS6wH',
                           scope='https://www.googleapis.com/auth/drive',
                           redirect_uri='http://hidden-refuge-27954.herokuapp.com/import/authorized')


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
