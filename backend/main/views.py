from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from base.models import Profile
from django.utils.dateparse import parse_datetime
from .voices import voice_automaai
from .models import Voice
from rest_framework import status
from django.utils import timezone
import uuid

global_voice = voice_automaai()

@api_view(['POST'])
def register_voice(request):
    name = request.data.get('name', None)
    file_url = request.data.get('file_url', None)

    # Check if required fields are provided
    if not name or not file_url:
        return Response({"message": "Both 'name' and 'file_url' are required fields."}, status=status.HTTP_400_BAD_REQUEST)

    description = request.data.get('description', None)
    voice_id = global_voice.add_voice(name, description, file_url)

    if voice_id["status"] == 200:
        unique_uuid = str(uuid.uuid4())[:5]

        # Generate the voice_id_name based on the count
        voice_id_name = f"AAI_{unique_uuid}"
        new_voice = Voice(
            voice_id=voice_id["voice_id"],
            voice_id_name=voice_id_name,
            file_url=file_url
        )
        new_voice.profile = request.user.profile
        new_voice.save()
        return Response(voice_id_name)
    else:
        return Response({"message": voice_id["message"]}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def delete_voice(request):
    voice_id_name = request.data.get("voice_id_name")
    voice_entry = Voice.objects.get(voice_id_name=voice_id_name)
    voice_id = voice_entry.voice_id
    voice_deleted_response = global_voice.delete_voice(voice_id)
    if voice_deleted_response["status"] == 200:
      voice_entry.delete()
      return Response(voice_id_name + voice_deleted_response["message"])
    else:
      return Response(voice_deleted_response["message"])

@api_view(['POST'])
def generate_voice(request):
    text = request.data.get("text")
    voice_id_name = request.data.get("voice_id_name")
    voice_entry = Voice.objects.get(voice_id_name=voice_id_name)
    voice_id = voice_entry.voice_id
    voice_name = voice_entry.voice_id_name
    generated_voice_response = global_voice.generate_voice(voice_id,voice_name,text,True)
    return Response(generated_voice_response)

@api_view(['GET'])
def get_usage_summary(request):
    get_usage_summary = global_voice.get_usage_summary()
    return Response(get_usage_summary)

@api_view(['GET'])
def check_status(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
    check_acess_status = global_voice.check_acess_status()
    current_time = timezone.now()
    if current_time > profile.expiry_date:
        if check_acess_status:
            return Response({"status": "Token expired"}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "Usage limit reached"}, status=status.HTTP_200_OK)
    else:
        return Response({"status": "Token valid"}, status=status.HTTP_200_OK)

    return Response(get_usage_summary)


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

    profile.expiry_date = expiry_date
    profile.save()

    return Response({"expiry_date": profile.expiry_date}, status=status.HTTP_200_OK)



@api_view(['GET'])
def current_plan(request):
    current_plan = global_voice.get_voice_list()
    return Response(current_plan)

@api_view(['GET'])
def unique_voices(request):
    unique_voices = global_voice.get_voice_list()
    for item in unique_voices:
      voice_entry = Voice.objects.get(voice_id=item['voice_id'])
      item['voice_id'] = voice_entry.voice_id_name
    return Response(unique_voices)



