from __future__ import annotations

import time
import logging


logger = logging.getLogger('django')


class ApiRequestLogMiddleware:
    """
    Lightweight access log for /api/* endpoints.

    Writes method, path, status, user, and latency to the existing django logger.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not (request.path or '').startswith('/api/'):
            return self.get_response(request)

        started = time.perf_counter()
        response = self.get_response(request)
        elapsed_ms = (time.perf_counter() - started) * 1000

        user = getattr(request, 'user', None)
        user_part = getattr(user, 'username', 'anon') if getattr(user, 'is_authenticated', False) else 'anon'
        logger.info(
            'API %s %s -> %s user=%s %.1fms',
            request.method,
            request.path,
            getattr(response, 'status_code', '-'),
            user_part,
            elapsed_ms,
        )
        return response

