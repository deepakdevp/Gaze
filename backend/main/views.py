
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .voices import voice_automaai
from .models import Voice
global_voice = voice_automaai()

@api_view(['POST'])
def register_voice(request):
    name = request.data.get('name', None)
    description = request.data.get('description', None)
    file_url = '/Users/deepak.panwar/personel/Django-React-jwt-authentication/backend/main/audio.mp3'
    voice_id = global_voice.add_voice(name, description,file_url )
    if voice_id.status == 200:
        existing_voice_count = Voice.objects.filter(profile=request.user.profile).count()

        # Generate the voice_id_name based on the count
        voice_id_name = f"AAI_{existing_voice_count + 1}"
        new_voice = Voice(
            voice_id=voice_id.voice_id,
            voice_id_name=voice_id_name,
            file_url=file_url
        )
        new_voice.profile = request.user.profile
        new_voice.save()
        return Response(voice_id_name)
    else:
      return Response({"message": voice_id.message}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def delete_voice(request):
    voice_id_name = request.data.get("voice_id_name")
    voice_entry = Voice.objects.get(voice_id_name=voice_id_name)
    voice_id = voice_entry.voice_id
    voice_deleted_response = global_voice.delete_voice(voice_id)
    return Response(voice_deleted_response)

@api_view(['POST'])
def generate_voice(request):
    text = request.data.get("text")
    voice_id_name = request.data.get("voice_id_name")
    voice_entry = Voice.objects.get(voice_id_name=voice_id_name)
    voice_id = voice_entry.voice_id
    generated_voice_response = global_voice.generate_voice(voice_id,text)
    return Response(generated_voice_response)

@api_view(['GET'])
def get_usage_summary(request):
    get_usage_summary = global_voice.get_usage_summary()
    return Response(get_usage_summary)

@api_view(['GET'])
def current_plan(request):
    current_plan = global_voice.get_voice_list()
    return Response(current_plan)

@api_view(['GET'])
def unique_voices(request):
    unique_voices = global_voice.get_voice_list()

    return Response(unique_voices)



