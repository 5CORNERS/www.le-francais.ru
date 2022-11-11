from home.utils import is_gpt_disabled


def geoip(request):
    if 'geoip' in request.session:
        return {
            'country_name': request.session['geoip'].get('country_name'),
            'country_code': request.session['geoip'].get('country_code'),
            'city': request.session['geoip'].get('city'),
            'region': request.session['geoip'].get('region')
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
