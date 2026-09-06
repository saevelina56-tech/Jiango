import time
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = getattr(settings, 'ENABLE_REQUEST_LOGGING', True)

    def __call__(self, request):
        if not self.enabled:
            return self.get_response(request)
        
        start = time.time()
        response = self.get_response(request)
        duration = time.time() - start
        
        ip = request.META.get('REMOTE_ADDR')
        if request.META.get('HTTP_X_FORWARDED_FOR'):
            ip = request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0]
        
        logger.info(f'IP: {ip} | {request.method} {request.path} | {duration:.3f}s')
        
        return response