from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response

    data = response.data

    # Normalize ValidationError
    if isinstance(data, dict) and "code" in data and "message" in data:
        return response

    # Convert DRF APIException format
    if hasattr(exc, "default_code"):
        response.data = {
            "code": exc.default_code,
            "message": str(exc.detail),
        }

    return response
