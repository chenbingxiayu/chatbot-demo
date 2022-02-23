import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import (
  HttpResponseNotAllowed,
)

logger = logging.getLogger("django.request")

# allowed http methods
class HttpMiddleware:
  http_method_names = ['get', 'post', 'put', 'delete', 'connect']

  def __init__(self, get_response):
    self.get_response = get_response
    # One-time configuration and initialization.

  def __call__(self, request):
    # Code to be executed for each request before
    # the view (and later middleware) are called.
    if request.method.lower() not in self.http_method_names:
      logger.warning(
        "Method Not Allowed (%s): %s",
        request.method,
        request.path,
        extra={"status_code": 405, "request": request},
      )
      return HttpResponseNotAllowed(self._allowed_methods())

    response = self.get_response(request)

    # Code to be executed for each request/response after
    # the view is called.

    return response

  def _allowed_methods(self):
    return [m.upper() for m in self.http_method_names]
