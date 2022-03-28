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
