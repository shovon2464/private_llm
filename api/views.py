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
            prompt = prompt+" "+"What is the "+queries+"?"
            prompt += "Please double check the policy numbers, it is the most important part. The accuracy is very important."
            prompt += "Please ensure there are no dots, spaces, or hyphens in broker id"
            prompt += "The example of date can be 2/23/2024 or 23 Jan 2024. Folow the date format while extracting any date. Please ensure there are no dots, spaces, or hyphens in date. The expiry date or end date is easy to find,it is range as range of 1 year from start date."
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
            prompt = prompt+" "+"Write the summary of the whole paragraph within "+number_of_words+" words"
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
class ClassifyNaturesView(View):
    #using ollma
    def post(self, request):
        try:
            model = MODEL
            prompt = request.POST.get('document')
            natures = "classify the type of the document within these classes NBS- New business, RII - Rewrite, XLN - Cancellation, PCH - Policy Change, ACR / DBR - Billing issue / Final notice, EDT - Endorsement, REI - Reinstate"
            prompt = prompt+" "+natures+" just classify, don't need to write reasoning"
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