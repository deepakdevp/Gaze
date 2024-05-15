import time
import requests  # Used for making HTTP requests
import json
from elevenlabs.client import ElevenLabs

class voice_automaai:

    def __init__(self):
        self.voice_id = None
        self.text = None
        self.AAI_VOICE_API_KEY = "63cb3ad2b580a642e46a1a5ce9ca26ea" # map this
        self.voice_list=[]
        self.voice_id_mapper = {} # sql table for this
        self.voice_id_count = 0 # can be based on sql indexing
        self.client = ElevenLabs(
            api_key=self.AAI_VOICE_API_KEY, # Defaults to ELEVEN_API_KEY
        )
        self.access_status = False # load from the mapping

        self.voice_setting = {"optimize_streaming_latency":"4","output_format":"mp3_44100_128"}
        self.data = {
            "text": "",
            "model_id": "eleven_turbo_v2",
            "output_format": "mp3_44100_128",
            "voice_settings": {
                "stability": 0.8,
                "similarity_boost": 0.8,
                "style": 0.0,
                "use_speaker_boost": False
            }
        }
        self.headers = {"xi-api-key": self.AAI_VOICE_API_KEY}

        self.headers_json = {
            "Accept": "application/json",
            "xi-api-key": self.AAI_VOICE_API_KEY
        }


    def load_meta(self):
        """
        Load all the meta information like voice id mapper, voice_id_count, voice_api_key
        """
        return

    def get_voice_list(self):
        self.voice_list=[]

        url = "https://api.elevenlabs.io/v1/voices"
        # headers = {"xi-api-key": self.AAI_VOICE_API_KEY}
        response = requests.request("GET", url, headers=self.headers)
        voices = json.loads(response.text)
        cloned_voices = [x for x in voices["voices"] if x['category']=='cloned']

        for x in cloned_voices:
            temp_voice = {}
            temp_voice["voice_id"]=x["voice_id"]#removed mapping for now
            temp_voice["name"]=x["name"]
            temp_voice["samples"]=x["samples"][0]["file_name"]
            temp_voice["file_type"]=x["samples"][0]["mime_type"]
            temp_voice["sample_size"]=x["samples"][0]["size_bytes"]
            temp_voice["description"]=x["description"]
            temp_voice["url"]=""
            self.voice_list.append(temp_voice)
            del temp_voice

        return self.voice_list

    def get_usage_summary(self):
        """
        Returns the usage and plan detail
        Check extendability, how it will happen.
        Is it good to store the plan details and billing amount with expiry date in database.
        """


        url = "https://api.elevenlabs.io/v1/user"
        # headers = {
        #     "xi-api-key": self.AAI_VOICE_API_KEY,
        #     "Content-Type": "application/json"
        # }

        response = requests.get(url, headers=self.headers_json)
        if response.status_code == 200:
            user_info = response.json()
            print("User Info:", user_info)
            response = json.loads(response.text)

            character_used = response["subscription"]["character_count"]
            character_limit = response["subscription"]["character_limit"]
            number_of_voices_allowed = response["subscription"]["voice_limit"]
            number_of_voices_add_edit_allowed = response["subscription"]["max_voice_add_edits"]
            number_of_voices_add_edit_used = response["subscription"]["voice_add_edit_counter"]
            billing_period = response["subscription"]["billing_period"]

            usage_summary={
                "character_used":character_used,
                "character_limit":character_limit,
                "number_of_voices_allowed":number_of_voices_allowed,
                "number_of_voices_add_edit_allowed":number_of_voices_add_edit_allowed,
                "number_of_voices_add_edit_used":number_of_voices_add_edit_used,
                "billing_period":billing_period,
                "plan_details":"1,00,000 characters",
                "billing_amount":"44 USD",
                "additional_token_character_pricing":"0.60/1000 Characters"
            }

            return usage_summary
        else:
            print("Failed to retrieve user info.")
        return



    def check_acess_status(self, voice_api_key):
        """
        Returns whether the access has expired or not
        Add expiry date check
        """
        usage_summary = self.get_usage_summary()
        voice_list = get_voice_list()
        if usage_summary["character_used"]<usage_summary["character_limit"] and usage_summary["number_of_voices_add_edit_used"]<usage_summary["number_of_voices_add_edit_allowed"] and len(voice_list)<usage_summary["number_of_voices_allowed"]:
            return True
        else:
            print("Usage summary :", usage_summary)
            return False


    def get_voice_details(self,voice_id):
        """
        Returns voice namd and voice file name uploaded as sample
        """
        try:
            # inv_voice_id_mapper = {v: k for k, v in self.voice_id_mapper.items()}
            # base_voice_id = inv_voice_id_mapper[voice_id]

            url = "https://api.elevenlabs.io/v1/voices/"+voice_id
            querystring = {"with_settings":"true"}
            # headers = {"xi-api-key": self.AAI_VOICE_API_KEY}
            response = requests.request("GET", url, headers=self.headers, params=querystring)
            response = json.loads(response.text)
            voice_name = response["name"]
            voice_file_name = response["samples"][0]["file_name"]
            return voice_name, voice_file_name
        except:
            return "No voice found with voice id:"+voice_id

    def add_voice(self, name, description, file_location):
        """
        Add new sample voice
        """
        voice = self.client.clone(
            name=name,
            description=description,
            files=[file_location],
        )
        print("voice----------------------------"+ voice)
        return {"status": 200,"voice_id":voice.voice_id}



    def delete_voice(self,voice_id):
        """
        Delete the specific voice from the set of samples
        """
        try:
            # inv_voice_id_mapper = {v: k for k, v in self.voice_id_mapper.items()}
            # base_voice_id = inv_voice_id_mapper[voice_id]

            voice_name, voice_file_name = self.get_voice_details(voice_id)

            url = "https://api.elevenlabs.io/v1/voices/"+voice_id
            # headers = {"xi-api-key": self.AAI_VOICE_API_KEY}
            response = requests.request("DELETE", url, headers=self.headers)
            response = json.loads(response.text)
            if response["status"]=="ok":
                return "Deleted "+voice_id+" successfully. Name:"+voice_name+" and sample file name:"+voice_file_name
        except:
            return "Check voice list. Seems not able to find voice id"+voice_id
        return

    def generate_voice(self,voice_id, text, is_file = False):
        # Construct the URL for the Text-to-Speech API request
        tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"

        # Set up headers for the API request, including the API key for authentication
        # headers = {
        #     "Accept": "application/json",
        #     "xi-api-key": AAI_VOICE_API_KEY
        # }

        # Set up the data payload for the API request, including the text and voice settings
        self.data["text"]=text

        # Make the POST request to the TTS API with headers and data, enabling streaming response
        response = requests.post(tts_url, headers=self.headers_json, json=self.data, stream=True, params=self.voice_setting)

        if is_file:
            CHUNK_SIZE = 1024 # Size of chunks to read/write at a time
            if response.ok:
                # Open the output file in write-binary mode
                with open(OUTPUT_PATH, "wb") as f:
                    # Read the response in chunks and write to the file
                    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                        f.write(chunk)
                    # Inform the user of success
                print("Audio stream saved successfully.")
            return
        else:
            return response