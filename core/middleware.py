import uuid

class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user:
            request.id = str(uuid.uuid4())
            return self.get_response(request)
        else:
            return request