from home.utils import is_gpt_disabled


def geoip(request):
    if 'geoip' in request.session:
        return {
            'country_name': request.session['geoip']['country_name'],
            'country_code': request.session['geoip']['country_code'],
            'city': request.session['geoip']['city'],
            'region': request.session['geoip']['region']
        }
    else:
        return {
            'country_name': None,
            'country_code': None,
            'city': None,
            'region': None
        }

def gpt_disabled(request):
    return {
        'is_gpt_disabled': is_gpt_disabled(request)
    }
