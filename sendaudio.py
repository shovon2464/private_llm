import requests
import json

url = "http://127.0.0.1:8000/api/speechtotext/"

import base64
with open("shovon.wav","rb") as audio_file:
    # Read the content of the audio file as binary data
    audio_data = audio_file.read()
    # Encode the binary data using Base64 encoding
    base64_encoded_data = base64.b64encode(audio_data)
    # Decode the binary data to convert it into a string
    base64_string = base64_encoded_data.decode('utf-8')
    payload = {
    "audio_file":base64_string,
    }
    response = requests.post(url, data=payload)
            
    response = response.json()
    print(response)  

    