import logging
import time

logger = logging.getLogger(__name__)

class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        method = request.method
        path = request.get_full_path()
        user = request.user.username if request.user.is_authenticated else 'Anonymous'
        logger.info(f"Начинаем {method} {path} для {user}")
        response = self.get_response(request)
        duration = (time.time() - start) * 1000  # ms
        logger.info(f"Завершено {method} {path} для {user} – статус {response.status_code}, время {duration:.1f}ms")
        return response