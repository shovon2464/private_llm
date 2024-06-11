import requests
MODEL = "llama3:8b-instruct-q8_0"
#MODEL = "llama3:8b-instruct-q6_k"
URL = 'http://localhost:11434/api/generate'
def languagetest(transcription):
    prompt = transcription[0:200] + "What is the language of it. For example if the language is english please return {\n\"language\": \"eng\"}.Return it in JSON < '''json"
    url = URL
    payload = {
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
            }
    response = requests.post(url,json=payload)
    response = response.json()
    response = response.get('response')
    start_index = response.find('{') 
    end_index = response.rfind('}')+1

    # Extract the JSON string
    response = response[start_index:end_index]
    print(response)
    return response

def translatelanguage(transcription):
    prompt = transcription + "\nTranslate the above sentences in English. If the whole language is English then do not translate. For example return {\n\"translation\": I emailed you back a couple days ago and I was waiting for a response. And you got moved on a dress down? Let me check again. Also, I can't really hear you like well. It's so muffled. Oh, okay. Hang on a moment. Hey, is that better? Yeah, much better. Alright, crappy Bluetooth. \"\"}.Return it in JSON < '''json"
    url = URL
    payload = {
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
            }
    response = requests.post(url,json=payload)
    response = response.json()
    response = response.get('response')
    start_index = response.find('{') 
    end_index = response.rfind('}')+1

    # Extract the JSON string
    response = response[start_index:end_index]

    return response

def makesummary(trascription):
    prompt = "You are an assistant who would make a summary of the sentence in 15 words. This is a phone transcription so there might be conversation about other things, but I want summary about the most important parts of the conversation. Then things that affects the business."
    prompt += "Return the summary in json with a key summary. Here is the transcription: "
    prompt += trascription + "<<<json"
    model = "llama3:70b"
    url = URL
    print("I am before sending it to 70b")
    payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
            }
    response = requests.post(url,json=payload)
    response = response.json()
    response = response.get('response')
    print(response)
    start_index = response.find('{') 
    end_index = response.rfind('}')+1
    # Extract the JSON string
    response = response[start_index:end_index]

    return response
    