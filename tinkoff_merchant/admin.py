import json

from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter

import bulk_update.helper
from django.contrib import admin

from .models import Payment, Receipt, ReceiptItem
from .services import MerchantAPI
from .consts import PAYMENT_PAYED_STATUSES, PAYMENT_REFUNDED_STATUSES
from .signals import payment_confirm, payment_refund


def make_get_status(modeladmin: admin.ModelAdmin, request, qs):
    to_update = []
    for p in qs:
        p:Payment
        api = MerchantAPI()
        old_status = p.status
        p = api.status(p)

        if old_status not in PAYMENT_PAYED_STATUSES and p.status in PAYMENT_PAYED_STATUSES:
            payment_confirm.send(modeladmin, payment=p)
        if old_status not in PAYMENT_REFUNDED_STATUSES and p.status in PAYMENT_REFUNDED_STATUSES:
            payment_refund.send(modeladmin, payment=p)

        to_update.append(p)

    bulk_update.helper.bulk_update(to_update)

make_get_status.short_description = 'Получить статус платежа'

def make_cancel(modeladmin: admin.ModelAdmin, request, qs):
    for p in qs:
        MerchantAPI().cancel(p)
        p.save()

make_cancel.short_description = 'Отменить платеж'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_id', 'get_amount_rub', 'success', 'status', 'payment_id', 'creation_date', 'update_date', 'email', 'recurrent', 'rebill_id', 'username']
    list_filter = ['status', 'success', 'recurrent']
    search_fields = ['order_id', 'payment_id', 'rebill_id', 'receipt__email', '_user__email']
    actions = [make_cancel, make_get_status]

    def get_amount_rub(self, obj):
        return obj.amount / 100

    get_amount_rub.short_description = 'Сумма (руб)'

    def has_add_permission(self, request):
        return False

    def get_fields(self, request, obj=None):
        return [f.name for f in obj._meta.fields if
                f.name not in ['request_history', 'response_history']] + [
            'request_history_prettified', 'response_history_prettified']

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in obj._meta.fields if f.name not in ['request_history', 'response_history']] + ['request_history_prettified', 'response_history_prettified']

    def request_history_prettified(self, instance:Payment):
        return prettify_json_field('request_history', instance)

    request_history_prettified.short_description='Request History'

    def response_history_prettified(self, instance:Payment):
        return prettify_json_field('response_history', instance)

    response_history_prettified.short_description = 'Response History'

def prettify_json_field(field_name, instance):
    response = json.dumps(getattr(instance, field_name), sort_keys=True,
                          indent=2)
    formatter = HtmlFormatter(style='colorful')
    response = highlight(response, JsonLexer(), formatter)
    style = "<style>" + formatter.get_style_defs() + "</style><br>"
    return mark_safe(style + response)

class PermissionsMixin:
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ReceiptItemInline(PermissionsMixin, admin.TabularInline):
    model = ReceiptItem


@admin.register(Receipt)
class ReceiptAdmin(PermissionsMixin, admin.ModelAdmin):
    list_display = ['id', 'payment', 'email', 'phone']
    inlines = [ReceiptItemInline]
