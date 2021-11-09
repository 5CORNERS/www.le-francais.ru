from django.db.models import F
from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView, TemplateView
from .models import Creative, LineItem


class AdCounterRedirectView(RedirectView):
    """
    ?utm_campaign=campaign&utm_medium=medium&utm_source=source
    """
    def get_redirect_url(self, *args, **kwargs):
        creative = get_object_or_404(Creative, pk=kwargs['creative'])
        line_item = get_object_or_404(LineItem, pk=kwargs['line_item'])
        utm_source = kwargs['source']

        if not self.request.user.is_staff:

            creative.clicks = F('clicks') + 1
            creative.save(update_fields=['clicks'])

            line_item.clicks = F('clicks') + 1
            line_item.save(update_fields=['clicks'])

        return creative.click_through_url \
               + f'?utm_campaign={creative.utm_campaign}&utm_medium={creative.utm_medium}&utm_source={utm_source}'


class TestView(TemplateView):
    template_name = 'ads/test.html'
