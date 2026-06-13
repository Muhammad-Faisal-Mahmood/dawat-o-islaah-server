import logging
from django.core.exceptions import RequestDataTooBig
from django.http import HttpResponse

logger = logging.getLogger(__name__)


class FileUploadSizeErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except RequestDataTooBig:
            return HttpResponse(
                "Max upload size is 2gb. the file you uploaded is greater than that",
                content_type="text/plain",
                status=400,
            )
