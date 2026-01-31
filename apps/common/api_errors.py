from rest_framework.response import Response


def api_error(*, code: str, message: str, status: int):
    """
    Standard API error response for frontend consumption.
    """
    return Response(
        {
            "code": code,
            "message": message,
        },
        status=status,
    )
