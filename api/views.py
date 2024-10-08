from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pgpt_python.client import PrivateGPTApi
from django.core.files.uploadedfile import UploadedFile
from django.http import JsonResponse
import os
from requests.exceptions import Timeout
import subprocess
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import requests
import json
import whisper
from rest_framework.renderers import JSONRenderer
import base64
import random
from .customfunctions import languagetest,translatelanguage,makesummary, risk_analysis_function
from faster_whisper import WhisperModel
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

#MODEL = "llama3:8b-instruct-q8_0"
MODEL = "llama3"
URL = 'http://localhost:11434/api/generate'

class IsActiveView(APIView):
    def get(self, request):
        data = {"message": "I Am Active!"}
        return Response(data, status=status.HTTP_200_OK)

class RetriveInfoView(APIView):
    def post(self, request):
        # Retrieve the document from the request data
        document = request.data.get("document")
        queries = request.data.get("queries")

        # Append retrieval instructions to the document
        document += "What is the "+queries+"?"
        print(document)

        # Initialize the PrivateGPTApi client
        client = PrivateGPTApi(base_url="http://localhost:8001")

        try:
            # Call the contextual completions endpoint with the document as prompt
            prompt_result = client.contextual_completions.prompt_completion(prompt=document)

            # Extract the content of the first choice from the response
            completion_content = prompt_result.choices[0].message.content

            # Prepare response data with the completion content
            response_data = completion_content

            # Return a successful response with the completion content
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle exceptions (e.g., logging, error handling)
            error_message = f"Error processing document: {str(e)}"
            return Response({"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RetriveSummaryView(APIView):
    def post(self, request):
        # Retrieve the document from the request data
        document = request.data.get("document")

        # Append instructions to write a summary
        document += " Write a summary within 15 words"
        print(document)

        # Initialize the PrivateGPTApi client
        client = PrivateGPTApi(base_url="http://localhost:8001")

        try:
            # Call the contextual completions endpoint with the document as prompt
            prompt_result = client.contextual_completions.prompt_completion(prompt=document)

            # Extract the content of the first choice from the response
            summary_content = prompt_result.choices[0].message.content

            # Prepare response data with the summary content
            response_data = summary_content

            # Return a successful response with the summary content
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle exceptions (e.g., logging, error handling)
            error_message = f"Error processing document: {str(e)}"
            return Response({"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        

@method_decorator(csrf_exempt, name='dispatch')
class RetriveInfoLatestView(View):
    #using ollma
    def post(self, request):
        try:
            model = MODEL
            prompt = request.POST.get('document')
            print(request)
            queries = request.POST.get("queries")
            prompt += "\nThe text given above is a scanned document of insurance but the scanning is not perfect, that's why the texts are scattered. I need your intelligence to extract the following keywords "
            prompt ="Please find the following keywords"+queries
            prompt += "Please double check the policy numbers, it is the most important part. The accuracy is very important."
            prompt += "Please ensure there are no dots, spaces, or hyphens in broker id"
            prompt += "The example of date format can be 23 Jan 2024. Folow this date format while extracting any date, if required reformat but be consistent. Please ensure there are no dots, spaces, or hyphens in date. The expiry date or end date is easy to find,it is range as range of 1 year from start date. But there might be explicity written expiry date"
            prompt += "Please be very careful, don't try to be fast, be accurate. You are sending values that are half accurate. If you cannot find the value, just give None in the value of the key."
            prompt += "I only want the JSON and nothing else. An example response can be {\n\"PolicyNumber\": \"4V3130329\",\n\"BrokerID\": \"37763\",\n\"StartDate\": \"01 Mar 2024\",\n\"EndDate\": \"01 Mar 2025\"\n}\n} > ```json" 
            url = URL
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
            }

            response = requests.post(url,json=payload)
            response = response.json()
            response = response.get('response')
            return JsonResponse(response,safe=False)


        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        

@method_decorator(csrf_exempt, name='dispatch')
class RetriveSummaryLatestView(View):
    #using ollma
    def post(self, request):
        try:
            model = MODEL
            prompt = request.POST.get('document')
            number_of_words = request.POST.get("number_of_words")
            prompt = prompt+" "+"Write the summary of the whole paragraph within "+number_of_words+" words. "+"Try to ignore the people names. This is a conversation on insurance so communication or network issues should also be ignored."
            prompt += "return it in a json format < '''json"
            url = URL
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
            }

            response = requests.post(url,json=payload)
            
            response = response.json()
            response = response.get('response')
            return JsonResponse(response,safe=False)


        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class CommandGPTView(View):
    #using ollma
    def post(self, request):
        try:
            model = MODEL
            prompt = request.POST.get('command')
            prompt = prompt
            url = "http://localhost:11434/api/chat"
            
            payload = {
                "model": model,
                "messages": [
                {
                "role": "user",
                "content": prompt
                }
            ],

                "stream": False,
            }

            response = requests.post(url,json=payload)
            
            print(response)
            response = response.json()
            response = response.get('message')
            response = response['content']
            return JsonResponse(response,safe=False)


        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class ClassifyNaturesView2(View):
    #using ollma
    def post(self, request):
        try:
            model = MODEL
            prompt = request.POST.get('document')
            prompt += "This is an insurance document. You need to classify it in various natures classes. "
            prompt += "If the document type is New Business then classify it to NBS. "
            prompt += "If the document type is Cancellation then classify it to XLN. "
            prompt += "If the document changes the policy then classify it to PCH. Don't get confused with NBS. Be careful while deciding. "
            prompt += "If the document type is reminder of outstanding balance and time to pay then classify it to ACR. "
            prompt += "If the document type is Endorsement then classify it to EDT. There is a difference between EDT and NBS, try to differencitate."
            prompt += "If the document type is debit note, telling the transaction then classify it to DBR."
            prompt += "If the document type is Renewal then classify it to RWL. "
            prompt += "If the document type is renewal issued, client not happy and  need to change then classify it to RII. "
            prompt += "If the document type is reinstate after cancellation non pay then classify it to REI. "
            #natures = "classify the type of the document within these classes NBS- New business, RII - Rewrite, XLN - Cancellation, PCH - Policy Change, ACR - Billing issue,  DBR - Final notice, EDT - Endorsement, REI - Reinstate"
            prompt += "just classify whole text in only one type in short form, don't need to write reasoning. Example can be {\n\"type\": \"PCH \"}.Return it in JSON < '''json"
            

            url = URL
            print(url)
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
            }

            response = requests.post(url,json=payload)
            
            response = response.json()
            response = response.get('response')
            return JsonResponse(response,safe=False)


        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        

@method_decorator(csrf_exempt, name='dispatch')
class ClassifyNaturesView(View):
    #using ollma
    def post(self, request):
        try:
            prompt = request.POST.get('document')
            url = "http://192.168.0.61:11000/api/classifynatures/"
            
            payload = {
                "document": prompt,
            }

            response = requests.post(url,data=payload)
            
            response = response.json()
            return JsonResponse(response,safe=False)


        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        
class RecievePDFView(APIView):
    def post(self, request):
        # Check if 'document' key is present in the request data
        if 'document' in request.FILES:
            # Retrieve the uploaded file
            
            os.makedirs('./receivedpdf', exist_ok=True)
            document: UploadedFile = request.FILES['document']

            # Check if the uploaded file is a PDF
            if document.content_type == 'application/pdf':
                # Save the uploaded PDF file to a specific location
                file_path = './receivedpdf/pdf1.pdf'
                with open(file_path, 'wb') as file:
                    for chunk in document.chunks():
                        file.write(chunk)

                # Optionally, you can perform additional processing with the PDF file here

                return Response({"message": "PDF file received and saved successfully"}, status=status.HTTP_200_OK)
            else:
                # If the uploaded file is not a PDF, return an error response
                return Response({"error": "Invalid file format. Expected PDF."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # If 'document' key is missing in the request data, return an error response
            return Response({"error": "No file uploaded. Please provide a PDF file."}, status=status.HTTP_400_BAD_REQUEST)
             
@method_decorator(csrf_exempt, name='dispatch')
class MakeSpeechToTextView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            uniqueid = data.get('uniqueid')
            voice_file_url = data.get('voice_file_url')
            calling_party_ip = data.get('calling_party_ip')
            response = requests.get(voice_file_url, stream=True)
            response.raise_for_status()  
            save_path = f'./{uniqueid}.wav'
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            with open(save_path, 'wb') as file:
                # Download the file in chunks
                for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1 MB chunks
                    if chunk:  # Filter out keep-alive chunks
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        # Print progress (optional)
                        print(f"Downloaded {downloaded_size / (1024 * 1024):.2f} MB of {total_size / (1024 * 1024):.2f} MB", end='\r')

            print(f"\nFile downloaded successfully and saved to {save_path}")

            # Save the uploaded audio file to a specific location
            file_path = f'./{uniqueid}.wav'

            # Load the Whisper model
            model_size = "large-v3"
            try:
                model = WhisperModel(model_size, device="cuda", compute_type="float16")
            except Exception as e:
                return Response({"error": "Failed to load Whisper model.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Transcribe the audio file
            try:
                segments, info = model.transcribe(file_path, beam_size=5)
            except Exception as e:
                return Response({"error": "Failed to transcribe audio.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Combine the transcription
            transcription = ""
            for segment in segments:
                transcription += segment.text

            print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
            print(transcription)
            translation = "Not Translated yet"
            if "en" != info.language or ("en" == info.language and info.language_probability < 0.88):
                translation = translatelanguage(transcription)
            else:
                translation = transcription
            
            # # Handle non-English transcriptions
            # if "en" != info.language or ("en" == info.language and info.language_probability < 0.95):
            #     try:
            #         translation = translatelanguage(transcription)
            #     except Exception as e:
            #         return Response({"error": "Translation failed.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            data = {
                "transcription": translation,
            }
            os.remove(file_path)
            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle unexpected errors
            return Response({"error": "An error occurred during processing.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@method_decorator(csrf_exempt, name='dispatch')
class MakeSpeechToTextView2(APIView):
    def post(self, request):
        try:
            # Generate a random integer and save it to a file
            random_integer = random.randint(1, 10000000)
            with open("./checkprocess.txt", "w") as file:
                file.write(str(random_integer))

            # Ensure that 'audio_file' is in the request.FILES
            if 'audio_file' not in request.FILES:
                return Response({"error": "No audio file provided."}, status=status.HTTP_400_BAD_REQUEST)

            audio: UploadedFile = request.FILES["audio_file"]

            # Validate that the file is an audio file (you can add more checks if necessary)
            if not audio.name.endswith(('.wav', '.mp3', '.m4a')):
                return Response({"error": "Unsupported audio format."}, status=status.HTTP_400_BAD_REQUEST)

            # Save the uploaded audio file to a specific location
            file_path = './output.wav'
            with open(file_path, 'wb') as file:
                for chunk in audio.chunks():
                    file.write(chunk)

            # Load the Whisper model
            model_size = "large-v3"
            try:
                model = WhisperModel(model_size, device="cuda", compute_type="float16")
            except Exception as e:
                return Response({"error": "Failed to load Whisper model.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Transcribe the audio file
            try:
                segments, info = model.transcribe(file_path, beam_size=5)
            except Exception as e:
                return Response({"error": "Failed to transcribe audio.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Combine the transcription
            transcription = ""
            for segment in segments:
                transcription += segment.text

            print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
            print(transcription)
            translation = "Not Translated yet"
            if "en" != info.language or ("en" == info.language and info.language_probability < 0.88):
                translation = translatelanguage(transcription)
            
            # # Handle non-English transcriptions
            # if "en" != info.language or ("en" == info.language and info.language_probability < 0.95):
            #     try:
            #         translation = translatelanguage(transcription)
            #     except Exception as e:
            #         return Response({"error": "Translation failed.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Prepare the response data
            data = {
                "transcription": translation,
            }
            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle unexpected errors
            return Response({"error": "An error occurred during processing.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class RiskAnalysisView(APIView):
    def post(self, request):
        policy = request.POST.get('policy')
        response = risk_analysis_function(policy)                  
        json.dumps(response)
        return Response(response, status=status.HTTP_200_OK)   


    
@method_decorator(csrf_exempt, name='dispatch')
class RedactTextView(View):
    #using ollma
    def post(self, request):
        try:
            model = MODEL
            prompt = request.POST.get('document')
            prompt += "This is a transcript of a conversation between an insurance agent and customer. "
            prompt += "I want you to carefully remove all the personal information. "
            prompt += "The information can be names, SIN number, mobile number, address, policy number, date of birth, etc. "
            prompt += "If the document type is reinstate after cancellation non pay then classify it to REI. "
            #natures = "classify the type of the document within these classes NBS- New business, RII - Rewrite, XLN - Cancellation, PCH - Policy Change, ACR - Billing issue,  DBR - Final notice, EDT - Endorsement, REI - Reinstate"
            prompt += "After removing them send the redacted document in a json format.. Example can be {\n\"readacted\": \"just a random example of redacted text\"}.Return it in JSON < '''json"
            url = URL
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
            }

            response = requests.post(url,json=payload)
            response = response.json()
            response = response.get('response')
            try:
                # Find the start and end indices of the JSON string within the triple backticks
                start_index = response.find('{') 
                end_index = response.rfind('}')+1

                # Extract the JSON string
                json_string = response[start_index:end_index]

                # Parse the JSON string
                response = json.loads(json_string)
                

            except Exception as e:
                print("No valid JSON data found:", e)
            
            
            
            return JsonResponse(response,safe=False)


        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


        