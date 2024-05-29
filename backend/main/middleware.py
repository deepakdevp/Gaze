from django.utils.deprecation import MiddlewareMixin


class XForwardedForMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if 'REMOTE_ADDR' not in request.META:
            try:
                request.META['REMOTE_ADDR'] = request.META['HTTP_X_REAL_IP']
            except:
                request.META['REMOTE_ADDR'] = '1.1.1.1'