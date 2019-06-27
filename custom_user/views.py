# -*- coding: UTF-8 -*-
import json
from datetime import datetime

from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import EmailMessage
from django.shortcuts import HttpResponse, render
from django.utils.decorators import method_decorator
from django.views import View

from custom_user.consts import MESSAGE_FOR_NOT_PAYED, MESSAGE_FOR_PAYED
from custom_user.models import User


class SawMessageView(View):
    def dispatch(self, request, *args, **kwargs):
        return super(SawMessageView, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        user = request.user  # type: User
        if request.POST['action'] == 'make_true':
            if user.saw_message:
                return HttpResponse(status=403)
            if user.has_payed():
                msg_body = MESSAGE_FOR_PAYED
                user.add_cups(5)
            else:
                msg_body = MESSAGE_FOR_NOT_PAYED
                if user.days_since_joined() > 7:
                    user.add_cups(1)
            if not user.is_staff:
                EmailMessage(
                    to=[request.user.email],
                    subject='Активация уроков на сайте le-francais.ru',
                    body=msg_body,
                    from_email='ilia.dumov@files.le-francais.ru',
                    reply_to=['support@le-francais.ru']
                ).send()
            user.saw_message = True
            user.saw_message_datetime = datetime.now()
            user.save()
            return HttpResponse(b'OK', status=200)
        elif request.POST['action'] == 'get_state':
            return HttpResponse(json.dumps(user.saw_message),
                                content_type='application/json',
                                status=200)
        else:
            return HttpResponse(status=400)


from home.models import UserLesson


class AdminCommands(View):

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AdminCommands, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, template_name='custom_user/admin_commands.html')

    def post(self, request):
        action = request.POST['action']
        user = request.user
        if action == 'zero':
            for userlesson in UserLesson.objects.filter(user=user):
                userlesson.delete()
            user.add_cups(-user.cup_amount)
            user.add_credit_cups(-user.cup_credit)
            user.saw_message = False
            user.saw_message_datetime = None
            user.save()
        elif action == 'add_cup':
            user.add_cups(1)
        elif action == 'switch_low_price':
            user.switch_low_price()
        elif action == 'add_minus_cup':
            user.add_cups(-1)
        elif action == 'switch_must_pay':
            if user.must_pay:
                user.must_pay = False
            else:
                user.must_pay = True
            user.save()
        return render(request, template_name='custom_user/admin_commands.html')
