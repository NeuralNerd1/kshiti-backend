from rest_framework.response import Response


def api_error(code: str, message: str, status_code: int):
    return Response(
        {
            "error": {
                "code": code,
                "message": message,
            }
        },
        status=status_code,
    )
