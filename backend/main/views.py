from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from base.models import Profile
from django.utils.dateparse import parse_datetime
from .voices import voice_automaai
from .models import Voice
from django.utils import timezone
import os
import uuid
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from .decorators import check_status_func
from django.conf import settings
from django_ratelimit.decorators import ratelimit
global_voice = voice_automaai()

@api_view(['POST'])
# @ratelimit(key='user', rate='3000/m', block=True, method='POST')
def register_voice(request):
    try:
        # Get name from request data
        name = request.data.get('name', None)

        # Check if file is in the request
        if 'file' not in request.FILES or not name:
            return Response({"message": "Both 'name' and 'file' are required fields."}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['file']
        description = request.data.get('description', None)

        # Save the file to the server
        file_name = default_storage.save(file.name, ContentFile(file.read()))
        file_url = default_storage.url(file_name)
        absolute_file_url = os.path.join(settings.MEDIA_ROOT, file_name)

        # Register the voice using the file_url
        voice_id = global_voice.add_voice(name, description, absolute_file_url)


        if voice_id["status"] == 200:
            unique_uuid = str(uuid.uuid4())[:5]
            voice_id_name = f"AAI_{unique_uuid}"
            new_voice = Voice(
                voice_id=voice_id["voice_id"],
                voice_id_name=voice_id_name,
                file_url=file_url
            )
            new_voice.profile = request.user.profile
            new_voice.save()

            # Delete the file after processing
            if default_storage.exists(file_name):
                default_storage.delete(file_name)

            return Response(voice_id_name)
        else:
            # Delete the file if there was an error in registering the voice
            if default_storage.exists(file_name):
                default_storage.delete(file_name)
            return Response({"message": voice_id["message"]}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
# @ratelimit(key='user', rate='3000/m', block=True, method='POST')
def delete_voice(request):
    try:
        voice_id_name = request.data.get("voice_id_name")
        voice_entry = Voice.objects.get(voice_id_name=voice_id_name)
        voice_id = voice_entry.voice_id
        voice_deleted_response = global_voice.delete_voice(voice_id)

        if voice_deleted_response["status"] == 200:
            voice_entry.delete()
            return Response(voice_id_name + voice_deleted_response["message"])
        else:
            return Response(voice_deleted_response["message"], status=status.HTTP_400_BAD_REQUEST)

    except ObjectDoesNotExist:
        return Response({"error": "Voice entry not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
# @ratelimit(key='user', rate='3000/m', block=True, method='POST')
def generate_voice(request):
    try:
        text = request.data.get("text")
        voice_id_name = request.data.get("voice_id_name")
        voice_entry = Voice.objects.get(voice_id_name=voice_id_name)
        voice_id = voice_entry.voice_id
        voice_name = voice_entry.voice_id_name
        generated_voice_response = global_voice.generate_voice(voice_id, voice_name, text, True)
        return Response(generated_voice_response)

    except ObjectDoesNotExist:
        return Response({"error": "Voice entry not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# @ratelimit(key='user', rate='3000/m', block=True, method='POST')
@api_view(['GET'])
def get_usage_summary(request):
    try:
        get_usage_summary = global_voice.get_usage_summary()
        return Response(get_usage_summary)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# @ratelimit(key='user', rate='3000/m', block=True, method='POST')
@api_view(['GET'])
def check_status(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        check_access_status = global_voice.check_access_status()
        current_time = timezone.now()

        if current_time > profile.expiry_date:
            if check_access_status:
                return Response({"status": "Token expired"}, status=status.HTTP_200_OK)
            else:
                return Response({"status": "Usage limit reached"}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "Token valid"}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# @ratelimit(key='user', rate='3000/m', block=True, method='POST')
@api_view(['PATCH'])
def set_expiry_date(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

    expiry_date_str = request.data.get('expiry_date')
    if not expiry_date_str:
        return Response({"error": "expiry_date is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        expiry_date = parse_datetime(expiry_date_str)
        if expiry_date is None:
            raise ValueError("Invalid date format")
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    try:
        profile.expiry_date = expiry_date
        profile.save()
        return Response({"expiry_date": profile.expiry_date}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# @ratelimit(key='user', rate='3000/m', block=True, method='POST')
@api_view(['GET'])
def current_plan(request):
    try:
        current_plan = global_voice.get_voice_list()
        return Response(current_plan)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# @ratelimit(key='user', rate='3000/m', block=True, method='POST')
@api_view(['GET'])
def unique_voices(request):
    try:
        unique_voices = global_voice.get_voice_list()
        for item in unique_voices:
            try:
                voice_entry = Voice.objects.get(voice_id=item['voice_id'])
                item['voice_id'] = voice_entry.voice_id_name
            except ObjectDoesNotExist:
                continue  # Skip if voice entry does not exist

        return Response(unique_voices)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
