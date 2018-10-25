import django.dispatch

payment_update = django.dispatch.Signal(providing_args=['payment'])
payment_confirm = django.dispatch.Signal(providing_args=['payment'])
