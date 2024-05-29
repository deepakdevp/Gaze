from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from .voices import voice_automaai
global_voice = voice_automaai()
def check_status_func(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            response = view_func(request, *args, **kwargs)
            return response
        except Exception as e:
            # Call the check_status function to validate the token
            check_status_response = global_voice.check_acess_status(request)
            if check_status_response.data.get("status") == "Token valid":
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return check_status_response

    return _wrapped_view