class GetPush4SiteId(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        response = self.get_response(request)
        return response

    def process_request(self, request):
        p4s_id = request.COOKIES.get('p4s_push_subscriber_id', None)
        if not (p4s_id is None or p4s_id in request.user.push4site):
            request.user.push4site.append(p4s_id)
