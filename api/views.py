from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pgpt_python.client import PrivateGPTApi
from django.core.files.uploadedfile import UploadedFile
from django.http import JsonResponse
import os


class IsActiveView(APIView):
    def get(self, request):
        data = {"message": "I Am Active!"}
        return Response(data, status=status.HTTP_200_OK)

class RetriveInfoView(APIView):
    def post(self, reqeust):
       document = self.request.data.get("document") 
       print(document)
       response_data = {"message": "The document is received"}
       client = PrivateGPTApi(base_url="http://localhost:8001")
       prompt_result = client.contextual_completions.prompt_completion(prompt=document)
       return Response(prompt_result.choices[0].message.content, status=status.HTTP_200_OK)

class RetriveSummaryView(APIView):
    def post(self, reqeust):
       document = self.request.data.get("document") 
       document += "Write a summary within two sentences"
       response_data = {"message": "The document is received"}
       client = PrivateGPTApi(base_url="http://localhost:8001")
       prompt_result = client.contextual_completions.prompt_completion(prompt=document)
       return Response(prompt_result.choices[0].message.content, status=status.HTTP_200_OK)





  
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